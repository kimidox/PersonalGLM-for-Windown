from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage


class AgentManager:

    @staticmethod
    def conver_messages_to_LangChainMessages(messages: list[dict])-> list[BaseMessage]:
        res_messages=[]
        for message in messages:

            if message["role"]=="user":
                res_messages.append(HumanMessage(content=message["content"],additional_kwargs={"message_id":message["message_id"]}))
            elif message["role"]=="assistant":
                res_messages.append(AIMessage(content=message["content"],additional_kwargs={"message_id":message["message_id"]}))
            elif message["role"]=="system":
                res_messages.append(SystemMessage(content=message["content"],additional_kwargs={"message_id":message["message_id"]}))
            else:
                raise Exception("不支持的消息类型")

        return res_messages
    
    @staticmethod
    def convert_LangChainMessage_to_dict(message: BaseMessage) -> dict:
        if isinstance(message, HumanMessage):
            return {"role": "user", "content": message.content,"message_id":message.additional_kwargs.get("message_id")}
        elif isinstance(message, AIMessage):
            return {"role": "assistant", "content": message.content,"message_id":message.additional_kwargs.get("message_id")}
        elif isinstance(message, SystemMessage):
            return {"role": "system", "content": message.content,"message_id":message.additional_kwargs.get("message_id")}
        else:
            # 尝试通过 type 属性判断
            if hasattr(message, 'type'):
                if message.type == "human":
                    return {"role": "user", "content": message.content,"message_id":message.additional_kwargs.get("message_id")}
                elif message.type == "ai":
                    return {"role": "assistant", "content": message.content,"message_id":message.additional_kwargs.get("message_id")}
                elif message.type == "system":
                    return {"role": "system", "content": message.content,"message_id":message.additional_kwargs.get("message_id")}
            raise Exception(f"不支持的消息类型: {type(message)}")

