import uuid
from pathlib import Path

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QComboBox,
)


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
        self.setFixedSize(220, 80)
        self._dragging = False
        self._drag_offset = QPoint(0, 0)
        self.id=str(uuid.uuid4())
        self._mode = "button"
        self._text = f"{name}"

        self._button = QPushButton(self._text, self)
        self._button.clicked.connect(self._on_button_clicked)

        self._line_edit = QLineEdit(self)
        self._line_edit.setText(self._text)
        self._line_edit.editingFinished.connect(self._on_text_changed)
        self._line_edit.hide()

        # 创建右上角关闭按钮
        self._close_button = QPushButton("×", self)
        self._close_button.setObjectName("closeButton")
        self._close_button.setFixedSize(24, 24)
        self._close_button.clicked.connect(self._on_close_clicked)
        # 设置按钮位置到右上角
        self._close_button.move(self.width() - 24 - 5, 5)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self._title_label = QLabel("可拖拽信息组件", self)
        self._title_label.setObjectName("draggableInfoTitle")
        layout.addWidget(self._title_label)
        layout.addWidget(self._button)
        layout.addWidget(self._line_edit)

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
            self._button.setText(self._text)
            self._button.show()
            self._line_edit.hide()
        else:
            self._line_edit.setText(self._text)
            self._line_edit.show()
            self._button.hide()

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
        self._text = self._line_edit.text()
        self._button.setText(self._text)

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


class MainWindow(QMainWindow):
    dragableInfowidgets=[]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 热重载 + 可拖拽信息组件示例")
        self.resize(900, 600)

        # 加载当前窗口的样式
        self._load_styles()

        # 顶部工具栏区域（非系统 ToolBar，用 QWidget 自己布局）
        top_bar = QWidget(self)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(12)

        mode_label = QLabel("信息组件模式：", top_bar)
        self.mode_combo = QComboBox(top_bar)
        self.mode_combo.addItem("按钮模式", userData="button")
        self.mode_combo.addItem("可编辑文本模式", userData="editable")
        # self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)

        hint_label = QLabel("提示：按aaa住信息组件区域空白处拖拽即可移动位置。", top_bar)
        hint_label.setObjectName("hintLabel")

        create_draggableInfowidget=QPushButton("创建可拖拽信息组件", top_bar)
        create_draggableInfowidget.clicked.connect(self.create_draggableInfowidget)

        top_layout.addWidget(mode_label)
        top_layout.addWidget(self.mode_combo)
        top_layout.addStretch(1)
        top_layout.addWidget(create_draggableInfowidget)
        top_layout.addWidget(hint_label)

        # 中心区域，用来放置可拖拽信息组件
        self.canvas = QFrame(self)
        self.canvas.setObjectName("canvas")


        # 总布局：上方工具 + 下方画布
        central = QWidget(self)
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(10, 10, 10, 10)
        central_layout.setSpacing(10)

        central_layout.addWidget(top_bar)
        central_layout.addWidget(self.canvas, 1)

        self.setCentralWidget(central)

    def _load_styles(self):
        """
        从同名 css 文件中加载当前窗口的 Qt 样式。
        """
        css_path = Path(__file__).with_suffix(".css")
        if css_path.exists():
            try:
                with css_path.open("r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except OSError:
                # 如果样式读取失败，保持默认样式
                pass

    def on_mode_changed(self, index: int):
        mode = self.mode_combo.itemData(index)
        for info_widget in self.dragableInfowidgets:
            info_widget.set_mode(mode)

    def create_draggableInfowidget(self):
        print("[MainWindow] 创建可拖拽信息组件")
        # 在 canvas 上创建一个可拖拽组件
        name=str(len(self.dragableInfowidgets) + 1)
        info_widget = BaseDraggableInfoWidget(self.canvas, name=f"信息组件_{name}")
        info_widget.move(50, 50)
        info_widget.show()
        info_widget.raise_()
        # 连接删除信号
        info_widget.delete_requested.connect(self.delete_draggableInfowidget)
        self.dragableInfowidgets.append(info_widget)

    def delete_draggableInfowidget(self, widget):
        """删除指定的可拖拽信息组件"""
        print(f"[MainWindow] 删除可拖拽信息组件: {widget.id}")
        # 从列表中移除
        if widget in self.dragableInfowidgets:
            self.dragableInfowidgets.remove(widget)
        # 销毁组件
        widget.deleteLater()
