from bafser import IdMixin, SqlAlchemyBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data import Tables
from data.quest import Quest
from data.user import User


class UserQuest(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.UserQuest
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))
    quest_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Quest}.id"))

    user: Mapped[User] = relationship(init=False)
    quest: Mapped[Quest] = relationship(init=False)
