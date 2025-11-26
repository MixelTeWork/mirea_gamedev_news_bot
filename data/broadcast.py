from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

import bafser_tgapi as tgapi
from bafser import IdMixin, Log, SqlAlchemyBase, Undefined, get_db_session, use_db_sess
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from data._tables import Tables


class Broadcast(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Broadcast

    chat_id: Mapped[int] = mapped_column(BigInteger)
    chat_thread_id: Mapped[Optional[int]]
    title: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)

    @staticmethod
    def new(chat_id: int, chat_thread_id: int | None, title: str):
        bc = Broadcast(chat_id=chat_id, chat_thread_id=chat_thread_id, title=title)
        Log.added(bc)
        return bc

    @staticmethod
    def add_by_message(msg: tgapi.Message):
        bc = Broadcast.get_by_message(msg)
        if bc:
            return False
        Broadcast.new(msg.chat.id, Undefined.default(msg.message_thread_id), msg.chat.title)
        return True

    @staticmethod
    def add_by_chat(chat: tgapi.Chat):
        bc = Broadcast.get_by_chat(chat.id, None)
        if bc:
            return False
        Broadcast.new(chat.id, None, chat.title)
        return True

    @staticmethod
    def get_by_message(msg: tgapi.Message):
        return Broadcast.get_by_chat(msg.chat.id, Undefined.default(msg.message_thread_id))

    @staticmethod
    def get_by_chat(chat_id: int, chat_thread_id: Union[int, None]):
        return get_db_session().query(Broadcast).filter((Broadcast.chat_id == chat_id) & (Broadcast.chat_thread_id == chat_thread_id)).first()

    @staticmethod
    @use_db_sess
    def sendMessage(
            db_sess: Session,
            text: str,
            use_markdown: bool = False,
            reply_markup: tgapi.InlineKeyboardMarkup | None = None,
            reply_parameters: tgapi.ReplyParameters | None = None,
            entities: list[tgapi.MessageEntity] | None = None,
            link_preview_options: tgapi.LinkPreviewOptions | None = None,
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
    @use_db_sess
    def sendMediaGroup(
            db_sess: Session,
            media: list[tgapi.InputMedia] = [],
            reply_parameters: tgapi.ReplyParameters | None = None,
    ):
        for bc in Broadcast.all(db_sess):
            tgapi.sendMediaGroup(chat_id=bc.chat_id, message_thread_id=bc.chat_thread_id,
                                 media=media,
                                 reply_parameters=reply_parameters,
                                 )

    def delete(self, commit=True):
        self.db_sess.delete(self)
        Log.deleted(self, commit=commit)
