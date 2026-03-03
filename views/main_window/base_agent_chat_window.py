"""
基础对话框中心页：内嵌的 Agent 聊天窗口。
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QWidget,
    QSizePolicy, QTextBrowser,
)


class BaseAgentChatWindow(QFrame):
    """中心区域基础对话框页，占位；后续可替换为完整聊天 UI。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("baseAgentChatWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 消息列表使用可滚动区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("messageScrollArea")
        self.scroll_area.setWidgetResizable(True)

        self.message_list_container = QWidget(self.scroll_area)
        self.message_list_container.setObjectName("messageListContainer")
        self.message_list_layout = QVBoxLayout(self.message_list_container)
        self.message_list_layout.setContentsMargins(4, 4, 4, 4)
        self.message_list_layout.setSpacing(8)
        # 底部只保留一个整体弹性空白，避免每条消息之间被撑出大间距
        self.message_list_layout.addStretch(1)


        self.scroll_area.setWidget(self.message_list_container)

        # 底部输入区域
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(8, 8, 8, 8)

        self.input_box = QLineEdit(self)
        self.input_box.setObjectName("inputBox")
        self.input_box.setPlaceholderText("请输入要发送的内容...")

        send_button = QPushButton("发送", self)
        send_button.setObjectName("sendButton")
        send_button.clicked.connect(self.on_send_button_clicked)

        h_layout.addWidget(self.input_box, 9)
        h_layout.addWidget(send_button, 1)

        layout.addWidget(self.scroll_area, 4)  # 消息列表区域约占整体高度的大部分
        layout.addLayout(h_layout, 1)

    def create_message_item_with_user(self, user_name: str, message: str):
        # 创建单条消息和用户头像所在的独立消息项
        message_item = QWidget(self.message_list_container)
        message_item.setObjectName("messageItem")
        # 垂直方向高度根据内容动态变化，最小高度为整体消息区域高度的约 1/5
        message_item.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        message_with_user_layout = QHBoxLayout(message_item)
        message_with_user_layout.setContentsMargins(4, 4, 4, 4)
        message_with_user_layout.setSpacing(8)

        message_text_browser = QTextBrowser(message_item)
        message_text_browser.setObjectName("messageTextBrowser")
        message_text_browser.setText(message)
        # 这里使用 QFrame.Shape.NoFrame，避免 IDE 报 “未解析的特性引用 NoFrame”
        message_text_browser.setFrameStyle(QFrame.Shape.NoFrame)
        message_text_browser.setReadOnly(True)
        message_text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        message_text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        message_text_browser.setWordWrapMode(QTextOption.WrapMode.WrapAnywhere)
        message_text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        user_label = QLabel(user_name, message_item)
        user_label.setObjectName("userLabel")
        # 头像固定大小，例如 40x40
        user_label.setFixedSize(40, 40)
        user_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        message_with_user_layout.addWidget(message_text_browser, 9)
        message_with_user_layout.addWidget(user_label, 1)
        return message_item


    def create_message_item_with_agent(self):
        # 头像改到左边
        pass
    def add_message_item_to_message_list(self, message_item):
        """
        将消息 item 追加到列表底部，保证：
        - 消息之间只按 spacing(8) 的固定间距排列
        - 只有在消息总高度不足以填满可视区域时，底部才会出现一块整体空白
        """
        # 先移除当前底部的 stretch，再插入新消息，最后重新加回 stretch
        count = self.message_list_layout.count()
        if count > 0:
            last_item = self.message_list_layout.itemAt(count - 1)
            # QSpacerItem 没有 widget()，用这一点判断是否是 stretch
            if last_item is not None and last_item.widget() is None:
                spacer = self.message_list_layout.takeAt(count - 1)
                del spacer
        self.message_list_layout.addWidget(message_item)
        self.message_list_layout.addStretch(1)

    def on_send_button_clicked(self):
        edit_content=self.input_box.text()
        message_item=self.create_message_item_with_user(user_name="李",message=edit_content)
        self.add_message_item_to_message_list(message_item)
