import sys
import json
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QLineEdit, QTextEdit, QComboBox, QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import socketio

# SocketIO client
sio = socketio.Client()

class MocapMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoCap PyQt")
        self.resize(1600, 900)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Camera Stream
        self.camera_stream_label = QLabel("Camera Stream")
        self.camera_image = QLabel()
        self.camera_image.setFixedHeight(400)
        self.camera_image.setAlignment(Qt.AlignCenter)
        self.start_camera_btn = QPushButton("Start")
        self.start_camera_btn.clicked.connect(self.toggle_camera_stream)
        self.fps_label = QLabel("FPS: 0")

        cam_layout = QHBoxLayout()
        cam_layout.addWidget(self.camera_stream_label)
        cam_layout.addWidget(self.start_camera_btn)
        cam_layout.addWidget(self.fps_label)

        self.layout.addLayout(cam_layout)
        self.layout.addWidget(self.camera_image)

        # Camera Settings
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(0, 1000)
        self.exposure_slider.setValue(100)
        self.exposure_slider.valueChanged.connect(self.update_camera_settings)
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(0, 100)
        self.gain_slider.setValue(0)
        self.gain_slider.valueChanged.connect(self.update_camera_settings)

        settings_layout = QFormLayout()
        settings_layout.addRow("Exposure", self.exposure_slider)
        settings_layout.addRow("Gain", self.gain_slider)
        settings_group = QGroupBox("Camera Settings")
        settings_group.setLayout(settings_layout)
        self.layout.addWidget(settings_group)

        # Add more controls as needed...

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.periodic_update)
        self.timer.start(500)

        # State
        self.camera_stream_running = False

        # Connect to socket
        sio.connect('http://localhost:3001')

        # Socket event handlers
        sio.on('fps', self.on_fps)
        # ...add more handlers

    def toggle_camera_stream(self):
        self.camera_stream_running = not self.camera_stream_running
        self.start_camera_btn.setText("Stop" if self.camera_stream_running else "Start")
        # Start/stop camera stream logic here

    def update_camera_settings(self):
        exposure = self.exposure_slider.value()
        gain = self.gain_slider.value()
        sio.emit("update-camera-settings", {"exposure": exposure, "gain": gain})

    def periodic_update(self):
        # Periodic tasks, e.g., send keepalive, update UI, etc.
        pass

    def on_fps(self, data):
        self.fps_label.setText(f"FPS: {data['fps']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MocapMainWindow()
    window.show()
    sys.exit(app.exec_())