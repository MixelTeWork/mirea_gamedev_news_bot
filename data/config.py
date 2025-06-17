from __future__ import annotations

from sqlalchemy import Column, Integer, BigInteger

from bafser import SqlAlchemyBase, SingletonMixin, Log
from data._tables import Tables
from data.user import User


class Config(SqlAlchemyBase, SingletonMixin):
    __tablename__ = Tables.Config

    chat_id = Column(BigInteger, nullable=True)
    chat_thread_id = Column(Integer, nullable=True)

    def set_chat(self, actor: User, chat_id: int, chat_thread_id: int):
        old_chat_id = self.chat_id
        old_chat_thread_id = self.chat_thread_id
        self.chat_id = chat_id
        self.chat_thread_id = chat_thread_id
        Log.updated(self, actor, [
            ("chat_id", old_chat_id, chat_id),
            ("chat_thread_id", old_chat_thread_id, chat_thread_id),
        ])
