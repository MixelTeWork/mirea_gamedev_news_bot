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


AttachmentType = Literal["photo", "posted_photo", "video", "audio", "doc", "graffiti", "link", "note", "app",
                         "poll", "page", "album", "photos_list", "market", "market_album", "sticker", "pretty_cards", "event"]


class Photo(ParsedJson):
    # https://dev.vk.com/ru/reference/objects/photo
    class Size(ParsedJson):
        # https://dev.vk.com/ru/reference/objects/photo-sizes
        type: Literal["s", "m", "x", "o", "p", "q", "r", "y", "z", "w"] = ""
        url: str = ""
        width: int = 0
        height: int = 0

    id: int = 0
    album_id: int = 0
    owner_id: int = 0
    user_id: int = 0
    text: str = ""
    date: int = 0
    thumb_hash: str = ""
    has_tags: bool = False
    sizes: list[Size] = []
    width: int = 0
    height: int = 0

    def _parse_field(self, key: str, v: Any, json):
        if key == "sizes":
            return key, [Photo.Size(el) for el in v]


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
    attachments: list[Any] = []
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

        if key == "attachments":
            attachments = []
            for attachment in v:
                atype: AttachmentType = attachment["type"]
                data = attachment[atype]
                if atype == "photo":
                    attachments.append(Photo(data))
            return key, attachments
