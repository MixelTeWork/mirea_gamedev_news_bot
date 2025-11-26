from datetime import datetime

from bafser import IdMixin, Log, SqlAlchemyBase
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data import Tables
from data.quest import Quest
from data.user import User


class UserQuest(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.UserQuest
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))
    quest_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Quest}.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)

    user: Mapped[User] = relationship(init=False)
    quest: Mapped[Quest] = relationship(init=False)

    @staticmethod
    def add(user_id: int, quest_id: int):
        uq = UserQuest.get_by_uq(user_id, quest_id)
        if uq:
            return uq, False
        uq = UserQuest(user_id=user_id, quest_id=quest_id)
        Log.added(uq)
        return uq, True

    @staticmethod
    def get_by_uq(user_id: int, quest_id: int):
        return (
            UserQuest.query2()
            .filter(UserQuest.user_id == user_id)
            .filter(UserQuest.quest_id == quest_id)
            .first()
        )

    @staticmethod
    def get_user_points(user: User):
        return int(
            UserQuest.query2()
            .select_from(UserQuest)
            .join(Quest, Quest.id == UserQuest.quest_id)
            .filter(UserQuest.user_id == user.id)
            .value(func.sum(Quest.reward)) or 0
        )

    @staticmethod
    def get_completed_quests(user: User):
        return list(
            Quest.query2()
            .join(UserQuest, Quest.id == UserQuest.quest_id)
            .filter(UserQuest.user_id == user.id)
            .all()
        )
