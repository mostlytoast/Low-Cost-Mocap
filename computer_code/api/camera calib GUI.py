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
from PyQt5.QtGui import QKeySequence, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot as Slot
import file_mech
import numpy as np

# import sys
import cameraThread
import videoSubSystem
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtGui import QIntValidator

import calibrationWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.file = file_mech.file_dialog(self)
        self.camera_poses = []
        self.to_world_coords_matrix = np.eye(4)
        self.camera_params = []
        self.initUI()
        self.save_path = ""

    def initUI(self):
        # TODO need new data structure that better supports edits
        self.data = [
            {
                "intrinsic_matrix": [
                    [677.8118436477158, 0.0, 369.67423322200443],
                    [0.0, 682.103355075851, 283.2898247123011],
                    [0.0, 0.0, 1.0],
                ],
                "distortion_coef": [
                    [
                        0.07002292606292972,
                        -0.40894724240016145,
                        -0.020332839259062062,
                        0.00025543761137419597,
                        1.157665841456218,
                    ]
                ],
                "rotation": 0,
                "id": 3,
                "name": "Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-1.4):",
                "width": 800,
                "height": 600,
                "connected": False,
                "calibrated": False,
                "added": False,
            },
            {
                "intrinsic_matrix": [
                    [679.654681050567, 0.0, 404.0916055013056],
                    [0.0, 678.2903122373327, 280.39271414461007],
                    [0.0, 0.0, 1.0],
                ],
                "distortion_coef": [
                    [
                        0.04194078685957363,
                        -0.007168281261102275,
                        -0.009100180545490017,
                        0.004533057678646769,
                        -0.17059294063428096,
                    ]
                ],
                "rotation": 0,
                "id": 2,
                "name": "Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.1.1):",
                "width": 800,
                "height": 600,
                "connected": False,
                "calibrated": False,
                "added": True,
            },
        ]

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        calibrate_menu = menubar.addMenu("calibration")
        # copy_menu = menubar.addMenu("copy")
        # todo add shortcuts?
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        save_as_action = QAction("Save &as", self)
        save_as_action.triggered.connect(self.file.save_as)
        file_menu.addAction(save_as_action)

        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.file.saveFile)
        file_menu.addAction(save_action)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save File")

        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.file.openFile)
        file_menu.addAction(open_action)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open File")

        self.calibrate_scratch_action = QAction("calibrate from scratch", self)
        # self.calibGui = calibrationWidget.calibrate_widget(self)
        self.calibrate_scratch_action.triggered.connect(self.calib_scratch)
        calibrate_menu.addAction(self.calibrate_scratch_action)
        # self.calibrate_scratch_action.setShortcut("Ctrl+O")
        self.calibrate_scratch_action.setStatusTip(
            "Calibrate a system from scratch, ignores all previous configurations"
        )

        self.calibrate_single_action = QAction("calibrate single camera", self)
        # self.calibGui = CalibrateGUI
        self.calibrate_single_action.triggered.connect(self.calib_single)
        calibrate_menu.addAction(self.calibrate_single_action)
        # self.calibrate_single_action.setShortcut("Ctrl+O")
        self.calibrate_single_action.setStatusTip("calibrate one camera")

        self.copy_calibration_action = QAction("copy calibration", self)
        # self.calibGui = CalibrateGUI
        self.copy_calibration_action.triggered.connect(self.calib_copy)
        calibrate_menu.addAction(self.copy_calibration_action)
        # self.copy_calibration_action.setShortcut("Ctrl+O")
        self.copy_calibration_action.setStatusTip(
            "copies calibration from one camera to another"
        )

        self.setWindowTitle("Camera calibration")
        self.setGeometry(300, 300, 400, 300)
        # Apply a VS Code-like style using QSS
        with open("computer_code/api/style.css") as style:
            self.styleText = style.read()
            self.setStyleSheet(self.styleText)
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.setup()

    def calib_scratch(self):
        # todo ask to save when settings are un modified
        calibrate_widget_instance = calibrationWidget.CalibrateWidget(self)
        self.central_widget.addWidget(calibrate_widget_instance)
        self.central_widget.setCurrentWidget(calibrate_widget_instance)
        calibrate_widget_instance.show_scratch()

    def calib_single(self):
        # todo ask to save when settings are un modified
        calibrate_widget_instance = calibrationWidget.calibrate_widget(self)
        self.central_widget.addWidget(calibrate_widget_instance)
        self.central_widget.setCurrentWidget(calibrate_widget_instance)
        calibrate_widget_instance.single_ui()

    def calib_copy(self):
        # todo ask to save when settings are un modified
        calibrate_widget_instance = calibrationWidget.calibrate_widget(self)
        self.central_widget.addWidget(calibrate_widget_instance)
        self.central_widget.setCurrentWidget(calibrate_widget_instance)
        # calibrate_widget_instance.copy()

    def setup(self):
        self.setup_widget = setup_window(self)
        self.central_widget.addWidget(self.setup_widget)
        self.central_widget.setCurrentWidget(self.setup_widget)
        self.setup_widget.update_list()

    def updates_config(self, camera_params, camera_poses, to_world_coords_matrix):
        """_summary_ gets updated config data from file_mech  and updates the backend

        Args:
            camera_params (_type_): _description_
            camera_poses (_type_): _description_
            to_world_coords_matrix (_type_): _description_
        """
        # TODO find way to have list update when open new file in calib view

        self.camera_params = camera_params
        self.setup_widget.data = camera_params
        self.camera_poses = camera_poses
        self.to_world_coords_matrix = to_world_coords_matrix
        self.setup_widget.update_list()


