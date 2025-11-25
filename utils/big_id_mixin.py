from typing import Type, TypeVar

from bafser import ObjMixin, get_db_session, randstr
from sqlalchemy import String
from sqlalchemy.orm import Mapped, Session, mapped_column

T = TypeVar("T", bound="BigIdMixin")


class BigIdMixin:
    id_big: Mapped[str] = mapped_column(String(8), unique=True, index=True, init=False)

    @classmethod
    def get_by_big_id(cls: Type[T], db_sess: Session, id_big: str, includeDeleted=False) -> T | None:
        if issubclass(cls, ObjMixin):
            return cls.query(db_sess, includeDeleted).filter(cls.id_big == id_big).first()
        else:
            return db_sess.query(cls).filter(cls.id_big == id_big).first()

    @classmethod
    def get_by_big_id2(cls: Type[T], id_big: str, includeDeleted=False) -> T | None:
        return cls.get_by_big_id(get_db_session(), id_big, includeDeleted)

    def set_unique_big_id(self, db_sess: Session):
        t = self
        while t is not None:
            id_big = randstr(8)
            t = self.get_by_big_id(db_sess, id_big, includeDeleted=True)
        self.id_big = id_big  # pyright: ignore[reportPossiblyUnboundVariable]

    def set_unique_big_id2(self):
        return self.set_unique_big_id(get_db_session())
