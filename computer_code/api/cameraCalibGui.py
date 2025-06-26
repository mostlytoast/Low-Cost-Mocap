import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,

    QAction,

    QStackedWidget,

)

from helpers import Cameras
import file_mech
import numpy as np

# import sys

import alertWidget
import calibrationWidget
import setupWidget

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.file = file_mech.file_dialog(self)
        self.cameras = Cameras.instance()
        self.save_path = ""
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        self.initUI()
        
        

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
        self.calibrate_scratch_action.triggered.connect(self.calib_scratch)
        calibrate_menu.addAction(self.calibrate_scratch_action)
        # self.calibrate_scratch_action.setShortcut("Ctrl+O")
        self.calibrate_scratch_action.setStatusTip(
            "Calibrate a system from scratch, ignores all previous configurations"
        )

        self.calibrate_single_action = QAction("calibrate single camera", self)
        self.calibrate_single_action.triggered.connect(self.calib_single)
        calibrate_menu.addAction(self.calibrate_single_action)
        # self.calibrate_single_action.setShortcut("Ctrl+O")
        self.calibrate_single_action.setStatusTip("calibrate one camera")

        self.copy_calibration_action = QAction("copy calibration", self)
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
        self.calibrate_widget_instance = calibrationWidget.CalibrateWidget(self)
        # todo singleton for camera data 
        self.setup_widget = setupWidget.setup_window(self)
        self.stacked_widget.addWidget(self.calibrate_widget_instance)

        self.stacked_widget.addWidget(self.setup_widget)
        self.stacked_widget.setCurrentWidget(self.setup_widget)
        self.setup_widget.update_list()
    def check_for_webcams(self):
        """make sure that we have cameras to use for calib otherwise give error popup and return false"""
        if len(self.cameras.added_cameras) == 0:
            alert = alertWidget.alert_widget(
                "you need to add cameras to the 'added cameras list' before you can start calibration", "ok", "", style=self.styleSheet()
                )
            alert.exec()
            return False
        return True
            

    def calib_scratch(self):
        if self.check_for_webcams():
            # # todo ask to save when settings are un modified
            self.stacked_widget.setCurrentIndex(0)
            self.setup_widget.camera_thread.stop()
            # self.stacked_widget.setCurrentWidget(self.calibrate_widget_instance)
            # self.calibrate_widget_instance.show_scratch()
            print()

    def calib_single(self):
        # todo ask to save when settings are un modified
        # calibrate_widget_instance = calibrationWidget.calibrate_widget(self)
        # self.stacked_widget.addWidget(calibrate_widget_instance)
        # self.stacked_widget.setCurrentWidget(calibrate_widget_instance)
        # calibrate_widget_instance.single_ui()
        print()


    def calib_copy(self):
        # todo ask to save when settings are un modified
        # calibrate_widget_instance = calibrationWidget.calibrate_widget(self)
        # self.stacked_widget.addWidget(calibrate_widget_instance)
        # self.stacked_widget.setCurrentWidget(calibrate_widget_instance)
        print()
    
        # calibrate_widget_instance.copy()

    def show_setup(self):
        self.calibrate_widget_instance.camera_thread.stop()
        self.stacked_widget.setCurrentIndex(1)
        
        

    def updates_config(self, camera_params, camera_poses, to_world_coords_matrix):
        """_summary_ gets updated config data from file_mech  and updates the backend

        Args:
            camera_params (_type_): _description_
            camera_poses (_type_): _description_
            to_world_coords_matrix (_type_): _description_
        """
        # TODO find way to have list update when open new file in calib view

        self.cameras.camera_params = camera_params
        # self.setup_widget.data = camera_params
        self.cameras.camera_poses = camera_poses
        self.cameras.to_world_coords_matrix = to_world_coords_matrix
        self.setup_widget.update_list()





if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
    # TODO have to find a way to reallocate a camera that moved to a different port with its original calibration settings ex move camera to new usb port and hit reload now have two webcams one without settings
