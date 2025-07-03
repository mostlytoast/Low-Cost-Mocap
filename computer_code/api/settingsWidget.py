
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QGridLayout,
 
    QSlider,
)

from PyQt5.QtCore import Qt
from helpers import Cameras


# import sys

import videoSubSystem
from PyQt5.QtGui import QIntValidator


class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)
        self.parent = parent
        self.cameras= Cameras.instance()
        self.layout = QVBoxLayout()
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
        
        # self.non_added_webcam_list.itemSelectionChanged.connect(self.update_labels)

        row = 0
        self.camera_data = {}
        # list of keys for camera settings
        self.list_camera_data = ["intrinsic_matrix", "distortion_coef"]
        for key in self.list_camera_data:
            self.camera_data[key] = QLabel("[]")
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
            cameras = Cameras.instance()
            idx = self.parent.get_index()
            data = self.cameras.camera_params[idx]
            value = self.sender().itemData(i)
            data["rotation"] = value
            cameras.set_rotation(idx,value)
            print(self.cameras.camera_params[idx])

        self.rot_combo.currentIndexChanged.connect(change_rot)
        self.editable_fields_layout.addWidget(QLabel("rotation"), row, 0)
        self.editable_fields_layout.addWidget(self.rot_combo, row, 1)
        row += 1

        # edit id
        def change_id():
            idx = self.parent.get_index()

            cameras = Cameras.instance()
            data = cameras.camera_params[idx]
            value = self.sender().text()
            data["id"] = value
            print(cameras.camera_params[idx])

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
            cameras = Cameras.instance()
            # access the resolution selection list that called this function
            value = self.sender().itemData(i)
            if value != None:
                idx = self.parent.get_index()
                cameras.set_resolution(idx,value[0], value[1])
                # self.cameras.camera_params[idx]["width"] = int(value[0])
                # self.cameras.camera_params[idx]["height"] = int(value[1])
                print(self.cameras.camera_params[idx])
            # self.parent = self.cameras.camera_params

        self.res_combo.currentIndexChanged.connect(change_resolution)
        self.editable_fields_layout.addWidget(QLabel("resolution"), row, 0)
        self.editable_fields_layout.addWidget(self.res_combo, row, 1)
        row += 1
        
        
        # self.exposure_gain_settings.setAlignment(Qt.AlignRight | Qt.AlignVCenter) 
        # self.editable_fields_layout.addWidget(self.exposure_gain_settings)
        self.layout.addLayout(self.editable_fields_layout)

        self.exposure_gain_settings = ExposureGainSettings(self)

        self.layout.addWidget(self.exposure_gain_settings, alignment=Qt.AlignTop )
        self.setLayout(self.layout)
    def get_index(self):
        return self.parent.get_index()
    def update_labels(self):
        self.exposure_gain_settings.update_labels()
        has_camera =self.parent.get_index() != -1

        self.rot_combo.setEnabled(has_camera)
        self.line_edit_id.setEnabled(has_camera)
        self.res_combo.setEnabled(has_camera)
        
        if not has_camera:
            return 
        data = self.cameras.camera_params[self.parent.get_index()]
        print("update settings", data)
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
            print(resolution)
            if resolution[0] == data.get("width") and resolution[1] == data.get(
                "height"
            ):
                current_res_index = i

        # Set current selection of res_combo to match data["width"] and data["height"]
        self.res_combo.setCurrentIndex(current_res_index)
        self.res_combo.blockSignals(False)
        

class ExposureGainSettings(QWidget):
    def __init__(self, parent=None):
        super(ExposureGainSettings, self).__init__(parent)
        self.parent = parent
        self.cameras= Cameras.instance()
        self.layout = QVBoxLayout()

        # exposure
        def change_exposure(i):
            cameras = Cameras.instance()
            idx = self.parent.get_index()
            
            cameras.set_exposure(idx,i)
            print(self.cameras.camera_params[idx])

        self.exposure_slider = QSlider(Qt.Horizontal)

        self.exposure_slider.setFixedHeight(20)
        self.exposure_slider.valueChanged.connect(change_exposure)

        self.gain_slider = QSlider(Qt.Horizontal)

        def change_gain(i):
            cameras = Cameras.instance()

            idx = self.parent.get_index()
            cameras.set_gain(idx,i)
            
            self.cameras.camera_params[idx]["gain"] = int(i)
            print(self.cameras.camera_params[idx])

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
        # self.layout.addLayout(self.editable_fields_layout)
        self.layout.addLayout(settings)
        self.setLayout(self.layout)

    def update_labels(self):
        has_camera =self.parent.get_index() != -1
        self.exposure_slider.setEnabled(has_camera)
        self.gain_slider.setEnabled(has_camera)
        if not has_camera:
            return 
        data = self.cameras.camera_params[self.parent.get_index()]
        

        # exposure and gain
        self.exposure_slider.setMinimum(data.get("min_exposure", 0))
        self.exposure_slider.setMaximum(data.get("max_exposure", 100))
        self.exposure_slider.setValue(int(data.get("exposure", 100)))
        self.gain_slider.setValue(int(data.get("gain", 100)))