class setup_window(QWidget):
    def __init__(self, parent=None):
        super(setup_window, self).__init__(parent)
        # self.list_of_rotations = ["0","90", "180", "270"]

        self.camera_thread = cameraThread.MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
        self.data = (
            parent.data
        )  # Access parent's data list directly; modifications here affect parent
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

        self.settings_ui()

        self.webcam_settings_layout.addLayout(self.editable_fields_layout)

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

    def settings_ui(self):
        self.editable_fields_layout = QGridLayout()
        self.editable_fields_layout.setColumnStretch(0, 0)
        self.editable_fields_layout.setColumnStretch(1, 1)
        self.editable_fields_layout.setHorizontalSpacing(10)
        self.editable_fields_layout.setVerticalSpacing(5)
        self.editable_fields_layout.setAlignment(Qt.AlignTop)
        self.editable_fields_layout.setSizeConstraint(QGridLayout.SetMinAndMaxSize)
        self.editable_fields_layout.setContentsMargins(0, 0, 0, 0)
        self.editable_fields_layout.setSpacing(8)
        self.editable_fields_layout.setColumnMinimumWidth(1, 120)

        # Connect selection changes to update_labels but only when camera stream not running
        def selection_update_labels():
            if not self.camera_thread._running:
                self.update_labels()

        self.added_webcam_list.itemSelectionChanged.connect(selection_update_labels)
        # self.non_added_webcam_list.itemSelectionChanged.connect(self.update_labels)

        row = 0
        self.camera_data = {}
        # list of keys for camera settings
        self.list_camera_data = ["intrinsic_matrix", "distortion_coef"]
        for key in self.list_camera_data:
            self.camera_data[key] = QLabel("lll")
            self.camera_data[key].setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.editable_fields_layout.addWidget(QLabel(key), row, 0)
            self.editable_fields_layout.addWidget(self.camera_data[key], row, 1)
            row += 1

        # edit rotation
        self.list_of_rotations = ["0", "90", "180", "270"]
        self.rot_combo = QComboBox(self)
        self.rot_combo.setEditable(True)
        for i, rot in enumerate(self.list_of_rotations):
            self.rot_combo.addItem(rot, i)

        def change_rot(i):
            data = self.data[self.get_index()]
            value = self.sender().itemData(i)
            data["rotation"] = value
            self.camera_thread.set_rotation(value)
            print(self.data)

        self.rot_combo.currentIndexChanged.connect(change_rot)
        self.editable_fields_layout.addWidget(QLabel("rotation"), row, 0)
        self.editable_fields_layout.addWidget(self.rot_combo, row, 1)
        row += 1

        # edit id
        def change_id():
            data = self.data[self.get_index()]
            value = self.sender().text()
            data["id"] = value
            print(self.data)

        self.line_edit_id = QLineEdit(self)
        self.line_edit_id.setValidator(QIntValidator(1, 2147483647, self))
        self.line_edit_id.editingFinished.connect(change_id)
        self.editable_fields_layout.addWidget(QLabel("id"), row, 0)
        self.editable_fields_layout.addWidget(self.line_edit_id, row, 1)
        row += 1

        # # edit width and height

        self.res_combo = QComboBox(self)
        self.res_combo.setEditable(True)

        def change_resolution(i):
            # access the resolution selection list that called this function
            value = self.sender().itemData(i)
            if value != None:
                self.camera_thread.set_resolution(value[0], value[1])
                idx = self.get_index()
                self.data[idx]["width"] = int(value[0])
                self.data[idx]["height"] = int(value[1])
                print(self.data[idx])
            # self.parent = self.data

        self.res_combo.currentIndexChanged.connect(change_resolution)
        self.editable_fields_layout.addWidget(QLabel("resolution"), row, 0)
        self.editable_fields_layout.addWidget(self.res_combo, row, 1)
        row += 1
        self.webcam_settings_layout.addLayout(self.editable_fields_layout)

        # exposure
        def change_exposure(i):
            self.camera_thread.set_exposure(i)
            idx = self.get_index()
            self.data[idx]["exposure"] = int(i)
            print(self.data[idx])

        self.exposure_slider = QSlider(Qt.Horizontal)

        self.exposure_slider.setFixedHeight(20)
        self.exposure_slider.valueChanged.connect(change_exposure)

        self.gain_slider = QSlider(Qt.Horizontal)

        def change_gain(i):
            self.camera_thread.set_gain(i)
            idx = self.get_index()
            self.data[idx]["gain"] = int(i)
            print(self.data[idx])

        self.gain_slider.setMinimum(0)
        self.gain_slider.setMaximum(100)
        self.gain_slider.setValue(0)
        self.gain_slider.setFixedHeight(30)
        self.gain_slider.valueChanged.connect(change_gain)

        settings = QGridLayout()
        settings.addWidget(QLabel("Exposure"), 0, 0)
        settings.addWidget(self.exposure_slider, 0, 1)
        settings.addWidget(QLabel("Gain"), 1, 0)
        settings.addWidget(self.gain_slider, 1, 1)
        self.webcam_settings_layout.addLayout(settings)

    def update_labels(self):
        data = self.data[self.get_index()]
        # camera data
        for key in self.list_camera_data:
            self.camera_data[key].setText(f"{str(data[key])}")
        # rotation
        self.rot_combo.setCurrentText(self.list_of_rotations[data["rotation"]])
        # id
        self.line_edit_id.setText(str(data["id"]))
        # resolution
        # Suppress signals while updating res_combo to avoid triggering change_resolution
        self.res_combo.blockSignals(True)
        # remove items so more can be added
        self.res_combo.clear()
        current_res_index = 0
        resolutions = videoSubSystem.getResolution(
            videoSubSystem.get_id_from_name(data["name"])
        )
        for i, resolution in enumerate(resolutions):
            self.res_combo.addItem(
                str(resolution[0]) + "x" + str(resolution[1]), resolution
            )
            if resolution[0] == data.get("width") and resolution[1] == data.get(
                "height"
            ):
                current_res_index = i

        # Set current selection of res_combo to match data["width"] and data["height"]
        self.res_combo.setCurrentIndex(current_res_index)
        self.res_combo.blockSignals(False)
        # exposure and gain
        self.exposure_slider.setMinimum(data.get("min_exposure", 0))
        self.exposure_slider.setMaximum(data.get("max_exposure", 100))
        self.exposure_slider.setValue(int(data.get("exposure", 100)))
        self.gain_slider.setValue(int(data.get("gain", 100)))

    def remove_webcam(self):
        selected_items = self.added_webcam_list.selectedItems()
        for item in selected_items:
            self.added_webcam_list.takeItem(self.added_webcam_list.row(item))
            self.non_added_webcam_list.addItem(item)
            self.data[item.data(Qt.UserRole)]["added"] = False

    def add_webcam(self):
        selected_items = self.non_added_webcam_list.selectedItems()
        for item in selected_items:
            self.non_added_webcam_list.takeItem(self.non_added_webcam_list.row(item))
            self.added_webcam_list.addItem(item)
            self.data[item.data(Qt.UserRole)]["added"] = True

    def update_list(self):
        self.added_webcam_list.clear()
        self.non_added_webcam_list.clear()
        for index, webcam in enumerate(self.data):
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

        attached_webcams = videoSubSystem.listWebcams()
        # TODO find better way of doing this
        for current_webcams in self.data:
            for attached_webcam in attached_webcams:
                if not any(cam["name"] == attached_webcam[0] for cam in self.data):
                    cam_id = videoSubSystem.get_id_from_name(attached_webcam[0])
                    res = videoSubSystem.getResolution(cam_id)[0]
                    settings = videoSubSystem.getSettings(cam_id)

                    self.data.append(
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

        name = self.data[self.get_index()]["name"]
        if not name:
            return
        camera_id = int(videoSubSystem.get_id_from_name(name))
        if (camera_id) == -1:
            print("stop")
            alert = alert_widget(
                "this camera could not be accessed", "ok", "", style=self.styleSheet()
            )
            alert.exec()
            return

        print(camera_id)
        self.camera_thread.set_camera_id(camera_id)

        self.camera_thread.start()
        self.update_labels()


class alert_widget(QDialog):
    def __init__(
        self, msg, accept_msg="ok", reject_msg="cancel", style=None, parent=None
    ):
        super(alert_widget, self).__init__(parent)
        if style:
            self.setStyleSheet(style)

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.button(QDialogButtonBox.Ok).setText(accept_msg)
        if reject_msg != "":
            QBtn = QBtn | QDialogButtonBox.Cancel
            self.buttonBox.rejected.connect(self.reject)
            self.buttonBox.button(QDialogButtonBox.cancel).setText(reject_msg)

        layout = QVBoxLayout()
        message = QLabel(msg)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def accept(self):
        return super().accept()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    # TODO have to find a way to reallocate a camera that moved to a different port with its original calibration settings ex move camera to new usb port and hit reload now have two webcams one without settings
