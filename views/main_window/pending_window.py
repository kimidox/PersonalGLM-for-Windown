"""
待办/画布中心页：可拖拽节点与连线。
"""

from PySide6.QtWidgets import QWidget, QFrame
from widgets.ConnectionOverlay import ConnectionOverlay


class PendingWindow(QWidget):
    """中心区域画布页，承载可拖拽信息组件与连线覆盖层。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pendingWindow")

        self.canvas = QFrame(self)
        self.canvas.setObjectName("canvas")
        self.canvas.setGeometry(self.rect())

        self.connection_overlay = ConnectionOverlay(self.canvas)
        self.connection_overlay.setGeometry(self.canvas.rect())
        self.connection_overlay.lower()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_overlay_geometry()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_overlay_geometry()

    def _update_overlay_geometry(self):
        self.canvas.setGeometry(self.rect())
        if self.connection_overlay:
            self.connection_overlay.setGeometry(self.canvas.rect())
