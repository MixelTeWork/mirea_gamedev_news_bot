from datetime import datetime

from bafser import IdMixin, Log, SqlAlchemyBase
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data import Tables
from data.user import User


class UserPoints(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.UserPoints
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))
    points: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)

    user: Mapped[User] = relationship(init=False)

    @staticmethod
    def new(user_id: int, points: int):
        uq = UserPoints(user_id=user_id, points=points)
        Log.added(uq)
        return uq

    @staticmethod
    def get_user_points(user: User):
        return int(
            UserPoints.query2()
            .select_from(UserPoints)
            .filter(UserPoints.user_id == user.id)
            .value(func.sum(UserPoints.points)) or 0
        )
