from pydantic import BaseModel



class ConversationHistory(BaseModel):
    user_uuid: str
    conversation_id: str
    messages: list[dict]