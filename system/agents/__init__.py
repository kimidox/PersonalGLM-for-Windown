import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from random import randint

from langchain.agents import create_agent
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableWithMessageHistory, ConfigurableFieldSpec

from system.agents.manager import AgentManager
from system.agents_cache import agent_cache
from system.conversations.manager import ConversationManager
from system.llms import llm
from system.messages.manager import MessageManager


@dataclass
class ResponseFormat:
    city: str | None
    weather: str |None


class SQLiteMessageHistory(BaseChatMessageHistory):
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.message_manager = MessageManager()
        self._messages = None  # 延迟加载
        print("load history:", conversation_id)

    @property
    def messages(self) -> list[BaseMessage]:
        """延迟加载消息，只在需要时从数据库读取"""
        if self._messages is None:
            # 从数据库加载历史消息
            db_messages = self.message_manager.get_messages_by_conversation_id(self.conversation_id)

            # 将数据库消息转换为字典格式
            messages_dict = []
            if db_messages:
                for db_message in db_messages:
                    messages_dict.append({"role": db_message.role, "content": db_message.content,"message_id":db_message.message_id})

            # 转换为 LangChain 消息格式
            if messages_dict:
                self._messages = AgentManager.conver_messages_to_LangChainMessages(messages_dict)
                print(f"Loaded {len(self._messages)} messages from database:")
            else:
                self._messages = []
                print("No history messages found, starting with empty history")
        return self._messages

    def add_message(self, message: BaseMessage | dict) -> None:
        """添加消息到内存和数据库"""
        message_dict = None
        if isinstance(message, BaseMessage):
            message_dict = AgentManager.convert_LangChainMessage_to_dict(message)
            if "message_id" not in message_dict:
                message_dict["message_id"] = str(uuid.uuid4())
            if not message_dict["message_id"]:
                message_dict["message_id"] = str(uuid.uuid4())

            # 保存到数据库
            try:
                self.message_manager.create_message(self.conversation_id, message_dict)
                # 如果消息列表已加载，也添加到内存中
                if self._messages is not None:
                    if isinstance(message, BaseMessage):
                        self._messages.append(message)
                    else:
                        # 转换为 BaseMessage 后添加
                        converted = AgentManager.conver_messages_to_LangChainMessages([message_dict])
                        if converted:
                            self._messages.append(converted[0])
                print(f"Saved message to db: {message_dict}")
            except Exception as e:
                print(f"Failed to save message to db: {e}")
        elif isinstance(message, dict):
            pass


    def clear(self) -> None:
        self._messages = []

def get_db_chat_message_history(conversation_id:str)->BaseChatMessageHistory:

    return SQLiteMessageHistory(conversation_id)


def create_agent_with_history(user_id: str, conversation_id: str = None):

    SYSTEM_PROMPT = SystemMessage(content="""你是个天气小助手""")

    agent = create_agent(
        model=llm,
        system_prompt=SYSTEM_PROMPT
    )
    
    agent_cache.set_agent(user_id, agent)
    agent_from_cache = agent_cache.get_agent(user_id)
    
    agent_runnable_with_Message_history = RunnableWithMessageHistory(
        runnable=agent_from_cache,
        get_session_history=get_db_chat_message_history,  # 自动从数据库加载历史消息
        input_messages_key="messages",
        history_factory_config=[
            ConfigurableFieldSpec(
                id="conversation_id",
                annotation=str,
                name="Conversation ID",
                description="会话唯一标识",
                default="",
                is_shared=True,
            )
        ],
    )
    
    return agent_runnable_with_Message_history


if __name__ == "__main__":
    #示例1: 使用已存在的会话ID（会自动加载历史消息）
    # existing_conversation_id = "existing_conversation_id_123"
    # agent = create_agent_with_history("13277886732", existing_conversation_id)
    #
    # # 调用时，历史消息会自动从数据库加载并传递给智能体
    # res = agent.invoke(
    #     input={"messages": [{"role": "user", "content": "前面我问了哪个城市，天气如何"}]},
    #     config={"configurable": {"conversation_id": existing_conversation_id}}
    # )
    # print("Response:", res["messages"][-1])
    
    # 示例2: 创建新会话（没有历史消息）
    conversation = ConversationManager().create_conversation("13277886732", f"新会话{datetime.now().strftime('%Y-%m-%d %H:%M:%S')+str(randint(1,1000))}")
    new_conversation_id = conversation.conversation_id
    agent2 = create_agent_with_history("13277886732", new_conversation_id)

    # 第一次调用，没有历史消息
    res1 = agent2.invoke(
        input={"messages": [{"role": "user", "content": "今天北京的天气如何？"}]},
        config={"configurable": {"conversation_id": new_conversation_id}}
    )
    print("First response:", res1)

    # 第二次调用，会包含第一次的对话历史
    res2 = agent2.invoke(
        input={"messages": [{"role": "user", "content": "前面我问了哪个城市，天气如何"}]},
        config={"configurable": {"conversation_id": new_conversation_id}}
    )
    print("Second response:", res2)

    pass