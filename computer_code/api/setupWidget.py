
from PyQt5.QtWidgets import (
  
    QListWidget,
    # QListWidgetItem,
    QShortcut,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QGridLayout,
 
    QSlider,
)
from PyQt5.QtGui import QKeySequence, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot as Slot



# import sys
import cameraThread
import settingsWidget
import videoSubSystem
from PyQt5.QtWidgets import QSplitter
from helpers import  Cameras
        

import alertWidget


class setup_window(QWidget):
    def __init__(self, parent=None):
        super(setup_window, self).__init__(parent)
        # self.list_of_rotations = ["0","90", "180", "270"]

        self.camera_thread = cameraThread.MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
        self.cameras = Cameras.instance()
        self.main_layout = QVBoxLayout()
        self.webcam_settings_layout = QVBoxLayout()
        self.webcam_preview_layout = QHBoxLayout()
        self.webcam_list_layout = QGridLayout()
        self.move_buttons_layout = QVBoxLayout()

        # added webcams
        self.added_webcam_list = QListWidget()
        self.webcam_list_layout.addWidget(QLabel("added webcams"), 0, 0)

        self.webcam_list_layout.addWidget(self.added_webcam_list, 1, 0)
        # center buttons
        self.reload_button = QPushButton("reload")
        self.reload_button.clicked.connect(self.reload_cameras)
        self.move_buttons_layout.addWidget(self.reload_button)
        self.add_button = QPushButton("<")
        self.add_button.clicked.connect(self.add_webcam)
        self.move_buttons_layout.addWidget(self.add_button)
        self.setup_button = QPushButton(">")
        self.setup_button.clicked.connect(self.remove_webcam)
        self.move_buttons_layout.addWidget(self.setup_button)

        self.webcam_list_layout.addLayout(self.move_buttons_layout, 1, 1)

        # webcams not added
        self.non_added_webcam_list = QListWidget()
        self.webcam_list_layout.addWidget(QLabel("non added webcams"), 0, 2)
        self.webcam_list_layout.addWidget(self.non_added_webcam_list, 1, 2)

        # Ensure only one list has a selection at a time and clicking an item selects it immediately
        def handle_added_selection():
            if self.added_webcam_list.selectedItems():
                self.non_added_webcam_list.clearSelection()

        def handle_non_added_selection():
            if self.non_added_webcam_list.selectedItems():
                self.added_webcam_list.clearSelection()

        self.added_webcam_list.itemSelectionChanged.connect(handle_added_selection)
        self.non_added_webcam_list.itemSelectionChanged.connect(
            handle_non_added_selection
        )

        # Make single-click select items (default for QListWidget), but ensure focus follows mouse
        self.added_webcam_list.setSelectionMode(QListWidget.SingleSelection)
        self.non_added_webcam_list.setSelectionMode(QListWidget.SingleSelection)
        self.added_webcam_list.setFocusPolicy(Qt.StrongFocus)
        self.non_added_webcam_list.setFocusPolicy(Qt.StrongFocus)

        self.main_layout.addLayout(self.webcam_list_layout)
        # Shortcuts for deleting items in each list
        self.update_list()

        self.delete_shortcut1 = QShortcut(
            QKeySequence(Qt.Key_Right), self.added_webcam_list
        )
        self.delete_shortcut1.setContext(Qt.WidgetShortcut)
        self.delete_shortcut1.activated.connect(self.remove_webcam)

        self.delete_shortcut2 = QShortcut(
            QKeySequence(Qt.Key_Left), self.non_added_webcam_list
        )
        self.delete_shortcut2.setContext(Qt.WidgetShortcut)
        self.delete_shortcut2.activated.connect(self.add_webcam)

        self.open_btn = QPushButton("Open The Camera", clicked=self.open_camera)
        self.webcam_settings_layout.addWidget(self.open_btn)

        self.settings_ui = settingsWidget.SettingsWidget(self)
        
        
        def selection_update_labels():
            if not self.camera_thread._running:
                self.settings_ui.update_labels()

        self.added_webcam_list.itemSelectionChanged.connect(selection_update_labels)
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
        # self.label.setBackgroundRole()
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.webcam_settings_widget)
        splitter.addWidget(self.label)
        splitter.setSizes([200, 400])  # Initial sizes

        self.webcam_preview_layout.addWidget(splitter)

        self.camera_thread = cameraThread.MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
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


    def remove_webcam(self):
        selected_items = self.added_webcam_list.selectedItems()
        for item in selected_items:
            self.added_webcam_list.takeItem(self.added_webcam_list.row(item))
            self.non_added_webcam_list.addItem(item)
            self.cameras.camera_params[item.data(Qt.UserRole)]["added"] = False

    def add_webcam(self):
        selected_items = self.non_added_webcam_list.selectedItems()
        for item in selected_items:
            self.non_added_webcam_list.takeItem(self.non_added_webcam_list.row(item))
            self.added_webcam_list.addItem(item)
            self.cameras.camera_params[item.data(Qt.UserRole)]["added"] = True

    def update_list(self):
        self.added_webcam_list.clear()
        self.non_added_webcam_list.clear()
        for index, webcam in enumerate(self.cameras.camera_params):
            item = None
            # get targeted list
            target_list = (
                self.added_webcam_list
                if webcam.get("added", False)
                else self.non_added_webcam_list
            )
            target_list.addItem(webcam["name"])
            item = target_list.item(target_list.count() - 1)
            if not webcam.get("calibrated", False):
                item.setForeground(Qt.gray)
                item.setToolTip("not calibrated")
            if not webcam.get("connected", False):
                item.setForeground(Qt.red)
                item.setToolTip("not connected")
            item.setData(Qt.UserRole, index)
        #

    def reload_cameras(self):
        """_summary_ reloads the list of cameras connected to the system"""

        # TODO have to find way of adding newly added cameras in system to list
        def add_camera(attached_webcam):
            cam_id = videoSubSystem.get_id_from_name(attached_webcam[0])
            res = videoSubSystem.getResolution(cam_id)[0]
            settings = videoSubSystem.getSettings(cam_id)

            self.cameras.camera_params.append(
                {
                    "intrinsic_matrix": [],
                    "distortion_coef": [],
                    "rotation": 0,
                    "id": None,
                    "name": attached_webcam[0],
                    "width": res[0],
                    "height": res[1],
                    "connected": True,
                    "calibrated": False,
                    "added": False,
                }
                | settings
            )

        attached_webcams = videoSubSystem.listWebcams()
        # TODO find better way of doing this
        if self.cameras.camera_params == []:
            for attached_webcam in attached_webcams:
                add_camera(attached_webcam)
        # self.update_list()

        else:
            for current_webcams in self.cameras.camera_params:
                for attached_webcam in attached_webcams:
                    if not any(cam["name"] == attached_webcam[0] for cam in self.cameras.camera_params):
                        add_camera(attached_webcam)
                    # assume its false
                    current_webcams["connected"] = False

                    if current_webcams["name"] == attached_webcam[0]:
                        current_webcams["connected"] = True
                        break

        self.update_list()

    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
    
    def open_camera(self):
        try:
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
            self.settings_ui.update_labels()
        except:
            alert = alertWidget.alert_widget(
                "this camera could not be accessed", "ok", "", style=self.styleSheet()
            )
            alert.exec()
