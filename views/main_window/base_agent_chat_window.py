"""
基础对话框中心页：内嵌的 Agent 聊天窗口。
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit


class BaseAgentChatWindow(QFrame):
    """中心区域基础对话框页，占位；后续可替换为完整聊天 UI。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("baseAgentChatWidget")
        layout = QVBoxLayout(self)
        # 左上右下
        layout.setContentsMargins(4, 4, 4,4)

        title = QLabel("基础对话框（内嵌窗口）", self)
        title.setObjectName("baseAgentChatTitle")

        # 加一个水平布局
        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(8, 8, 8, 8)

        # 在水平布局里面加一个输入框和按钮
        input_box = QLineEdit( self)
        input_box.setObjectName("inputBox")
        input_box.setPlaceholderText("请输入要发送的内容...")


        send_button = QPushButton("发送", self)
        send_button.setObjectName("sendButton")

        h_layout.addWidget(input_box,9)
        h_layout.addWidget(send_button,1)

        layout.addWidget(title)
        layout.addLayout(h_layout)


