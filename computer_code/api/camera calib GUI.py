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
    QDialogButtonBox,
)
from PyQt5.QtGui import QKeySequence, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot as Slot

# import sys
import cameraThread
import videoSubSystem
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMessageBox

import calibrationWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # super(MainWindow, self).__init__(parent)
        # self.central_widget = QStackedWidget()
        # self.data=[]
        # self.setCentralWidget(self.central_widget)
        # login_widget = setup_window(self)
        # # login_widget.button.clicked.connect(self.login)
        # self.central_widget.addWidget(login_widget)

        self.setWindowTitle("Camera Setup")

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

        save_as_action = QAction("save as", self)
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)

        save_action = QAction("save", self)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save File")

        open_action = QAction("open", self)
        open_action.triggered.connect(self.open)
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
        calibrate_widget_instance = calibrationWidget.calibrate_widget(self)
        self.central_widget.addWidget(calibrate_widget_instance)
        self.central_widget.setCurrentWidget(calibrate_widget_instance)
        calibrate_widget_instance.scratch_ui()

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
        setup_widget = setup_window(self)
        self.central_widget.addWidget(setup_widget)
        self.central_widget.setCurrentWidget(setup_widget)

    def save(self):
        if self.save_path == "":

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", "", "Json Files (*.json);;All Files (*.*)"
            )
            if file_path and not file_path.lower().endswith(".json"):
                file_path += ".json"
            if file_path:
                print(f"Selected file: {file_path}")
                self.save_path = file_path
        # double check
        if self.save_path != "":
            try:
                with open(self.save_path, "w") as f:
                    json.dump(self.data, f, indent=4)
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Can't save file: {e}")

                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                self.save_path = ""  # delete path so can save new files in future

    def save_as(self):
        self.save_path = ""
        self.save()

    def open(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Json Files (*.json);;All Files (*.*)"
        )
        if file_path:
            print(f"Selected file: {file_path}")
            self.save_path = file_path
        # double check
        if self.save_path != "":
            try:
                with open(self.save_path, "r") as f:
                    self.data = json.load(f)
                    self.update_list()  # update list with new data
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Can't read file: {e}")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        self.save_path = ""  # delete path so can open new files in future


