import bafser_tgapi as tgapi
from flask import Blueprint, g, render_template, request

from bot.bot import Bot
from data.quest import Quest
from data.user import User
from utils import parse_int

bp = Blueprint("scanner", __name__)


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

    ok, r = tgapi.getChatMember(Bot._quest_room_id, user.id_tg)
    if not ok or r.status not in ("creator", "administrator", "member"):
        return "User is not a member of the quest room", 403

    return render_template("scanner.html", user=user, quest=quest)
