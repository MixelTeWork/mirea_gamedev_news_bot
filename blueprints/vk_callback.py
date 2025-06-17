import re

from flask import Blueprint, g
from sqlalchemy.orm import Session
from bafser import response_msg, use_db_session

from data.config import Config
import tgapi
from utils import find
import vkapi

ME = tgapi.MessageEntity

blueprint = Blueprint("vk_callback", __name__)


@blueprint.post("/api/vk_callback")
def vk_callback():
    data, is_json = g.json
    if not is_json:
        return response_msg("body is not json", 415)

    callback = vkapi.Callback(data)
    if (not vkapi.check_callback_secret(callback.secret)):
        return response_msg("wrong secret", 403)

    if callback.type == "confirmation":
        return vkapi.get_confirmation_code()

    if isinstance(callback.object, vkapi.Post):
        on_new_post(callback.object)

    return "ok"


re_link = re.compile("\\[(.*)\\|(.*)\\]")


@use_db_session()
def on_new_post(post: vkapi.Post, db_sess: Session):
    config = Config.get(db_sess)
    if config.chat_id is None or config.chat_thread_id is None:
        return

    attachments: list[tgapi.InputMedia] = []
    for attachment in post.attachments:
        if isinstance(attachment, vkapi.Photo):
            img = (find(attachment.sizes, lambda v: v.type == "base") or
                   find(attachment.sizes, lambda v: v.type == "z") or
                   attachment.sizes[-1])
            attachments.append(tgapi.InputMediaPhoto(img.url))

    text = post.text
    entities = []

    search_start = 0
    while True:
        m = re_link.search(text, search_start)
        if not m:
            break
        p1 = text[:m.start()]
        p2 = m.group(2)
        p3 = text[m.end():]
        text = p1 + p2 + p3
        search_start = len(p1 + p2)
        entities.append(ME.text_link(ME.len(p1), ME.len(p2), m.group(1)))

    if len(attachments) == 0:
        tgapi.sendMessage(config.chat_id, text, config.chat_thread_id, entities=entities)
    else:
        attachments[0].set_caption(text, caption_entities=entities)
        tgapi.sendMediaGroup(config.chat_id, config.chat_thread_id, attachments)
