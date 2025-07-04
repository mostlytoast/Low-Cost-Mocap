from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter, QFontMetrics
from PyQt5.QtCore import Qt

class Label(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.p = QPixmap()
        self.text = ""
        self.text_flags = Qt.NoTextInteraction

    def setPixmap(self, p):
        self.p = p
        self.update()

    def setText(self, text):
        self.text = text
        self.update()

    def setTextInteractionFlags(self, flags):
        self.text_flags = flags
        self.setFocusPolicy(Qt.StrongFocus if flags & Qt.TextSelectableByKeyboard or flags & Qt.TextSelectableByMouse else Qt.NoFocus)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if not self.p.isNull():
            # Draw scaled pixmap
            scaled_pixmap = self.p.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        elif self.text:
            # Draw text centered in the widget
            painter.setRenderHint(QPainter.TextAntialiasing)
            painter.setPen(self.palette().text().color())
            font_metrics = QFontMetrics(self.font())
            text_width = font_metrics.horizontalAdvance(self.text)
            text_height = font_metrics.height()
            x = (self.width() - text_width) // 2
            y = (self.height() + text_height) // 2 - font_metrics.descent()
            painter.drawText(x, y, self.text)

    def mousePressEvent(self, event):
        if self.text_flags & Qt.TextSelectableByMouse:
            self.setFocus(True)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if self.text_flags & Qt.TextSelectableByKeyboard:
            super().keyPressEvent(event)