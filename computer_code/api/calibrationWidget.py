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

class CalibrateWidget(QWidget):
    def __init__(self, parent=None):
        super(CalibrateWidget, self).__init__(parent)
        self.parent = parent

        # Create QStackedWidget to hold different UIs
        self.stacked_widget = QStackedWidget(self)
        
        # Create the different UI pages
        self.main_page = QWidget()
        self.single_page = QWidget()
        self.scratch_page = QWidget()

        # Setup main page
        main_layout = QVBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        main_layout.addWidget(self.back_button)
        self.main_page.setLayout(main_layout)

        # Setup single page
        single_layout = QVBoxLayout()
        single_label = QLabel("Single UI Page")
        single_layout.addWidget(single_label)
        self.single_page.setLayout(single_layout)

        # Setup scratch page
        scratch_layout = QVBoxLayout()
        scratch_label = QLabel("Scratch UI Page")
        scratch_layout.addWidget(scratch_label)
        self.scratch_page.setLayout(scratch_layout)
        self.layout = QVBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(parent.setup)
        scratch_layout.addWidget(self.back_button)
      

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_page)    # index 0
        self.stacked_widget.addWidget(self.single_page)  # index 1
        self.stacked_widget.addWidget(self.scratch_page) # index 2

        # Set layout for this widget
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def show_main(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_single(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_scratch(self):
        self.stacked_widget.setCurrentIndex(2)

    def go_back(self):
        if self.parent is not None and hasattr(self.parent, "setup"):
            self.parent.setup()
