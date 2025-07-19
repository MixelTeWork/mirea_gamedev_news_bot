from __future__ import annotations

from sqlalchemy import Column, Integer, BigInteger

from bafser import SqlAlchemyBase, SingletonMixin, Log
from data._tables import Tables
from data.user import User


class Config(SqlAlchemyBase, SingletonMixin):
    __tablename__ = Tables.Config
