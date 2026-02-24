import uuid
from abc import abstractmethod, ABC

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
    # 连接点被点击：自身、边（"left"/"right"）
    connector_clicked = Signal(object, str)
    # 组件被移动，用于连线覆盖层重绘
    moved = Signal()
    input_data={}
    output_data={}
    node_data={}

    def __init__(self, parent=None,name=None,code=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedSize(220, 150)
        self._dragging = False
        self._drag_offset = QPoint(0, 0)
        self.id=str(uuid.uuid4())
        self._mode = "button"
        self._text = f"编辑"


        self._button = QPushButton(self._text, self)
        self._button.clicked.connect(self._on_button_clicked)

        # 由（可能的）子类负责组装 self._stacked，父类只负责放入布局
        self._stacked = self._build_stacked_widget()

        # 创建右上角关闭按钮
        self._close_button = QPushButton("×", self)
        self._close_button.setObjectName("closeButton")
        self._close_button.setFixedSize(8, 8)  # 增大按钮尺寸，便于点击和显示
        self._close_button.clicked.connect(self._on_close_clicked)

        # 左右两侧连接点按钮（“+”号）
        self._left_connector = QPushButton("+", self)
        self._left_connector.setObjectName("leftConnector")
        self._left_connector.setFixedSize(16, 16)
        self._left_connector.clicked.connect(lambda: self._on_connector_clicked("left"))

        self._right_connector = QPushButton("+", self)
        self._right_connector.setObjectName("rightConnector")
        self._right_connector.setFixedSize(16, 16)
        self._right_connector.clicked.connect(lambda: self._on_connector_clicked("right"))

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

    def _build_stacked_widget(self) -> QStackedWidget:
        # 子类实现
        pass

    def _on_close_clicked(self):
        """关闭按钮被点击时，发送删除信号"""
        self.delete_requested.emit(self)

    # ---- 模式切换相关 ----

    def set_mode(self, mode: str):
        # 子类实现
        pass

    def mode(self) -> str:
        return self._mode


    def text(self) -> str:
        return self._text

    def _on_button_clicked(self):
        """
        点击组件上的“编辑”按钮，在按钮模式与可编辑文本模式之间切换。
        """
        if self._mode == "button":
            # 进入可编辑模式
            self.set_mode("editable")
            self._button.setText("保存")
        else:
            # 返回按钮模式
            self.set_mode("button")
            self._button.setText("编辑")



    def _on_connector_clicked(self, side: str):
        """
        边缘“+”号被点击。
        side: "left" 或 "right"
        """
        self.connector_clicked.emit(self, side)

    # ---- 拖拽相关事件 ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 检查点击位置是否在关闭按钮上，如果是则不触发拖拽
            click_pos = event.position().toPoint()
            if hasattr(self, '_close_button') and self._close_button.geometry().contains(click_pos):
                # 让关闭按钮处理点击事件
                super().mousePressEvent(event)
                return
            # 点击在左右“+”连接点上时，同样不触发拖拽
            if hasattr(self, '_left_connector') and self._left_connector.geometry().contains(click_pos):
                super().mousePressEvent(event)
                return
            if hasattr(self, '_right_connector') and self._right_connector.geometry().contains(click_pos):
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
                self.moved.emit()
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
        # 同时重新定位左右“+”连接点到组件左右两侧中间
        if hasattr(self, '_left_connector'):
            cy = self.height() // 2 - self._left_connector.height() // 2
            # 略微移出边框，让按钮中心在边界上
            self._left_connector.move(-self._left_connector.width() // 2, cy)
        if hasattr(self, '_right_connector'):
            cy = self.height() // 2 - self._right_connector.height() // 2
            self._right_connector.move(self.width() - self._right_connector.width() // 2, cy)

    def set_input_data(self,data):
        self.input_data=data
    def set_output_data(self,data):
        self.output_data=data

    def set_node_data(self,data):
        self.node_data=data

    def get_input_data(self)->dict:
        res=self.input_data
        return res
    def get_output_data(self)->dict:
        res=self.output_data
        return res
    def get_node_data(self)->dict:
        res=self.node_data
        return res

    # ---- 提供给外部用于计算连线位置的辅助函数 ----
    def get_connector_point(self, side: str) -> QPoint:
        """
        获取连接点在父组件坐标系中的坐标，用于画连线。
        side: "left" / "right"
        """
        if side == "left":
            local = QPoint(0, self.height() // 2)
        else:
            local = QPoint(self.width(), self.height() // 2)
        # 映射到父组件坐标
        return self.mapToParent(local)