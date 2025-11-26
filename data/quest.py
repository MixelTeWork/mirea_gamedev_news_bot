from datetime import datetime
from typing import Optional

from bafser import IdMixin, Log, SqlAlchemyBase
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from data import Tables


class Quest(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Quest

    name: Mapped[str] = mapped_column(String(128))
    chat_id: Mapped[int] = mapped_column(BigInteger)
    chat_thread_id: Mapped[int]
    reward: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)

    @staticmethod
    def new(name: str, chat_id: int, chat_thread_id: int):
        q = Quest(name=name, chat_id=chat_id, chat_thread_id=chat_thread_id, reward=5)
        Log.added(q)
        return q

    @staticmethod
    def get_by_topic(chat_id: int, chat_thread_id: int):
        return Quest.query2().filter(Quest.chat_id == chat_id, Quest.chat_thread_id == chat_thread_id).first()

    def update_name(self, name: str):
        self.name = name
        Log.updated(self)

    def set_reward(self, reward: int):
        self.reward = reward
        Log.updated(self)
