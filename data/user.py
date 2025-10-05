from bafser_tgapi import TgUserBase

from data import Roles


class User(TgUserBase):
    _default_role = Roles.user
