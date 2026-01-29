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
    QStackedWidget,
)

from widgets.BaseDraggableInfoWidget import BaseDraggableInfoWidget


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
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)

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

    @staticmethod
    def get_object_widget():
        pass