class setup_window(QWidget):
    def __init__(self, parent=None):
        super(setup_window, self).__init__(parent)

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
        # Create a vertical layout for the edit button and label
        # self.edit_layout = QVBoxLayout()
        # self.edit_button = QPushButton("edit")
        # self.edit_button.setEnabled(False)  # Initially greyed out
        # self.edit_button.clicked.connect(self.add_webcam)

        # self.edit_layout.addWidget(self.edit_button)
        # self.move_buttons_layout.addLayout(self.edit_layout)

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

        # # Enable the discover button only when an item is selected in either list
        # self.added_webcam_list.itemSelectionChanged.connect(
        #     lambda: self.edit_button.setEnabled(
        #         bool(self.added_webcam_list.selectedItems())
        #         or bool(self.non_added_webcam_list.selectedItems())
        #     )
        # )
        # self.non_added_webcam_list.itemSelectionChanged.connect(
        #     lambda: self.edit_button.setEnabled(
        #         bool(self.added_webcam_list.selectedItems())
        #         or bool(self.non_added_webcam_list.selectedItems())
        #     )
        # )

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
        self.webcam_settings_widget.setMinimumWidth(200)  # Minimum width
        self.webcam_settings_widget.setMaximumWidth(400)  # Optional: Maximum width

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

    def on_data_change(self, idx, key, value):
        try:

            self.data[idx][key] = value
            print(self.data[idx])
            # self.editable_labels["rotation"].setText(f"rotation: {value}")
        except ValueError:
            pass  # Ignore invalid input

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

        # Connect selection changes to update_settings_ui
        self.added_webcam_list.itemSelectionChanged.connect(self.update_settings_ui)
        # self.non_added_webcam_list.itemSelectionChanged.connect(self.update_settings_ui)

        # Initial population
        self.update_settings_ui()
        # Dropdown to edit a variable (e.g., "rotation" of the first webcam)

    def update_settings_ui(self):
        # Remove all widgets from the layout
        while self.editable_fields_layout.count():
            item = self.editable_fields_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        # self.editable_labels.clear()

        # Determine which list and item is selected
        selected_item = None
        if self.added_webcam_list.selectedItems():
            selected_item = self.added_webcam_list.selectedItems()[0]
        elif self.non_added_webcam_list.selectedItems():
            selected_item = self.non_added_webcam_list.selectedItems()[0]
        self.idx = 0
        data = {}
        if not selected_item:
            # show when there is no camera selected
            data = {
                "intrinsic_matrix": [
                    [0.0, 0.0, 0.0],
                    [
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [0.0, 0.0, 1.0],
                ],
                "distortion_coef": [[0.0, 0.0, 0.0, 0.0, 0.0]],
                "rotation": 0,
                "id": 0,
                "name": "",
                "width": 0,
                "height": 0,
            }
        else:
            self.idx = selected_item.data(Qt.UserRole)
            data = self.data[self.idx]

        # list non editable settings
        key = "intrinsic_matrix"
        row = 0
        for key in ["intrinsic_matrix", "distortion_coef", "name"]:
            label = QLabel(f"{str(data[key])}")
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self.editable_fields_layout.addWidget(QLabel(key), row, 0)
            self.editable_fields_layout.addWidget(label, row, 1)
            row += 1
            # self.editable_labels[key] = label

        # edit rotation
        self.combobox_rotation = QComboBox(self)
        self.combobox_rotation.setEditable(True)

        self.combobox_rotation.addItem("0", 0)
        self.combobox_rotation.addItem("90", 1)
        self.combobox_rotation.addItem("180", 2)
        self.combobox_rotation.addItem("270", 3)
        self.combobox_rotation.setCurrentText(str(data["rotation"]))

        self.combobox_rotation.currentIndexChanged.connect(
            lambda i, key="rotation": self.on_data_change(
                self.idx, key, self.combobox_rotation.itemData(i)
            )
        )
        self.editable_fields_layout.addWidget(QLabel("rotation"), row, 0)
        self.editable_fields_layout.addWidget(self.combobox_rotation, row, 1)
        row += 1
        # edit id
        self.line_edit_id = QLineEdit(self)
        self.line_edit_id.setValidator(QIntValidator(1, 2147483647, self))
        self.line_edit_id.setText(str(data["id"]))
        self.line_edit_id.editingFinished.connect(
            lambda idx=self.idx, key="id": self.on_data_change(
                idx, key, int(self.line_edit_id.text())
            )
        )
        self.editable_fields_layout.addWidget(QLabel("id"), row, 0)

        self.editable_fields_layout.addWidget(self.line_edit_id, row, 1)
        row += 1

        # edit width and height

        self.combobox_resolution = QComboBox(self)
        self.combobox_resolution.setEditable(True)
        if data.get("connected", False):

            for resolution in videoSubSystem.getResolution(
                videoSubSystem.get_id_from_name(data["name"])
            ):
                self.combobox_resolution.addItem(
                    str(resolution[0]) + "x" + str(resolution[1]), resolution
                )
                # item = self.combobox_resolution.item(self.combobox_resolution.count() - 1)
                # item.setData(Qt.UserRole, resolution)

        self.combobox_resolution.setCurrentText(
            str(data["width"]) + "x" + str(data["height"])
        )

        self.combobox_resolution.currentIndexChanged.connect(
            lambda i, key="width": self.on_data_change(
                self.idx, key, self.combobox_resolution.itemData(i)[0]
            )
        )
        self.combobox_resolution.currentIndexChanged.connect(
            lambda i, key="height": self.on_data_change(
                self.idx, key, self.combobox_resolution.itemData(i)[1]
            )
        )
        self.editable_fields_layout.addWidget(QLabel("resolution"), row, 0)

        self.editable_fields_layout.addWidget(self.combobox_resolution, row, 1)
        row += 1

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
                if webcam["added"]
                else self.non_added_webcam_list
            )
            target_list.addItem(webcam["name"])
            item = target_list.item(target_list.count() - 1)
            if not webcam["calibrated"]:
                item.setForeground(Qt.gray)
                item.setToolTip("not calibrated")
            if not webcam["connected"]:
                item.setForeground(Qt.red)
                item.setToolTip("not connected")
            item.setData(Qt.UserRole, index)

    def reload_cameras(self):
        """_summary_ reloads the list of cameras connected to the system"""

        # TODO have to find way of adding newly added cameras in system to list

        attached_webcams = videoSubSystem.listWebcams()
        # TODO find better way of doing this
        for current_webcams in self.data:
            for attached_webcam in attached_webcams:
                if not any(cam["name"] == attached_webcam[0] for cam in self.data):
                    res = videoSubSystem.getResolution(
                        videoSubSystem.get_id_from_name(attached_webcam[0])
                    )[0]
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
        item = self.added_webcam_list.currentItem()
        if not item:
            return

        name = self.data[item.data(Qt.UserRole)]["name"]
        if not name:
            return
        camera_id = int(videoSubSystem.get_id_from_name(name))
        if (camera_id) == -1:
            print("stop")
            alert = alert_widget(
                "this camera could not be accessed", "ok", "", style=self.styleSheet()
            )
            # alert.setStyleSheet(self.parent().styleSheet() if self.parent() else self.styleSheet())

            alert.exec()

            return

        print(camera_id)
        self.camera_thread.set_camera_id(camera_id)

        self.camera_thread.start()


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
    app.exec_()
    # TODO have to find a way to reallocate a camera that moved to a different port with its original calibration settings ex move camera to new usb port and hit reload now have two webcams one without settings
