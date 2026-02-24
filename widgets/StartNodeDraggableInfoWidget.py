import uuid

from PySide6.QtWidgets import QFrame, QPushButton, QLineEdit, QLabel, QStackedWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, Signal

from widgets.BaseDraggableInfoWidget import BaseDraggableInfoWidget


class StartNodeDraggableInfoWidget(BaseDraggableInfoWidget):
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

    def __init__(self, parent=None,name="开始节点",code=None):
        super().__init__(parent,name,code)

    def _build_stacked_widget(self) -> QStackedWidget:
        """
        子类自定义 stacked 内容：这里简单示例为“开始节点”标题 + 可编辑输入框。
        BaseDraggableInfoWidget 负责把 self._stacked 加到布局里。
        """
        # 标题标签
        self._title_label = QLabel("开始节点", self)
        self._title_label.setObjectName("draggableInfoTitle")

        # 可编辑输入框
        self._line_edit = QLineEdit(self)
        self._line_edit.setText("开始节点")
        self._line_edit.editingFinished.connect(self._on_text_changed)

        stacked = QStackedWidget(self)
        stacked.addWidget(self._title_label)   # 索引 0：button 模式
        stacked.addWidget(self._line_edit)     # 索引 1：editable 模式
        return stacked
    def set_mode(self, mode: str):
        """
        mode: "button" / "editable"
        """
        if mode not in ("button", "editable"):
            return
        self._mode = mode
        self._title_label_text=self._line_edit.text()
        if mode == "button":
            self._title_label.setText(self._title_label_text)
            self._stacked.setCurrentIndex(0)  # 显示标题页
        else:
            self._line_edit.setText(self._title_label_text)
            self._stacked.setCurrentIndex(1)  # 显示输入框页
    def _on_text_changed(self):
        text = self._line_edit.text()
        self._title_label_text=text

    def set_node_data(self,node_json:dict):
        pass

    def get_node_data(self)->dict:
        pass
