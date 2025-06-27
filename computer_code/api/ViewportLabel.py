
import time
from PyQt5.QtWidgets import (

    QWidget,

)
from PyQt5.QtGui import QPixmap,QPainter

from PyQt5.QtCore import Qt


class Label(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.p = QPixmap()

    def setPixmap(self, p):
        self.p = p
        self.update()

    def paintEvent(self, event):
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            # Scale the pixmap while keeping the aspect ratio
            scaled_pixmap = self.p.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Calculate position to center the image
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2

            # Draw the scaled pixmap centered in the widget
            painter.drawPixmap(x, y, scaled_pixmap)