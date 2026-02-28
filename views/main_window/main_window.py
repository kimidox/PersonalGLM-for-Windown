from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QStackedWidget,
)

from widgets.BaseDraggableInfoWidget import BaseDraggableInfoWidget
from widgets.StartNodeDraggableInfoWidget import StartNodeDraggableInfoWidget
from views.main_window.pending_window import PendingWindow
from views.main_window.base_agent_chat_window import BaseAgentChatWindow


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

        BaseAgentChatButton=QPushButton("基础对话框",parent=top_bar)
        BaseAgentChatButton.setObjectName("BaseAgentChatButton")
        BaseAgentChatButton.clicked.connect(self.change_center_area_to_base_agent_chat)


        hint_label = QLabel("提示：按aaa住信息组件区域空白处拖拽即可移动位置。", top_bar)
        hint_label.setObjectName("hintLabel")

        # 下拉选项框：选择“开始节点”时创建可拖拽信息组件
        self.node_combo = QComboBox(top_bar)
        self.node_combo.addItem("开始节点")
        self.node_combo.activated.connect(self.on_node_selected)

        save_push_button=QPushButton("保存",top_bar)
        save_push_button.clicked.connect(self.save_arrangement_infos)

        # 顶部不再使用全局模式切换，下方每个节点通过自己的“编辑”按钮切换模式
        top_layout.addWidget(BaseAgentChatButton)
        # addStretch()会添加一个可伸缩的空白区域
        top_layout.addStretch(1)
        top_layout.addWidget(self.node_combo)
        top_layout.addWidget(save_push_button)
        top_layout.addWidget(hint_label)

        # 中心区域：画布页（可拖拽节点 + 连线）
        self.pending_window = PendingWindow(self)
        self.canvas = self.pending_window.canvas
        self.connection_overlay = self.pending_window.connection_overlay

        # 中心区域堆叠：0=画布，1=基础对话框内嵌窗口（点击按钮切换）
        self.center_stacked = QStackedWidget(self)
        self.center_stacked.addWidget(self.pending_window)

        # 基础对话框内嵌窗口
        self.base_agent_chat_window = BaseAgentChatWindow(self)
        self.center_stacked.addWidget(self.base_agent_chat_window)

        # 设置默认窗口为基础对话窗口
        self.center_stacked.setCurrentIndex(1)

        # 两段式连线：第一次点击记录“起点”，第二次点击记录“终点”并画线
        self._pending_connection = None  # None 或 (widget, side)

        # 总布局：上方工具 + 下方画布
        central = QWidget(self)
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(10, 10, 10, 10)
        central_layout.setSpacing(10)

        central_layout.addWidget(top_bar)
        central_layout.addWidget(self.center_stacked, 1)

        self.setCentralWidget(central)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_overlay_geometry()

    def showEvent(self, event):
        """窗口首次显示时布局才完成，此时同步覆盖层尺寸，否则覆盖层可能是 0×0 看不到连线"""
        super().showEvent(event)
        self._update_overlay_geometry()

    def _update_overlay_geometry(self):
        if hasattr(self, "pending_window") and self.pending_window:
            self.pending_window._update_overlay_geometry()

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

    def on_node_selected(self, index: int):
        text = self.node_combo.itemText(index)
        if text == "开始节点":
            self.create_draggableInfowidget(class_name=StartNodeDraggableInfoWidget)

    def create_draggableInfowidget(self,class_name=BaseDraggableInfoWidget):
        print("[MainWindow] 创建可拖拽信息组件")
        # 在 canvas 上创建一个可拖拽组件
        id=str(len(self.dragableInfowidgets) + 1)
        info_widget = class_name(self.canvas, code=f"信息组件_{id}")
        info_widget.move(50, 50)
        info_widget.show()
        info_widget.raise_()
        # 连接删除信号
        info_widget.delete_requested.connect(self.delete_draggableInfowidget)

        # 连接连接点信号
        info_widget.connector_clicked.connect(self.on_connector_clicked)
        # 组件移动时重绘连线
        info_widget.moved.connect(self.connection_overlay.update)

        self.dragableInfowidgets.append(info_widget)

    def delete_draggableInfowidget(self, widget):
        """删除指定的可拖拽信息组件"""
        print(f"[MainWindow] 删除可拖拽信息组件: {widget.id}")
        # 取消未完成的连线（若起点是该组件）
        if self._pending_connection and self._pending_connection[0] is widget:
            self._pending_connection = None
        # 移除与该组件相关的所有连线
        self.connection_overlay.remove_connections_for_widget(widget)
        # 从列表中移除
        if widget in self.dragableInfowidgets:
            self.dragableInfowidgets.remove(widget)
        # 销毁组件
        widget.deleteLater()

    def on_connector_clicked(self, widget: BaseDraggableInfoWidget, side: str):
        if self._pending_connection is None:
            # 第一次点击：记录起点
            self._pending_connection = (widget, side)
            print(f"[MainWindow] 连线起点: {widget.id} {side}，请点击另一个组件的连接点")
            return
        # 第二次点击：若为不同组件则画线
        source_widget, source_side = self._pending_connection
        if widget is source_widget:
            # 点到同一组件，取消本次连线
            self._pending_connection = None
            print("[MainWindow] 已取消连线")
            return
        self.connection_overlay.add_connection(source_widget, source_side, widget, side)
        self._pending_connection = None
        print(f"[MainWindow] 已连线: {source_widget.id} {source_side} -> {widget.id} {side}")

    def change_center_area_to_base_agent_chat(self):
        """点击「基础对话框」按钮：在画布(0)与基础对话框(1)之间切换。"""
        idx = self.center_stacked.currentIndex()
        if idx==0:
            # 切换为基础对话框
            self.center_stacked.setCurrentIndex(1)
        else:
            # 切换为画布
            self.center_stacked.setCurrentIndex(0)
    @staticmethod
    def get_object_widget():
        res=MainWindow.dragableInfowidgets
        return res

    def save_arrangement_infos(self):
        res=MainWindow.get_object_widget()
        pass
