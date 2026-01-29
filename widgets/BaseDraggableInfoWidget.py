import uuid

from PySide6.QtWidgets import QFrame, QPushButton, QLineEdit, QLabel, QStackedWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, Signal

class BaseDraggableInfoWidget(QFrame):
    """
    可拖拽的信息组件：
    - 模式一：按钮（点击后在控制台输出当前文本）
    - 模式二：可编辑文本（QLineEdit）
    """
    # 定义删除信号，传递组件自身作为参数
    delete_requested = Signal(object)

    def __init__(self, parent=None,name=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedSize(220, 150)
        self._dragging = False
        self._drag_offset = QPoint(0, 0)
        self.id=str(uuid.uuid4())
        self._mode = "button"
        self._text = f"{name}"
        self._title_label_text="可拖拽信息组件"

        self._button = QPushButton(self._text, self)
        self._button.clicked.connect(self._on_button_clicked)

        self._line_edit = QLineEdit(self)
        self._line_edit.setText(self._title_label_text)
        self._line_edit.editingFinished.connect(self._on_text_changed)

        # 创建标题标签
        self._title_label = QLabel(self._title_label_text, self)
        self._title_label.setObjectName("draggableInfoTitle")

        # 使用 QStackedWidget：同一区域切换显示“标题”或“输入框”，避免布局跳动
        self._stacked = QStackedWidget(self)
        self._stacked.addWidget(self._title_label)   # 索引 0：button 模式
        self._stacked.addWidget(self._line_edit)     # 索引 1：editable 模式

        # 创建右上角关闭按钮
        self._close_button = QPushButton("×", self)
        self._close_button.setObjectName("closeButton")
        self._close_button.setFixedSize(8, 8)  # 增大按钮尺寸，便于点击和显示
        self._close_button.clicked.connect(self._on_close_clicked)

        # 创建水平布局：标题在左，关闭按钮在右
        layout_h = QHBoxLayout()
        layout_h.setContentsMargins(0, 0, 0, 0)
        layout_h.addStretch(1)
        layout_h.addWidget(self._close_button)

        # 主垂直布局：第一行关闭按钮，第二行堆叠（标题/输入框），第三行按钮
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addLayout(layout_h)
        layout.addWidget(self._stacked)  # 第二行固定为 stacked，只切换当前页
        layout.addWidget(self._button)
        self.setLayout(layout)

    def _on_close_clicked(self):
        """关闭按钮被点击时，发送删除信号"""
        self.delete_requested.emit(self)

    # ---- 模式切换相关 ----
    def set_mode(self, mode: str):
        """
        mode: "button" / "editable"
        """
        if mode not in ("button", "editable"):
            return
        self._mode = mode
        if mode == "button":
            self._title_label.setText(self._title_label_text)
            self._stacked.setCurrentIndex(0)  # 显示标题页
        else:
            self._line_edit.setText(self._title_label_text)
            self._stacked.setCurrentIndex(1)  # 显示输入框页

    def mode(self) -> str:
        return self._mode

    def set_text(self, text: str):
        self._text = text
        self._button.setText(text)
        self._line_edit.setText(text)

    def text(self) -> str:
        return self._text

    def _on_button_clicked(self):
        print(f"[DraggableInfoWidget] 按钮被点击，当前文本: {self._text}")

    def _on_text_changed(self):
        text = self._line_edit.text()
        self._title_label_text=text
        # self._button.setText(self._text)

    # ---- 拖拽相关事件 ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 检查点击位置是否在关闭按钮上，如果是则不触发拖拽
            click_pos = event.position().toPoint()
            if hasattr(self, '_close_button') and self._close_button.geometry().contains(click_pos):
                # 让关闭按钮处理点击事件
                super().mousePressEvent(event)
                return
            self._dragging = True
            self._drag_offset = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & Qt.LeftButton:
            # 在父容器坐标系中移动
            parent = self.parentWidget()
            if parent is not None:
                new_pos = event.globalPosition().toPoint() - parent.mapToGlobal(self._drag_offset)
                # 简单限制：不让组件拖出父容器边界
                new_x = max(0, min(new_pos.x(), parent.width() - self.width()))
                new_y = max(0, min(new_pos.y(), parent.height() - self.height()))
                self.move(new_x, new_y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        """当组件大小改变时，重新定位关闭按钮到右上角"""
        super().resizeEvent(event)
        if hasattr(self, '_close_button'):
            self._close_button.move(self.width() - self._close_button.width() - 5, 5)