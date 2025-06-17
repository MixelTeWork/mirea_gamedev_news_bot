from flask import Blueprint, g
from sqlalchemy.orm import Session
from bafser import response_msg, use_db_session

from data.config import Config
import tgapi
import vkapi


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


@use_db_session()
def on_new_post(post: vkapi.Post, db_sess: Session):
    config = Config.get(db_sess)
    if config.chat_id is None or config.chat_thread_id is None:
        return

    tgapi.sendMessage(config.chat_id, post.text, config.chat_thread_id)
