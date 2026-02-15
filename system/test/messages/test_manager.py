from system.messages.manager import MessageManager


class TestMessageManager:
    def test_create_message(self):
        test_conversation_id = "conv_123"
        test_message_content = "Hello, pytest!"
        mock_message_id = "mock-uuid-123456"

        message_manager=MessageManager()
        message = message_manager.create_message(test_conversation_id, test_message_content)
        assert True