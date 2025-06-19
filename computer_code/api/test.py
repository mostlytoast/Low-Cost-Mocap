from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QListWidgetItem,
    QShortcut,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QAction,
    QPushButton,
    QLabel,
)
from PyQt5.QtGui import QKeySequence, QImage, QPixmap
from PyQt5.QtCore import Qt
import cv2
from PyQt5.QtCore import QThread, pyqtSignal as Signal, pyqtSlot as Slot
import imutils
import sys
import videoSubSystem

"""_summary_ separate thread to get video from webcam 

Returns:
    _type_: _description_ signal image 
"""


class MyThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id

    def set_camera_id(self, camera_id):
        self.camera_id = camera_id

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        while self.cap.isOpened():
            _, frame = self.cap.read()
            frame = self.cvimage_to_label(frame)
            self.frame_signal.emit(frame)

    def cvimage_to_label(self, image):
        image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Setup")
        self.camera_thread = MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
        self.initUI()

    def initUI(self):
        self.data = {
            "addedWebcams": {
                "webcam 1": {
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
                },
                "webcam 2": {
                    
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
                    
                }
            },
            "nonAddedWebcams": {
                "webcam 1": {
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
                },
                "webcam 2": {
                    
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
                    
                },
            }
        }
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        save_action = QAction("save", self)
        #   save_action.triggered.connect()
        file_menu.addAction(save_action)

        open_action = QAction("open", self)
        #   open_action.triggered.connect()
        file_menu.addAction(open_action)

        self.setWindowTitle("QMenuBar Example")
        self.setGeometry(300, 300, 400, 300)
        self.main_layout = QVBoxLayout()
        self.webcam_preview_layout = QHBoxLayout()
        self.webcam_list_layout = QHBoxLayout()
        self.move_buttons_layout = QVBoxLayout()

        # added webcams
        self.added_webcam_list = QListWidget()
        # self.added_webcam_list.addItem("0")
        # self.added_webcam_list.addItem("3")
        # self.added_webcam_list.addItem("2")
        self.webcam_list_layout.addWidget(self.added_webcam_list)

        self.add_button = QPushButton("<")
        self.add_button.clicked.connect(self.add_webcam)
        self.move_buttons_layout.addWidget(self.add_button)
        self.setup_button = QPushButton(">")
        self.setup_button.clicked.connect(self.remove_webcam)
        self.move_buttons_layout.addWidget(self.setup_button)
        self.webcam_list_layout.addLayout(self.move_buttons_layout)

        # webcams not added
        self.non_added_webcam_list = QListWidget()
        self.non_added_webcam_list.addItem("webcam 4")
        self.non_added_webcam_list.addItem("webcam 2")
        self.webcam_list_layout.addWidget(self.non_added_webcam_list)
        self.main_layout.addLayout(self.webcam_list_layout)
        # Shortcuts for deleting items in each list
        self.update_list()

        self.delete_shortcut1 = QShortcut(
            QKeySequence(Qt.Key_Delete), self.added_webcam_list
        )
        self.delete_shortcut1.setContext(Qt.WidgetShortcut)
        self.delete_shortcut1.activated.connect(self.remove_webcam)

        self.delete_shortcut2 = QShortcut(
            QKeySequence(Qt.Key_Delete), self.non_added_webcam_list
        )
        self.delete_shortcut2.setContext(Qt.WidgetShortcut)
        self.delete_shortcut2.activated.connect(self.add_webcam)

        self.open_btn = QPushButton("Open The Camera", clicked=self.open_camera)
        self.webcam_preview_layout.addWidget(self.open_btn)
        self.label = QLabel()
        self.webcam_preview_layout.addWidget(self.label)

        self.camera_thread = MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
        self.main_layout.addLayout(self.webcam_preview_layout)
        # Set main_layout on a QWidget and set as central widget
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def remove_webcam(self):
        selected_items = self.added_webcam_list.selectedItems()
        for item in selected_items:
            self.added_webcam_list.takeItem(self.added_webcam_list.row(item))
            self.non_added_webcam_list.addItem(item)

    def add_webcam(self):
        selected_items = self.non_added_webcam_list.selectedItems()
        for item in selected_items:
            self.non_added_webcam_list.takeItem(self.non_added_webcam_list.row(item))
            self.added_webcam_list.addItem(item)

    def save(self):
        RuntimeWarning("not implemented yet")

    def open(self):
        RuntimeWarning("not implemented yet")

    def update_list(self):
        for webcam in self.data["addedWebcams"]:
            self.added_webcam_list.addItem(webcam)
        for webcam in self.data["nonAddedWebcams"]:
            self.non_added_webcam_list.addItem(webcam)

    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def open_camera(self):
        self.camera_thread.set_camera_id(
            videoSubSystem.get_id_from_name(self.data["addedWebcams"][self.added_webcam_list.currentItem().text()]["name"])
        )
        self.camera_thread.start()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
