from __future__ import annotations

from typing import Optional, Union

import bafser_tgapi as tgapi
from bafser import IdMixin, Log, SqlAlchemyBase, Undefined, UserBase, use_db_session
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from data._tables import Tables
from data.user import User


class Broadcast(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Broadcast

    chat_id: Mapped[int] = mapped_column(BigInteger)
    chat_thread_id: Mapped[Optional[int]]
    title: Mapped[str] = mapped_column(String(256))

    @staticmethod
    def new(creator: UserBase, chat_id: int, chat_thread_id: int | None, title: str, db_sess: Session | None = None):
        db_sess = db_sess if db_sess else creator.db_sess
        bc = Broadcast(chat_id=chat_id, chat_thread_id=chat_thread_id, title=title)

        db_sess.add(bc)
        Log.added(bc, creator, [
            ("chat_id", chat_id),
            ("chat_thread_id", chat_thread_id),
            ("title", title),
        ], db_sess=db_sess)

        return bc

    @staticmethod
    def add_by_message(creator: User, msg: tgapi.Message):
        bc = Broadcast.get_by_message(creator.db_sess, msg)
        if bc:
            return False
        Broadcast.new(creator, msg.chat.id, Undefined.default(msg.message_thread_id), msg.chat.title)
        return True

    @staticmethod
    def add_by_chat(creator: User, chat: tgapi.Chat):
        bc = Broadcast.get_by_chat(creator.db_sess, chat.id, None)
        if bc:
            return False
        Broadcast.new(creator, chat.id, None, chat.title)
        return True

    @staticmethod
    def get_by_message(db_sess: Session, msg: tgapi.Message):
        return Broadcast.get_by_chat(db_sess, msg.chat.id, Undefined.default(msg.message_thread_id))

    @staticmethod
    def get_by_chat(db_sess: Session, chat_id: int, chat_thread_id: Union[int, None]):
        return db_sess.query(Broadcast).filter((Broadcast.chat_id == chat_id) & (Broadcast.chat_thread_id == chat_thread_id)).first()

    @staticmethod
    @use_db_session
    def sendMessage(
            text: str,
            use_markdown: bool = False,
            reply_markup: tgapi.InlineKeyboardMarkup | None = None,
            reply_parameters: tgapi.ReplyParameters | None = None,
            entities: list[tgapi.MessageEntity] | None = None,
            link_preview_options: tgapi.LinkPreviewOptions | None = None,
            db_sess: Session = Session,  # type: ignore
    ):
        for bc in Broadcast.all(db_sess):
            tgapi.sendMessage(chat_id=bc.chat_id, message_thread_id=bc.chat_thread_id,
                              text=text,
                              use_markdown=use_markdown,
                              reply_markup=reply_markup,
                              reply_parameters=reply_parameters,
                              entities=entities,
                              link_preview_options=link_preview_options,
                              )

    @staticmethod
    @use_db_session
    def sendMediaGroup(
            media: list[tgapi.InputMedia] = [],
            reply_parameters: tgapi.ReplyParameters | None = None,
            db_sess: Session = Session,  # type: ignore
    ):
        for bc in Broadcast.all(db_sess):
            tgapi.sendMediaGroup(chat_id=bc.chat_id, message_thread_id=bc.chat_thread_id,
                                 media=media,
                                 reply_parameters=reply_parameters,
                                 )

    def delete(self, actor: User, commit=True):
        self.db_sess.delete(self)
        Log.deleted(self, actor, commit=commit)
