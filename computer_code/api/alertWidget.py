import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    # QListWidgetItem,
    QShortcut,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QAction,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QGridLayout,
    QStackedWidget,
    QDialog,
    QDialogButtonBox,
    QSlider,
)


class alert_widget(QDialog):
    def __init__(
        self, msg, accept_msg="ok", reject_msg="", style=None, parent=None, title = "error"
    ):
        super(alert_widget, self).__init__(parent)
        if style:
            self.setStyleSheet(style)

        self.setWindowTitle(title)

        QBtn = QDialogButtonBox.Ok
        if reject_msg != "":
            QBtn = QBtn | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.button(QDialogButtonBox.Ok).setText(accept_msg)
        if reject_msg != "":
            self.buttonBox.rejected.connect(self.reject)
            self.buttonBox.button(QDialogButtonBox.Cancel).setText(reject_msg)

        layout = QVBoxLayout()
        message = QLabel(msg)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def accept(self):
        return super().accept()
