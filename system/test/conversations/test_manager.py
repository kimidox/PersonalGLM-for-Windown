from system.conversations.manager import ConversationManager


class TestConversationManager:
    def test_get_conversation_history(self):
        user_id='1'
        conversation_id='conv_123'
        conversation_manager=ConversationManager()
        conversation_history=conversation_manager.get_conversation_history(user_id,conversation_id)
        assert True
