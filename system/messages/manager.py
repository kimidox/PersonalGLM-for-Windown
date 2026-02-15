import json
import uuid

from system.database import get_session
from system.database.models import Messages


class MessageManager:


    def create_message(self,conversation_id:str, message:dict)->Messages:

        if "message_id" not in message:
            message["message_id"]=str(uuid.uuid4())
        #检查消息是否已经存在
        with get_session() as session:
            exist_message=session.query(Messages).filter(Messages.message_id==message["message_id"]).first()
            if exist_message:
                return exist_message
        message=Messages(
            message_id=message["message_id"],
            conversation_id=conversation_id,
            role=message["role"],
            content=message["content"]
        )
        with get_session() as session:
            session.add(message)
            session.commit()
        # print("create message:", message)
        return message

    def get_message(self, message_id:str)->Messages:
        with get_session() as session:
            message=session.query(Messages).filter(Messages.message_id==message_id).first()
        return message
    def get_messages_by_conversation_id(self, conversation_id:str)->list[Messages]:
        with get_session() as session:
            messages=session.query(Messages).where(Messages.conversation_id==conversation_id).all()
        return messages