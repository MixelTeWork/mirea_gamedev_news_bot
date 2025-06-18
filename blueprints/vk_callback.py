import math
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
re_url = re.compile("https?:\\/\\/(?:www\\.)?([-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*))")
video_text = ["первое", "второе", "третье", "четвёртое", "пятое"]


@use_db_session()
def on_new_post(post: vkapi.Post, db_sess: Session):
    config = Config.get(db_sess)
    if config.chat_id is None or config.chat_thread_id is None:
        return

    repost = post.copy_history[0] if len(post.copy_history) > 0 else None
    repost_attachments = repost.attachments if repost else []

    attachments: list[tgapi.InputMedia] = []
    video: list[str] = []
    links: list[vkapi.Link] = []
    docs: list[vkapi.Doc] = []
    polls: list[vkapi.Poll] = []
    for attachment in post.attachments + repost_attachments:
        if isinstance(attachment, vkapi.Link):
            links.append(attachment)
            attachment = attachment.photo
        elif isinstance(attachment, vkapi.Poll):
            polls.append(attachment)
            attachment = attachment.photo
        elif isinstance(attachment, vkapi.Doc):
            docs.append(attachment)
        if isinstance(attachment, vkapi.Photo):
            img = (find(attachment.sizes, lambda v: v.type == "base") or
                   find(attachment.sizes, lambda v: v.type == "z") or
                   attachment.sizes[-1])
            if img:
                attachments.append(tgapi.InputMediaPhoto(img.url))
        elif isinstance(attachment, vkapi.Video):
            image = None
            for img in attachment.image:
                if not image or image.width < img.width:
                    image = img
            url = f"https://vk.com/video{attachment.owner_id}_{attachment.id}"
            video.append(url)
            if image:
                attachments.append(tgapi.InputMediaPhoto(image.url))

    text = ""
    entities = []

    if len(video) > 0:
        t = "🎞 Видео"
        if len(video) == 1:
            entities.append(ME.text_link(ME.len(text), ME.len(t), video[0]))
            text += t
        else:
            text += t + ": "
            for i, url in enumerate(video):
                if i < len(video_text):
                    t = video_text[i]
                else:
                    t = f"видео#{i + 1}"
                if i > 0:
                    text += ", "
                entities.append(ME.text_link(ME.len(text), ME.len(t), video[i]))
                text += t
        text += "\n\n"

    for link in links:
        q = ME.len(text)
        caption = link.caption
        if caption == "":
            caption = link.url
            caption = caption.removeprefix("https://")
            caption = caption.removeprefix("http://")
            caption = caption.removeprefix("www.")
            if len(caption) > 16:
                caption = caption[:16] + "..."
        t = "📎 " + caption
        entities.append(ME.text_link(ME.len(text), ME.len(t), link.url))
        text += t
        text += f"\n{link.title}"
        entities.append(ME.blockquote(q, ME.len(text) - q))
        text += "\n\n"

    for doc in docs:
        text += "📄 Файл: "
        t = doc.title
        entities.append(ME.text_link(ME.len(text), ME.len(t), doc.url))
        text += t + "\n\n"

    for poll in polls:
        q = ME.len(text)
        text += "📊 Опрос: "
        t = poll.question
        entities.append(ME.bold(ME.len(text), ME.len(t)))
        text += t + "\n"
        for i, ans in enumerate(poll.answers):
            dot = "🔸" if i % 2 == 0 else "🔹"
            text += dot + " " + ans.text + "\n"
        entities.append(ME.blockquote(q, ME.len(text) - q))
        text += "\n"

    search_start = len(text)
    text += post.text

    if repost:
        text = text.rstrip()
        if len(text) > 0:
            text += "\n\n"
        text += "↪\n"
        text += repost.text

    text = text.rstrip()
    text += f"\n\n🖋 {post.date:%d %b}    [https://vk.com/wall{post.owner_id}_{post.id}|Оригинал]"

    while True:
        m_link = re_link.search(text, search_start)
        m_url = re_url.search(text, search_start)
        if not m_link and not m_url:
            break
        if m_link and (not m_url or m_link.start() < m_url.start()):
            p1 = text[:m_link.start()]
            p2 = m_link.group(2)
            p3 = text[m_link.end():]
            text = p1 + p2 + p3
            search_start = len(p1 + p2)
            entities.append(ME.text_link(ME.len(p1), ME.len(p2), m_link.group(1)))
        else:
            url = m_url.group(0)
            url_text = m_url.group(1)
            p1 = text[:m_url.start()]
            p2 = url_text if len(url_text) <= 16 else url_text[:16] + "..."
            p3 = text[m_url.end():]
            text = p1 + p2 + p3
            search_start = len(p1 + p2)
            entities.append(ME.text_link(ME.len(p1), ME.len(p2), url))

    if len(attachments) == 0:
        sendMessage(config, text, entities)
    else:
        long = len(text) >= 1024
        if not long:
            attachments[0].set_caption(text, caption_entities=entities)
        tgapi.sendMediaGroup(config.chat_id, config.chat_thread_id, attachments)
        if long:
            sendMessage(config, text, entities)


def sendMessage(config: Config, text: str, entities: list[ME] = []):
    tlen = len(text)
    MAXL = 4096
    if tlen < MAXL:
        tgapi.sendMessage(config.chat_id, text, config.chat_thread_id, entities=entities,
                          link_preview_options=tgapi.LinkPreviewOptions.disable())
        return

    part_start = 0
    part_startL = 0
    part_end = math.ceil(tlen / math.ceil(tlen / MAXL))
    while part_start < tlen:
        t = text[part_start:part_end]
        part_endL = part_startL + ME.len(t)
        ent = []
        len_changed = False
        for e in entities:
            if e.offset >= part_startL and e.offset < part_endL:
                if e.offset + e.length > part_endL:
                    len_changed = True
                    while part_endL > e.offset:
                        part_end -= 1
                        t = text[part_start:part_end]
                        part_endL = part_startL + ME.len(t)
                    break
                e = e.copy()
                e.offset -= part_startL
                ent.append(e)
        if len_changed:
            continue
        part_start = part_end
        part_startL = part_endL
        tlen_left = tlen - part_start
        partLen = 0 if tlen_left == 0 else math.ceil(tlen_left / math.ceil(tlen_left / MAXL))
        part_end = min(part_start + partLen, tlen)
        tgapi.sendMessage(config.chat_id, t, config.chat_thread_id, entities=ent,
                          link_preview_options=tgapi.LinkPreviewOptions.disable())
