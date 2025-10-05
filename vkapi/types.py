from datetime import datetime
from typing import Any, Literal, Union, override

from bafser import JsonObj, JsonOpt, Undefined


class Callback(JsonObj):
    # https://dev.vk.com/ru/api/community-events/json-schema
    type: str = ""
    object: Any = None
    group_id: int = 0
    secret: str = ""

    @override
    def _parse(self, key: str, v: Any, json: dict[str, Any]):
        if key != "object" or "type" not in json:
            return None
        type = json["type"]
        obj = None

        if type == "wall_post_new":
            obj = Post.new(v)

        return key, obj


type AttachmentType = Literal["photo", "posted_photo", "video", "audio", "doc", "graffiti", "link", "note", "app",
                              "poll", "page", "album", "photos_list", "market", "market_album", "sticker", "pretty_cards", "event"]


class Photo(JsonObj):
    # https://dev.vk.com/ru/reference/objects/photo
    class Size(JsonObj):
        # https://dev.vk.com/ru/reference/objects/photo-sizes
        type: Literal["s", "m", "x", "o", "p", "q", "r", "y", "z", "w", ""] = ""
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


class Video(JsonObj):
    # https://dev.vk.com/ru/reference/objects/video
    class Image(JsonObj):
        height: int = 0
        width: int = 0
        url: str = ""
        with_padding: bool = False

        @override
        def _parse(self, key: str, v: Any, json: dict[str, Any]):
            if key == "with_padding":
                return key, v == 1

    id: int = 0
    owner_id: int = 0
    title: str = ""
    description: str = ""
    duration: int = 0
    image: list[Image] = []
    first_frame: list[Image] = []
    date: int = 0
    adding_date: int = 0
    views: int = 0
    local_views: int = 0
    comments: int = 0
    player: str = ""
    platform: str = ""
    can_add: bool = False
    is_private: bool = False
    access_key: str = ""
    processing: bool = False
    is_favorite: bool = False
    can_comment: bool = False
    can_edit: bool = False
    can_like: bool = False
    can_repost: bool = False
    can_subscribe: bool = False
    can_add_to_faves: bool = False
    can_attach_link: bool = False
    width: int = 0
    height: int = 0
    user_id: int = 0
    converting: bool = False
    added: bool = False
    is_subscribed: bool = False
    repeat: bool = False
    type: Literal["video", "music_video", "movie", "story", ""] = ""
    balance: int = 0
    live: bool = False
    live_start_time: int = 0
    live_status: Literal["waiting", "started", "finished", "failed", "upcoming", ""] = ""
    upcoming: bool = False
    spectators: int = 0
    # likes: Any = None
    # reposts: Any = None

    @override
    def _parse(self, key: str, v: Any, json: dict[str, Any]):
        if key in [
            "can_add",
            "is_private",
            "processing",
            "can_comment",
            "can_edit",
            "can_like",
            "can_repost",
            "can_subscribe",
            "can_add_to_faves",
            "can_attach_link",
            "converting",
            "added",
            "is_subscribed",
            "repeat",
            "live",
            "upcoming",
        ]:
            return key, v == 1


class Link(JsonObj):
    # https://dev.vk.com/ru/reference/objects/link
    url: str = ""
    title: str = ""
    caption: str = ""
    description: str = ""
    photo: JsonOpt[Photo] = Undefined
    # product: Any = None
    # button: Any = None
    preview_page: str = ""
    preview_url: str = ""


class Doc(JsonObj):
    # https://dev.vk.com/ru/reference/objects/doc
    id: int = 0
    owner_id: int = 0
    title: str = ""
    size: int = 0
    ext: str = ""
    url: str = ""
    date: int = 0
    type: int = 0
    # preview: Any = None


class Poll(JsonObj):
    # https://dev.vk.com/ru/reference/objects/poll
    class Answer(JsonObj):
        id: int = 0
        text: str = ""
        votes: int = 0
        rate: int = 0

    id: int = 0
    owner_id: int = 0
    created: int = 0
    question: str = ""
    votes: int = 0
    answers: list[Answer] = []
    anonymous: bool = False
    multiple: bool = False
    answer_ids: list[int] = []
    end_date: int = 0
    closed: bool = False
    is_board: bool = False
    can_edit: bool = False
    can_vote: bool = False
    can_report: bool = False
    can_share: bool = False
    author_id: int = 0
    photo: JsonOpt[Photo] = Undefined
    # background: Any = None
    friends: list[int] = []


class Post(JsonObj):
    __datetime_parser__ = datetime.fromtimestamp
    # https://dev.vk.com/ru/reference/objects/post
    id: int = 0
    owner_id: int = 0
    from_id: int = 0
    created_by: int = 0
    date: datetime = datetime.now()
    text: str = ""
    reply_owner_id: int = 0
    reply_post_id: int = 0
    friends_only: bool = False
    # comments: Any = None
    # copyright: Any = None
    # likes: Any = None
    # reposts: Any = None
    # views: Any = None
    post_type: Literal["post", "copy", "reply", "postpone", "suggest", ""] = ""
    # post_source: Any = None
    attachments: list[Union[Photo, Video, Link, Doc, Poll]] = []
    # geo: Any = None
    signer_id: int = 0
    copy_history: list["Post"] = []
    can_pin: bool = False
    can_delete: bool = False
    can_edit: bool = False
    is_pinned: bool = False
    marked_as_ads: bool = False
    is_favorite: bool = False
    # donut: Any = None
    postponed_id: int = 0

    @override
    def _parse(self, key: str, v: Any, json: dict[str, Any]):
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
                    attachments.append(Photo.new(data))
                elif atype == "video":
                    attachments.append(Video.new(data))
                elif atype == "link":
                    attachments.append(Link.new(data))
                elif atype == "doc":
                    attachments.append(Doc.new(data))
                elif atype == "poll":
                    attachments.append(Poll.new(data))
            return key, attachments
