from typing import Any, override

from bafser import UserKwargs
from bafser_tgapi import TgUserBase
from sqlalchemy.orm import Session

from data import Roles
from utils import BigIdMixin


class User(TgUserBase, BigIdMixin):
    _default_role = Roles.user

    @classmethod
    @override
    def _new(cls, db_sess: Session, user_kwargs: UserKwargs, *,
             id_tg: int, is_bot: bool, first_name: str, last_name: str, username: str, language_code: str, **kwargs: Any):
        u = cls(**user_kwargs,
                id_tg=id_tg, is_bot=is_bot, first_name=first_name, last_name=last_name, username=username, language_code=language_code)
        u.set_unique_big_id(db_sess)
        return u
