from io import BytesIO

import bafser_tgapi as tgapi
import qrcode
from bafser import JsonObj
from flask import Blueprint, g, render_template, request, send_file

from data.quest import Quest
from data.user import User
from data.user_quest import UserQuest
from utils import parse_int

bp = Blueprint("quest", __name__)


@bp.route("/scanner")
def scanner():
    uid = request.args.get("uid")
    id = parse_int(request.args.get("id") or "")
    if not uid or not id:
        return "Missing parameters", 400
    user = User.get_by_big_id2(uid)
    if not user:
        return "User not found", 400
    quest = Quest.get2(id)
    if not quest:
        return "Quest not found", 400

    ok, r = tgapi.getChatMember(quest.chat_id, user.id_tg)
    if not ok or r.status not in ("creator", "administrator", "member"):
        return "User is not a member of the quest room", 403

    return render_template("scanner.html", user=user, quest=quest)


class ScannerData(JsonObj):
    data: str
    qid: str
    uid: str


@bp.post("/api/scanner")
def api_scanner():
    data = ScannerData.get_from_req()
    user = User.get_by_big_id2(data.data)
    if not user:
        return "User not found", 400
    actor = User.get_by_big_id2(data.uid)
    if not actor:
        return "Actor not found", 400
    quest = Quest.get2(parse_int(data.qid, 0))
    if not quest:
        return "Quest not found", 400
    ok, r = tgapi.getChatMember(quest.chat_id, actor.id_tg)
    if not ok or r.status not in ("creator", "administrator", "member"):
        return "Actor is not a member of the quest room", 403
    _, added = UserQuest.add(user.id, quest.id)
    if not added:
        return f"Квест уже был засчитан ранее для {user.get_tagname()}"
    txt = f"🎉 Вы выполнили квест {quest.name}!\n"
    xp = UserQuest.get_user_points(user)
    txt += f"✨ XP +{quest.reward}\n  {xp - quest.reward} -> {xp}"
    tgapi.call_async(tgapi.sendMessage, user.id_tg, txt)
    return f"Квест засчитан для {user.get_tagname()}"


@bp.route("/qr")
def qr():
    data = request.args.get("data")
    if not data:
        return "Missing parameters", 400
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    byte_stream = BytesIO()
    img.save(byte_stream, "PNG")
    byte_stream.seek(0)
    return send_file(byte_stream, mimetype="image/png")
