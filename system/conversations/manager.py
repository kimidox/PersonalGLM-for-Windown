import uuid



from system.conversations.model import ConversationHistory
from system.database import get_session
from system.database.models import Conversations, Messages
from system.messages.manager import MessageManager


class ConversationManager:

    def create_conversation(self, user_id:str, title:str)->Conversations:
        """
        创建一个会话
        :param user_id:
        :return:
        """
        conversation = Conversations(
            conversation_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title
        )
        with get_session() as session:
            try:
                session.add(conversation)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            return conversation

    def check_conversation_exist(self, conversation_id:str)->bool:
        """
        检查会话是否存在
        :param conversation_id:
        :return:
        """
        with get_session() as session:
            conversation = session.query(Conversations).filter(Conversations.conversation_id == conversation_id).first()
        return conversation is not None
    def get_conversation(self, conversation_id:str)->Conversations:
        """
        获取一个会话
        :param conversation_id:
        :return:
        """
        with get_session() as session:
            conversation = session.query(Conversations).filter(Conversations.conversation_id == conversation_id).first()
        return conversation

    def get_conversation_history(self, user_id:str,conversation_id:str)->ConversationHistory:
        """
        获取会话历史
        :param user_id:
        :param conversation_id:
        :return:
        """
        mssager_manager=MessageManager()
        messages:list[Messages]=mssager_manager.get_messages_by_conversation_id(conversation_id)
        messages_dict=[message.to_dict() for message in messages]
        return ConversationHistory(
            user_uuid=user_id,
            conversation_id=conversation_id,
            messages=messages_dict
        )

