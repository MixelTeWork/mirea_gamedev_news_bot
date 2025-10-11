import math
import re

import bafser_tgapi as tgapi
from bafser import listfind, response_msg
from flask import Blueprint, g

import vkapi
from data.broadcast import Broadcast

blueprint = Blueprint("vk_callback", __name__)
ME = tgapi.MessageEntity


@blueprint.post("/api/vk_callback")
def vk_callback():
    data, is_json = g.json
    if not is_json:
        return response_msg("body is not json", 415)

    callback = vkapi.Callback.new(data)
    if (not vkapi.check_callback_secret(callback.secret)):
        return response_msg("wrong secret", 403)

    if callback.type == "confirmation":
        return vkapi.get_confirmation_code()

    if isinstance(callback.object, vkapi.Post):
        post = callback.object
        if post.post_type not in ("post", "copy", "reply"):
            return "ok"
        tgapi.call_async(on_new_post, post)

    return "ok"


re_link = re.compile("\\[(#alias\\|)?([-a-zA-Z0-9$_.+!*'(),\\/&?=:%]+)\\|(.+?)\\]")
re_url_full = re.compile("https?:\\/\\/(?:www\\.)?([-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*))")
re_url = re.compile("(https?:\\/\\/)?(?:www\\.)?([-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*))")
video_text = ["первое", "второе", "третье", "четвёртое", "пятое"]


def on_new_post(post: vkapi.Post):
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
            img = (listfind(attachment.sizes, lambda v: v.type == "base") or
                   listfind(attachment.sizes, lambda v: v.type == "z") or
                   attachment.sizes[-1])
            if img:
                attachments.append(tgapi.InputMediaPhoto(media=img.url))
        elif isinstance(attachment, vkapi.Video):
            image = None
            for img in attachment.image:
                if not image or image.width < img.width:
                    image = img
            url = f"https://vk.com/video{attachment.owner_id}_{attachment.id}"
            video.append(url)
            if image:
                attachments.append(tgapi.InputMediaPhoto(media=image.url))

    msg = tgapi.build_msg()

    if len(video) > 0:
        if len(video) == 1:
            msg.text_link("🎞 Видео", video[0])
        else:
            msg.text("🎞 Видео: ")
            for i, url in enumerate(video):
                t = video_text[i] if i < len(video_text) else f"видео#{i + 1}"
                if i > 0:
                    msg.text(", ")
                msg.text_link(t, video[i])
        msg.text("\n\n")

    for link in links:
        caption = link.caption
        if caption == "":
            caption = link.url
            caption = caption.removeprefix("https://")
            caption = caption.removeprefix("http://")
            caption = caption.removeprefix("www.")
            if len(caption) > 16:
                caption = caption[:16] + "..."
        q = tgapi.build_msg()
        q.text_link("📎 " + caption, link.url)
        q.text(f"\n{link.title}")
        msg.blockquote(q)
        msg.text("\n\n")

    for doc in docs:
        msg.text("📄 Файл: ")
        q.text_link(doc.title, doc.url)
        msg.text("\n\n")

    for poll in polls:
        # q = ME.len(text)
        q = tgapi.build_msg()
        q.text("📊 Опрос: ")
        q.bold(poll.question).text("\n")
        for i, ans in enumerate(poll.answers):
            dot = "🔸" if i % 2 == 0 else "🔹"
            q.text(dot + " " + ans.text + "\n")
        msg.blockquote(q)
        msg.text("\n")

    text, entities = msg.build()
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
        m_url = re_url_full.search(text, search_start)
        if not m_link and not m_url:
            break
        if m_link and (not m_url or m_link.start() < m_url.start()):
            url = m_link.group(2)
            p1 = text[:m_link.start()]
            p2 = m_link.group(3)
            p3 = text[m_link.end():]
            if m_link.group(1):
                url, p2 = p2, url
            text = p1 + p2 + p3
            search_start = len(p1 + p2)
            if not re_url.match(url):
                url = "https://vk.com/" + url
            if re_url.match(url):
                entities.append(ME.text_link(ME.len(p1), ME.len(p2), url))
        elif m_url:
            url = m_url.group(0)
            url_text = m_url.group(1)
            p1 = text[:m_url.start()]
            p2 = url_text if len(url_text) <= 16 else url_text[:16] + "..."
            p3 = text[m_url.end():]
            text = p1 + p2 + p3
            search_start = len(p1 + p2)
            entities.append(ME.text_link(ME.len(p1), ME.len(p2), url))

    if len(attachments) == 0:
        sendMessage(text, entities)
    else:
        long = len(text) >= 1024
        if not long:
            attachments[0].set_caption(text, caption_entities=entities)
        Broadcast.sendMediaGroup(attachments)
        if long:
            sendMessage(text, entities)


def sendMessage(text: str, entities: list[ME]):
    tlen = len(text)
    MAXL = 4096
    if tlen < MAXL:
        Broadcast.sendMessage(text, entities=entities, link_preview_options=tgapi.LinkPreviewOptions.disable())
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
        Broadcast.sendMessage(t, entities=ent, link_preview_options=tgapi.LinkPreviewOptions.disable())
