from typing import Literal
from tgapi import Any, ParsedJson


class Callback(ParsedJson):
    # https://dev.vk.com/ru/api/community-events/json-schema
    type: str = ""
    object: Any = None
    group_id: int = 0
    secret: str = ""

    def _parse_field(self, key: str, v: Any, json: dict[str, Any]):
        if key != "object" or "type" not in json:
            return None
        type = json["type"]
        obj = None

        if type == "wall_post_new":
            obj = Post(v)

        return "object", obj


class Post(ParsedJson):
    # https://dev.vk.com/ru/reference/objects/post
    id: int = 0
    owner_id: int = 0
    from_id: int = 0
    created_by: int = 0
    date: int = 0
    text: str = ""
    reply_owner_id: int = 0
    reply_post_id: int = 0
    friends_only: bool = False
    # comments: Any = None
    # copyright: Any = None
    # likes: Any = None
    # reposts: Any = None
    # views: Any = None
    post_type: Literal["post", "copy", "reply", "postpone", "suggest"] = ""
    # post_source: Any = None
    # attachments: list[Any] = []
    # geo: Any = None
    signer_id: int = 0
    # copy_history: list[Any] = []
    can_pin: bool = False
    can_delete: bool = False
    can_edit: bool = False
    is_pinned: bool = False
    marked_as_ads: bool = False
    is_favorite: bool = False
    # donut: Any = None
    postponed_id: int = 0

    def _parse_field(self, key: str, v: Any, json):
        if key in [
            "friends_only",
            "can_pin",
            "can_delete",
            "can_edit",
            "is_pinned",
            "marked_as_ads",
        ]:
            return key, v == 1
