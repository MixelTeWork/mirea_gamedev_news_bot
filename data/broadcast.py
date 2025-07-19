from __future__ import annotations
from typing import Union

from sqlalchemy import Column, Integer, BigInteger, String
from sqlalchemy.orm import Session

from bafser import SqlAlchemyBase, IdMixin, Log, use_db_session
from data._tables import Tables
from data.user import User
import tgapi


class Broadcast(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Broadcast

    chat_id = Column(BigInteger, nullable=False)
    chat_thread_id = Column(Integer, nullable=True)
    title = Column(String(256), nullable=False)

    @staticmethod
    def new(creator: User, chat_id: int, chat_thread_id: int, title: str, db_sess: Session = None):
        db_sess = db_sess if db_sess else Session.object_session(creator)
        reciever = Broadcast(chat_id=chat_id, chat_thread_id=chat_thread_id, title=title)

        db_sess.add(reciever)
        Log.added(reciever, creator, [
            ("chat_id", chat_id),
            ("chat_thread_id", chat_thread_id),
            ("title", title),
        ], db_sess=db_sess)

        return reciever

    @staticmethod
    def add_by_message(creator: User, msg: tgapi.Message):
        db_sess = Session.object_session(creator)
        bc = Broadcast.get_by_message(db_sess, msg)
        if bc:
            return False
        Broadcast.new(creator, msg.chat.id, msg.message_thread_id, msg.chat.title)
        return True

    @staticmethod
    def add_by_chat(creator: User, chat: tgapi.Chat):
        db_sess = Session.object_session(creator)
        bc = Broadcast.get_by_chat(db_sess, chat.id, None)
        if bc:
            return False
        Broadcast.new(creator, chat.id, None, chat.title)
        return True

    @staticmethod
    def get_by_message(db_sess: Session, msg: tgapi.Message):
        return Broadcast.get_by_chat(db_sess, msg.chat.id, msg.message_thread_id)

    @staticmethod
    def get_by_chat(db_sess: Session, chat_id: int, chat_thread_id: Union[int, None]):
        return db_sess.query(Broadcast).filter((Broadcast.chat_id == chat_id) & (Broadcast.chat_thread_id == chat_thread_id)).first()

    @staticmethod
    @use_db_session()
    def sendMessage(
            text: str,
            use_markdown: bool = False,
            reply_markup: tgapi.InlineKeyboardMarkup = None,
            reply_parameters: tgapi.ReplyParameters = None,
            entities: list[tgapi.MessageEntity] = None,
            link_preview_options: tgapi.LinkPreviewOptions = None,
            db_sess: Session = None,
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
    @use_db_session()
    def sendMediaGroup(
            media: list[tgapi.InputMedia] = [],
            reply_parameters: tgapi.ReplyParameters = None,
            db_sess: Session = None,
    ):
        for bc in Broadcast.all(db_sess):
            tgapi.sendMediaGroup(chat_id=bc.chat_id, message_thread_id=bc.chat_thread_id,
                                 media=media,
                                 reply_parameters=reply_parameters,
                                 )

    def delete(self, actor: User, commit=True):
        db_sess = Session.object_session(self)
        db_sess.delete(self)
        Log.deleted(self, actor, commit=commit)

    def get_dict(self):
        return self.to_dict(only=("chat_id", "chat_thread_id", "title"))
