from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QGridLayout,
    QSlider,
    QSplitter,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot as Slot
from computer_code.api.cameraThread import Thread
from  computer_code.Ui.ViewportLabel import Label
import computer_code.Ui.settingsWidget as settingsWidget
import computer_code.Ui.alertWidget as alertWidget, computer_code.api.videoSubSystem as videoSubSystem
from computer_code.api.cameras import Cameras
# TODO have singleton for camera with a current camera param that stores current camera setting and 
# todo maybe also have this be singleton for setup data with a param for if it has been modified since saving 
class CalibrateWidget(QWidget):
    def __init__(self, parent=None):
        super(CalibrateWidget, self).__init__(parent)
        self.parent = parent
        self.cameras = Cameras.instance()
        self.index = 0
        self.min_num_captures = 9
        
        self.has_enough_captures = False
        self.on_last_camera=False
        # Camera thread setup
        self.camera_thread = Thread.instance()

        self.camera_thread.frame_signal.connect(self.setImage)
        self.camera_thread.set_find_chessboard(True)


        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Current camera label
        # self.label = Label()
        # self.label.setMinimumSize(800, 600)

        # self.label = QLabel()
        # self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # self.main_layout.addWidget(self.label)

        # Webcam settings widget and layout
        self.webcam_settings_layout = QVBoxLayout()
        self.webcam_settings_widget = QWidget()
        self.webcam_settings_widget.setMinimumWidth(300)
        self.webcam_settings_widget.setMaximumWidth(500)
        self.webcam_settings_widget.setLayout(self.webcam_settings_layout)

        # Settings UI
        self.settings_ui = settingsWidget.SettingsWidget(self)
        self.webcam_settings_layout.addWidget(self.settings_ui)

        self.back_btn = QPushButton("go back", clicked=self.go_back)
        self.webcam_settings_layout.addWidget(self.back_btn)

        # Splitter for settings and preview
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.webcam_settings_widget)

        # Preview and capture settings layout
        self.preview_capture_settings_layout = QVBoxLayout()
        self.label = Label()
        # self.label.setAlignment(Qt.AlignRight)
        self.label.setMinimumSize(800, 600)
        self.preview_capture_settings_layout.addWidget(self.label)

        # Capture settings grid
        self.capture_settings_layout = QGridLayout()
        self.preview_capture_settings_layout.addLayout(self.capture_settings_layout)

        self.next_finish_btn = QPushButton()
        self.next_finish_btn.clicked.connect(self._next_camera)
        self.capture_settings_layout.addWidget(self.next_finish_btn,0,3)

        self.progress_label = QLabel()
        self.capture_settings_layout.addWidget(self.progress_label,1,3)



        # Wrap preview/capture layout in a widget for splitter
        prev_capt_to_widget = QWidget()
        prev_capt_to_widget.setLayout(self.preview_capture_settings_layout)
        splitter.addWidget(prev_capt_to_widget)
        splitter.setSizes([200, 400])

        # Add splitter to main layout
        splitter_to_layout = QHBoxLayout()
        splitter_to_layout.addWidget(splitter)
        self.main_layout.addLayout(splitter_to_layout)

        # --- Capture Controls ---

        # Capture button
        self.capture_btn = QPushButton("capture")
        self.capture_btn.clicked.connect(self._capture_toggle)
        self.capture_settings_layout.addWidget(self.capture_btn, 0, 0)

        # Sensitivity slider and label
        self.sensitivity_label = QLabel()
        self.capture_settings_layout.addWidget(self.sensitivity_label, 0, 1)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(1)
        self.sensitivity_slider.setMaximum(1000)
        self.sensitivity_slider.valueChanged.connect(self._set_sensitivity)
        self.sensitivity_slider.setValue(500)
        self.capture_settings_layout.addWidget(self.sensitivity_slider, 0, 2)

        # Auto capture button
        self.auto_btn = QPushButton("auto capture")
        self.auto_btn.clicked.connect(self._auto_capture_toggle)
        self.capture_settings_layout.addWidget(self.auto_btn, 1, 0)

        # Timer slider and label
        self.timer_label = QLabel()
        self.capture_settings_layout.addWidget(self.timer_label, 1, 1)
        self.timer_slider = QSlider(Qt.Horizontal)
        self.timer_slider.setMinimum(1)
        self.timer_slider.setMaximum(100)
        self.timer_slider.valueChanged.connect(self._set_auto_timer)
        self.capture_settings_layout.addWidget(self.timer_slider, 1, 2)
        self._set_auto_timer(20)  # Set default timer

        # Initialize labels and states
        self.update_labels()

    # --- Helper Methods for UI Callbacks ---
    def _next_camera(self):
        
        if not self.on_last_camera:
            self.index+=1
            self.camera_thread.calc_calib()
            self.camera_thread.set_camera_id(self.get_index())
            self.camera_thread.start()
        else:
            self.camera_thread.calc_calib()
            self._finish_calibration()

        self.camera_thread.clearData() 
        self.update_labels()
           

    def _finish_calibration(self):
        
        
        self.parent.show_setup()
        # self.parent.update_labels()
    def _capture_toggle(self):
        self.camera_thread.take_capture_state = not self.camera_thread.take_capture_state
        self.update_labels()

    def _set_sensitivity(self, val):
        outMin, outMax = 0.001, 0.02
        new_val = outMin + (float(val - self.sensitivity_slider.minimum()) /
                            float(self.sensitivity_slider.maximum() - self.sensitivity_slider.minimum()) *
                            (outMax - outMin))
        self.camera_thread.sensitivity = new_val
        self.sensitivity_label.setText(f"sensitivity {val:8.0f}")

    def _auto_capture_toggle(self):
        self.camera_thread.auto_capture_state = not self.camera_thread.auto_capture_state
        self.update_labels()

    def _set_auto_timer(self, val):
        seconds = (val / 10) + 1
        self.camera_thread.auto_time = seconds
        self.timer_label.setText(f"auto capture {seconds:8.1f} seconds")

        # self.setCentralWidget(central_widget)

    # Function to update editable fields when selection changes
    def update_labels(self):
        # todo not updating when change id number
    
        self.on_last_camera = self.index >= len(self.cameras.added_cameras)-1
        
        
        self.has_enough_captures = (self.min_num_captures <= len(self.camera_thread.imgpoints))
      
        if self.get_index() != -1:
            cam = self.cameras.camera_params[self.get_index()]
            self.label.setText(f"current camera: {cam['name']} id {cam['id']}")
        else:
            self.label.setText("current camera: None")

        self.capture_btn.setEnabled(self.camera_thread._running and not self.camera_thread.auto_capture_state)
        self.sensitivity_slider.setEnabled(self.camera_thread._running )
        auto = self.camera_thread._running 
        self.auto_btn.setEnabled(auto)
        self.timer_slider.setEnabled(auto)

        # enough_captures = len(self.camera_thread.objpoints) >= self.min_num_captures
        self.next_finish_btn.setEnabled(self.has_enough_captures)
        if self.get_index() != -1:
            idx = self.get_index()
            if not self.on_last_camera:
                cam = self.cameras.camera_params[idx]
                self.next_finish_btn.setText(f"next camera id: {cam['id']}")
            else:
                self.next_finish_btn.setText(f"finish calibration")

        self.progress_label.setText(f"captures left {len(self.camera_thread.imgpoints)}/{self.min_num_captures}")
        self.settings_ui.update_labels()

        

   
    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
    

    def go_back(self):
        alert = alertWidget.alert_widget(
                "are you sure you want to leave calibration ", "yes", "no", style=self.styleSheet(),
                title="exit before finishing?")
        alert.exec()
        
        if alert.result() == alert.Accepted:
            self.parent.show_setup()

    def get_index(self):
        if self.index >= len(self.cameras.added_cameras):
            return -1
        return self.cameras.added_cameras[self.index]
    
    def open_camera(self):
        
        if len(self.cameras.camera_params) == 0:
            return
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
        print("camera_id",camera_id)
        self.camera_thread.set_camera_id(self.get_index())
        self.camera_thread.start()
        # self.update_labels()
        self.settings_ui.update_labels()
        self.update_labels()