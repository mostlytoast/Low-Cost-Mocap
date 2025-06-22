import sys
# import json
# import requests
import socketio
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QSlider,QGridLayout
)
import cameraThread
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QPixmap, QImage
# TRAJECTORY_PLANNING_TIMESTEP = 0.05
# LAND_Z_HEIGHT = 0.075
# NUM_DRONES = 2

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Low-Cost Mocap PyQt")
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:3001')
        self.camera_stream_running = False
        self.camera_stream_thread = None
        self.camera_thread = cameraThread.MyThread("http://localhost:3001/api/camera-stream")
        self.camera_thread.frame_signal.connect(self.setImage)
        self.init_ui()
        self.register_socket_handlers()

    def init_ui(self):
        layout = QVBoxLayout()
        # Camera Stream Viewer
        self.camera_stream_label = QLabel("Camera Stream")
        self.camera_stream_label.setFixedHeight(300)
        self.camera_stream_label.setAlignment(Qt.AlignCenter)
        self.toggle_stream_btn = QPushButton("Start Camera Stream")
        self.toggle_stream_btn.clicked.connect(self.toggle_camera_stream)
        layout.addWidget(self.camera_stream_label)
        layout.addWidget(self.toggle_stream_btn)
        # Camera Controls
        camera_group = QVBoxLayout()
        camera_group.addWidget(QLabel("Camera Controls"))
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setMinimum(0)
        self.exposure_slider.setMaximum(1000)
        self.exposure_slider.setValue(100)
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setMinimum(0)
        self.gain_slider.setMaximum(100)
        self.gain_slider.setValue(0)
        camera_group.addWidget(QLabel("Exposure"))
        camera_group.addWidget(self.exposure_slider)
        camera_group.addWidget(QLabel("Gain"))
        camera_group.addWidget(self.gain_slider)
        self.update_camera_btn = QPushButton("Update Camera Settings")
        self.update_camera_btn.clicked.connect(self.update_camera_settings)
        camera_group.addWidget(self.update_camera_btn)
        layout.addLayout(camera_group)


        tracking_group = QGridLayout()
        tracking_group.addWidget(QLabel("tracking settings"),0,0)
        tracking_group.addWidget(QLabel("Live triangulation"),1,0)
        self.live_triangulation = QPushButton("start")
        self.live_triangulation.clicked.connect(self.toggle_live_triangulation)
        
        tracking_group.addWidget(self.live_triangulation,1,1)
        tracking_group.addWidget(QLabel("Locate Objects"),2,0)
        self.locate_objects = QPushButton("start")
        self.locate_objects.clicked.connect(self.toggle_locate_objects)
        
        tracking_group.addWidget(self.locate_objects,2,1)
        tracking_group.addWidget(QLabel("set Scale Using Points"),3,0)
        self.set_scale = QPushButton("start")
        self.set_scale.clicked.connect(self.toggle_set_scale)
        
        tracking_group.addWidget(self.set_scale,3,1)
        tracking_group.addWidget(QLabel("Acquire floor"),4,0)
        self.acquire_floor = QPushButton("start")
        self.acquire_floor.clicked.connect(self.toggle_acquire_floor)
        
        tracking_group.addWidget(self.acquire_floor,4,1)
        tracking_group.addWidget(QLabel("set origin"),5,0)
        self.set_origin = QPushButton("start")
        self.set_origin.clicked.connect(self.toggle_set_origin)
        
        tracking_group.addWidget(self.set_origin,5,1)
        tracking_group.addWidget(QLabel("Collect points for camera pose calibration"),6,0)
        self.collect_points = QPushButton("start")
        self.collect_points.clicked.connect(self.toggle_collect_points)
        
        tracking_group.addWidget(self.collect_points,6,1)
        self.calculate_pose = QPushButton("calculate camera pose with 0 points")
        self.calculate_pose.clicked.connect(self.toggle_calculate_pose)
        
        tracking_group.addWidget(self.calculate_pose,6,1)


        layout.addLayout(tracking_group)


        # # Trajectory Planning
        # traj_group = QVBoxLayout()
        # traj_group.addWidget(QLabel("Trajectory Planning"))
        # self.max_vel_input = QLineEdit("1,1,1")
        # self.max_accel_input = QLineEdit("1,1,1")
        # self.max_jerk_input = QLineEdit("0.5,0.5,0.5")
        # self.waypoints_input = QTextEdit(
        #     '[\n[0.2,0.2,0.6,0,0,0.8,true],\n[-0.2,0.2,0.6,0.2,0.2,0.6,true],\n[-0.2,-0.2,0.5,0,0,0.4,true],\n[0.2,-0.2,0.5,-0.2,-0.2,0.6,true],\n[0.2,0.2,0.5,0,0,0.8,true]\n]'
        # )
        # traj_group.addWidget(QLabel("Max Vel (comma separated)"))
        # traj_group.addWidget(self.max_vel_input)
        # traj_group.addWidget(QLabel("Max Accel (comma separated)"))
        # traj_group.addWidget(self.max_accel_input)
        # traj_group.addWidget(QLabel("Max Jerk (comma separated)"))
        # traj_group.addWidget(self.max_jerk_input)
        # traj_group.addWidget(QLabel("Waypoints (JSON)"))
        # traj_group.addWidget(self.waypoints_input)
        # self.plan_traj_btn = QPushButton("Plan Trajectory")
        # self.plan_traj_btn.clicked.connect(self.plan_trajectory)
        # traj_group.addWidget(self.plan_traj_btn)
        # self.traj_result = QTextEdit()
        # self.traj_result.setReadOnly(True)
        # traj_group.addWidget(self.traj_result)
        # layout.addLayout(traj_group)

        # # Drone Setpoints
        # drone_group = QVBoxLayout()
        # drone_group.addWidget(QLabel("Drone Setpoints"))
        # self.drone_setpoint_inputs = []
        # for i in range(NUM_DRONES):
        #     h = QHBoxLayout()
        #     h.addWidget(QLabel(f"Drone {i} Setpoint:"))
        #     x = QLineEdit("0")
        #     y = QLineEdit("0")
        #     z = QLineEdit("0")
        #     h.addWidget(x)
        #     h.addWidget(y)
        #     h.addWidget(z)
        #     self.drone_setpoint_inputs.append((x, y, z))
        #     drone_group.addLayout(h)
        # self.send_setpoint_btn = QPushButton("Send Setpoints")
        # self.send_setpoint_btn.clicked.connect(self.send_setpoints)
        # drone_group.addWidget(self.send_setpoint_btn)
        # layout.addLayout(drone_group)

        self.setLayout(layout)
    def toggle_live_triangulation(self):
        print()
        # socket.emit("triangulate-points", { startOrStop, cameraPoses, toWorldCoordsMatrix })
    def toggle_locate_objects(self):
        print()
        # setIsLocatingObjects(!isLocatingObjects);
        #             socket.emit("locate-objects", { startOrStop: isLocatingObjects ? "stop" : "start" })
    def toggle_set_scale(self):
        print()
    def toggle_acquire_floor(self):
        print()
    def toggle_set_origin(self):
        print()
    def toggle_collect_points(self):
        print()
    def toggle_calculate_pose(self):
        print()
    def update_camera_settings(self):
        exposure = self.exposure_slider.value()
        gain = self.gain_slider.value()
        self.sio.emit("update-camera-settings", {"exposure": exposure, "gain": gain})

    # def plan_trajectory(self):
    #     try:
    #         waypoints = json.loads(self.waypoints_input.toPlainText())
    #         max_vel = [float(x) for x in self.max_vel_input.text().split(",")]
    #         max_accel = [float(x) for x in self.max_accel_input.text().split(",")]
    #         max_jerk = [float(x) for x in self.max_jerk_input.text().split(",")]
    #         timestep = TRAJECTORY_PLANNING_TIMESTEP
    #         body = {
    #             "waypoints": waypoints,
    #             "maxVel": max_vel,
    #             "maxAccel": max_accel,
    #             "maxJerk": max_jerk,
    #             "timestep": timestep
    #         }
    #         resp = requests.post("http://localhost:3001/api/trajectory-planning", json=body)
    #         if resp.ok:
    #             setpoints = resp.json()["setpoints"]
    #             self.traj_result.setPlainText(json.dumps(setpoints, indent=2))
    #         else:
    #             self.traj_result.setPlainText("Error: " + resp.text)
    #     except Exception as e:
    #         self.traj_result.setPlainText(f"Error: {e}")

    # def send_setpoints(self):
    #     for i, (x, y, z) in enumerate(self.drone_setpoint_inputs):
    #         setpoint = [float(x.text()), float(y.text()), float(z.text())]
    #         self.sio.emit("set-drone-setpoint", {"droneSetpoint": setpoint, "droneIndex": i})

    def register_socket_handlers(self):
        @self.sio.on("fps")
        def on_fps(data):
            print("FPS:", data["fps"])

        @self.sio.on("to-world-coords-matrix")
        def on_matrix(data):
            print("To World Coords Matrix:", data["to_world_coords_matrix"])

        @self.sio.on("object-points")
        def on_object_points(data):
            print("Object Points:", data["object_points"])
    def toggle_camera_stream(self):
        if not self.camera_stream_running:
            self.camera_stream_running = True
            self.toggle_stream_btn.setText("Stop Camera Stream")
            
          

            self.camera_thread.start()
            # self.camera_stream_thread = threading.Thread(target=self.camera_stream_loop, daemon=True)
            # self.camera_stream_thread.start()
        else:
            self.camera_stream_running = False
            self.camera_thread.stop()
            self.toggle_stream_btn.setText("Start Camera Stream")

    # def camera_stream_loop(self):
    #     url = "http://localhost:3001/api/camera-stream"
    #     import requests
    #     try:
    #         with requests.get(url, stream=True) as r:
    #             bytes_data = b""
    #             for chunk in r.iter_content(chunk_size=1024):
    #                 if not self.camera_stream_running:
    #                     break
    #                 bytes_data += chunk
    #                 a = bytes_data.find(b'\xff\xd8')
    #                 b = bytes_data.find(b'\xff\xd9')
    #                 if a != -1 and b != -1 and b > a:
    #                     jpg = bytes_data[a:b+2]
    #                     bytes_data = bytes_data[b+2:]
    #                     self.update_camera_image(jpg)
    #     except Exception as e:
    #         print("Camera stream error:", e)

    # def update_camera_image(self, jpg_bytes):
    #     image = QImage.fromData(jpg_bytes)
    #     pixmap = QPixmap.fromImage(image)
    #     # Resize to fit label
        
    #     pixmap = pixmap.scaled(self.camera_stream_label.width(), self.camera_stream_label.height(), Qt.KeepAspectRatio)
    #     from PyQt5.QtCore import QTimer
    #     def set_pixmap():
    #         self.camera_stream_label.setPixmap(pixmap)
    #     # Schedule the update on the main thread
    #     QTimer.singleShot(0, set_pixmap)
    @Slot(QImage)
    def setImage(self, image):
        self.camera_stream_label.setPixmap(QPixmap.fromImage(image))
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())