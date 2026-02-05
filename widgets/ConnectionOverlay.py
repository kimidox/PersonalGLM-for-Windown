"""
在画布上绘制组件之间连接线的覆盖层。
作为 canvas 的子控件，置于可拖拽组件下方，在 paintEvent 中绘制所有连线。
"""
from typing import List, Tuple, TYPE_CHECKING

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from widgets.BaseDraggableInfoWidget import BaseDraggableInfoWidget

# 连接表示为 (源组件, 源边, 目标组件, 目标边)
Connection = Tuple["BaseDraggableInfoWidget", str, "BaseDraggableInfoWidget", str]


class ConnectionOverlay(QWidget):
    """在画布上绘制连接线的透明覆盖层，不接收鼠标事件，置于组件下方。"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._connections: List[Connection] = []

    def set_connections(self, connections: List[Connection]) -> None:
        self._connections = list(connections)
        self.update()

    def add_connection(
        self,
        source: "BaseDraggableInfoWidget",
        source_side: str,
        target: "BaseDraggableInfoWidget",
        target_side: str,
    ) -> None:
        # 确保覆盖层与画布同大，避免初始时为 0×0 导致看不见线
        parent = self.parent()
        if parent and parent.rect().isValid():
            self.setGeometry(parent.rect())
        self._connections.append((source, source_side, target, target_side))
        self.update()

    def remove_connections_for_widget(self, widget: "BaseDraggableInfoWidget") -> None:
        """移除所有与该组件相关的连接。"""
        self._connections = [
            c for c in self._connections if c[0] is not widget and c[2] is not widget
        ]
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(80, 120, 200), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        for source, source_side, target, target_side in self._connections:
            try:
                # 连接点坐标是相对于父控件(canvas)的，本覆盖层与 canvas 同父且同几何，故即相对本控件
                p1 = source.get_connector_point(source_side)
                p2 = target.get_connector_point(target_side)
                painter.drawLine(p1, p2)
            except RuntimeError:
                # 组件已被删除
                continue
