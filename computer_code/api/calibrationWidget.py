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
    QSlider,
    QSplitter,
    QDialogButtonBox
)
from PyQt5.QtGui import QKeySequence, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot as Slot
import cameraThread
import settingsWidget
import alertWidget, videoSubSystem
from helpers import Cameras
# TODO have singleton for camera with a current camera param that stores current camera setting and 
# todo maybe also have this be singleton for setup data with a param for if it has been modified since saving 
class CalibrateWidget(QWidget):
    def __init__(self, parent=None):
        super(CalibrateWidget, self).__init__(parent)
        self.parent = parent
        self.cameras = Cameras.instance()
        self.index = 1
        # self.list_of_rotations = ["0","90", "180", "270"]

        self.camera_thread = cameraThread.MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
        self.data = (
            parent.data
        )  # Access parent's data list directly; modifications here affect parent
        self.main_layout = QVBoxLayout()
        self.webcam_settings_layout = QVBoxLayout()
        self.webcam_preview_layout = QHBoxLayout()
    
        # Shortcuts for deleting items in each list
        self.current_camera_label=QLabel()
        self.current_camera_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.main_layout.addWidget(self.current_camera_label)

    
        self.open_btn = QPushButton("Open The Camera", clicked=self.open_camera)
        self.webcam_settings_layout.addWidget(self.open_btn)

        self.settings_ui = settingsWidget.SettingsWidget(self)
        
        
        def selection_update_labels():
            if not self.camera_thread._running:
                self.settings_ui.update_labels()
        # self.settings_ui.update.connect(self.update_labels)
        # self.added_webcam_list.itemSelectionChanged.connect(selection_update_labels)
        self.webcam_settings_layout.addWidget(self.settings_ui)
        # self.webcam_settings_layout.addLayout(self.editable_fields_layout)

        # Use a QSplitter to allow resizing between settings and preview

        self.webcam_settings_widget = QWidget()
        self.webcam_settings_widget.setLayout(self.webcam_settings_layout)
        self.webcam_settings_widget.setMinimumWidth(300)  # Minimum width
        self.webcam_settings_widget.setMaximumWidth(500)  # Optional: Maximum width

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignRight)
        self.label.setMinimumSize(800, 600)
        self.preview_capture_settings_layout = QVBoxLayout()
        self.capture_settings_layout = QGridLayout()
        self.capture_btn = QPushButton("capture")
        self.capture_btn.clicked.connect(self.camera_thread.capture)
        self.capture_settings_layout.addWidget(self.capture_btn,0,0)

        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMaximum(10)
        self.sensitivity_slider.setMinimum(1)
        self.sensitivity_slider.valueChanged.connect(self.camera_thread.set_sensitivity)
        self.capture_settings_layout.addWidget(self.sensitivity_slider,0,1)
        self.auto_btn = QPushButton("auto capture")
        self.auto_btn.clicked.connect(self.camera_thread.auto_capture)
        self.capture_settings_layout.addWidget(self.auto_btn,1,0)

        self.timer_slider = QSlider(Qt.Horizontal)
        self.capture_settings_layout.addWidget(self.timer_slider,1,1)


        self.preview_capture_settings_layout.addWidget(self.label)
        self.preview_capture_settings_layout.addLayout(self.capture_settings_layout)

        # self.label.setBackgroundRole()
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.webcam_settings_widget)
        # To add widgets to a QSplitter, wrap the layout in a QWidget first
        preview_widget = QWidget()
        preview_widget.setLayout(self.preview_capture_settings_layout)
        splitter.addWidget(preview_widget)
        splitter.setSizes([200, 400])  # Initial sizes

        self.webcam_preview_layout.addWidget(splitter)

        self.camera_thread = cameraThread.MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
        self.back_btn = QPushButton("go back", clicked=self.go_back)
        self.webcam_settings_layout.addWidget(self.back_btn)
        self.main_layout.addLayout(self.webcam_preview_layout)
        # Set main_layout on a QWidget and set as central widget

        self.setLayout(self.main_layout)

        # self.setCentralWidget(central_widget)

    # Function to update editable fields when selection changes

    def get_index(self):
        if self.added_webcam_list.selectedItems():
            i = self.added_webcam_list.selectedItems()[0].data(Qt.UserRole)
        elif self.non_added_webcam_list.selectedItems():
            i = self.non_added_webcam_list.selectedItems()[0].data(Qt.UserRole)
        else:
            i = 0
        return i
    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
    

    def go_back(self):
        # self.camera_thread.stop()
        # if self.parent is not None and hasattr(self.parent, "show_setup"):
        self.parent.show_setup()
    def get_index(self):
        return self.index
    def open_camera(self):

        name = self.cameras.camera_params[self.get_index()]["name"]
        if not name:
            return
        camera_id = int(videoSubSystem.get_id_from_name(name))
        if (camera_id) == -1:
            print("stop")
            alert = alertWidget.alert_widget(
                "this camera could not be accessed", "ok", "", style=self.styleSheet()
            )
            alert.exec()
            return
        self.cameras.current_cam = camera_id
        print(camera_id)
        self.camera_thread.set_camera_id(self.cameras.current_cam)
        self.camera_thread.start()
        self.update_labels()
        self.settings_ui.update_labels()

    def update_labels(self):
        # todo not updating when change id number
        self.current_camera_label.setText(f"current camera: {self.cameras.camera_params[self.get_index()]["name"] } id {self.cameras.camera_params[self.get_index()]["id"]}")
        