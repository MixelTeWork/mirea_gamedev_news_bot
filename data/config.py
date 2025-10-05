from __future__ import annotations

from bafser import Log, SingletonMixin, SqlAlchemyBase
from sqlalchemy import BigInteger, Column, Integer

from data._tables import Tables
from data.user import User


class Config(SqlAlchemyBase, SingletonMixin):
    __tablename__ = Tables.Config
