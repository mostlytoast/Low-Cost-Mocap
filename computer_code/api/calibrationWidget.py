import json
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
    QFileDialog,
    QStackedWidget,
    QDialog,
    QDialogButtonBox
)
from PyQt5.QtGui import QKeySequence, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot as Slot

# import sys
# import api.cameraThread
# import videoSubSystem
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMessageBox

class calibrate_widget(QWidget):
    def __init__(self, parent=None):
        super(calibrate_widget, self).__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(parent.setup)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

    def single_ui(self):
        print()
        

    def scratch_ui(self):
        # self.layout = QVBoxLayout()
        self.back_button = QPushButton("Back4444")
        self.back_button.clicked.connect(self.parent.setup)
        
        self.layout.addWidget(self.back_button)
        # self.setLayout(self.layout)


    # def go_back(self):
    #     # Assumes parent is MainWindow and has a QStackedWidget as central_widget
    #     parent = self.parent
    #     if hasattr(parent, "central_widget"):
    #         for i in range(parent.central_widget.count()):
    #             widget = parent.central_widget.widget(i)
    #             if isinstance(widget, setup_window):
    #                 parent.central_widget.setCurrentWidget(widget)
    #                 break
    # def calib(self):
    #     parent = self.parent
    #     if hasattr(parent, "central_widget"):
    #         parent.central_widget.setCurrentWidget(self)

