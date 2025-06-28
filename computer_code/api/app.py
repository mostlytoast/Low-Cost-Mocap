import os
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QGridLayout,
    QAction
)
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import index
from viewer3d import QGLControllerWidget
import time
from PyQt5 import QtWidgets, QtCore
import numpy as np
import file_mech
# import openmesh as om


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Low-Cost Mocap PyQt")

        self.camera_stream_running = False
        self.camera_stream_thread = None
        self.has_world_calibration = False
        self.has_collected_points = False
        self.collecting_points = False
        self.is_triangulating_points = False
        self.is_locating_objects = False

        # data variables
        self.captured_points_for_pose = []
        self.camera_poses = []
        self.object_points = []

        self.last_time = 0
        # self.to_world_coords_matrix = [[0.9941338485260931,0.0986512964608827,-0.04433748889242502,0.9938296704767513],[-0.0986512964608827,0.659022672138982,-0.7456252673517598,2.593331619023365],[0.04433748889242498,-0.7456252673517594,-0.6648888236128887,2.9576262456228286],[0,0,0,1]]
        self.to_world_coords_matrix = np.eye(4)
        self.camera_params = []
        # self.camera_poses = ([{"R":[[1,0,0],[0,1,0],[0,0,1]],"t":[0,0,0]},{"R":[[-0.13639683654819235,0.5218092394166619,-0.8420872998917929],[-0.4139150519535063,0.7422608899144861,0.5269944032621987],[0.9000390173464546,0.42043297796766566,0.11474266116518528]],"t":[0.26932272217012254,-0.5101944343371594,0.89286825065571]}])


        self.camera_thread = index.MyThread()
        self.camera_thread.frame_signal.connect(self.setImage)
        self.camera_thread.data_signal.connect(self.setData)
        self.file = file_mech.file_dialog(self)
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # self.resize(640, 480)
        # TODO probs just include in this file and not as separate css
        dirname = ""
        # When accessing these files at runtime, use sys._MEIPASS to get the correct path if running as a bundled app.
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            dirname = os.path.dirname(sys._MEIPASS)
            dirname += "/_internal/api"
            print("package", dirname)
        else:
            dirname = os.path.dirname(__file__)

        # dirname = os.path.dirname(sys._MEIPASS)
        filename = os.path.join(dirname, "style.css")
        f = open(filename)
        with open(filename) as style:
            self.styleText = style.read()
            self.setStyleSheet(self.styleText)

        self.init_ui()

    def init_ui(self):
        stream_preview = QVBoxLayout()
        # Camera Stream Viewer
        self.fps_label = QLabel("FPS 0")
        self.fps_label.setFixedHeight(20)
        stream_preview.addWidget(self.fps_label)
        self.camera_stream_label = QLabel("Camera Stream")
        self.camera_stream_label.setFixedHeight(200)
        self.camera_stream_label.setAlignment(Qt.AlignCenter)
        self.toggle_stream_btn = QPushButton("Start Camera Stream")
        self.toggle_stream_btn.clicked.connect(self.toggle_camera_stream)
        self.toggle_stream_btn.setFixedHeight(30)
        # self.toggle_stream_btn.setEnabled(False)

        stream_preview.addWidget(self.camera_stream_label)
        stream_preview.addWidget(self.toggle_stream_btn)

        # Camera Controls
        stream_preview.addWidget(QLabel("Camera Controls"))
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setMinimum(0)
        self.exposure_slider.setMaximum(100)
        self.exposure_slider.setValue(100)
        self.exposure_slider.setFixedHeight(20)

        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setMinimum(0)
        self.gain_slider.setMaximum(100)
        self.gain_slider.setValue(0)
        self.gain_slider.setFixedHeight(30)
        settings = QGridLayout()
        settings.addWidget(QLabel("Exposure"), 0, 0)
        settings.addWidget(self.exposure_slider, 0, 1)
        settings.addWidget(QLabel("Gain"), 1, 0)
        settings.addWidget(self.gain_slider, 1, 1)
        stream_preview.addLayout(settings)

        # self.update_camera_btn = QPushButton("Update Camera Settings")
        # self.update_camera_btn.clicked.connect(self.update_camera_settings)
        # self.update_camera_btn.setFixedHeight(30)

        stream_preview.addWidget(self.update_camera_btn)
        self.layout.addLayout(stream_preview)

        self.tracking_layout = QGridLayout()

        # Ensure tracking_layout and tracking_group expand properly
        self.tracking_layout.setColumnStretch(0, 0)
        self.tracking_layout.setColumnStretch(1, 1)
        self.tracking_layout.setRowStretch(0, 1)
        #
        self.tracking_group = QGridLayout()
        self.tracking_group.addWidget(QLabel("tracking settings"), 0, 0)
        self.tracking_group.addWidget(QLabel("Live triangulation"), 1, 0)
        self.live_triangulation = QPushButton("start")
        self.live_triangulation.clicked.connect(self.toggle_live_triangulation)
        # self.live_triangulation.setEnabled(False)

        self.tracking_group.addWidget(self.live_triangulation, 1, 1)
        self.tracking_group.addWidget(QLabel("Locate Objects"), 2, 0)
        self.locate_objects = QPushButton("start")
        self.locate_objects.clicked.connect(self.toggle_locate_objects)
        # self.locate_objects.setEnabled(False)

        self.tracking_group.addWidget(self.locate_objects, 2, 1)
        self.tracking_group.addWidget(QLabel("set Scale Using Points"), 3, 0)
        self.set_scale = QPushButton("start")
        self.set_scale.clicked.connect(self.toggle_set_scale)
        # self.set_scale.setEnabled(False)

        self.tracking_group.addWidget(self.set_scale, 3, 1)
        self.tracking_group.addWidget(QLabel("Acquire floor"), 4, 0)
        self.acquire_floor = QPushButton("start")
        self.acquire_floor.clicked.connect(self.toggle_acquire_floor)
        # self.acquire_floor.setEnabled(False)

        self.tracking_group.addWidget(self.acquire_floor, 4, 1)
        self.tracking_group.addWidget(QLabel("set origin"), 5, 0)
        self.set_origin = QPushButton("start")
        self.set_origin.clicked.connect(self.toggle_set_origin)
        # self.set_origin.setEnabled(False)

        self.tracking_group.addWidget(self.set_origin, 5, 1)
        self.tracking_group.addWidget(QLabel("Collect points"), 6, 0)
        self.collect_points = QPushButton("start")
        self.collect_points.clicked.connect(self.toggle_collect_points)
        # self.collect_points.setEnabled(False)
        self.tracking_group.addWidget(self.collect_points, 6, 1)

        self.calculate_pose = QPushButton("calculate with 0 points")
        self.calculate_pose.clicked.connect(self.toggle_calculate_pose)
        # self.calculate_pose.setEnabled(False)
        self.tracking_group.setColumnMinimumWidth(0, 20)
        self.tracking_group.setColumnMinimumWidth(1, 20)
        self.tracking_group.addWidget(self.calculate_pose, 7, 1)
        # Wrap tracking_group in a QWidget for proper sizing
        tracking_group_widget = QWidget()
        tracking_group_widget.setLayout(self.tracking_group)
        self.tracking_layout.addWidget(tracking_group_widget, 0, 0)

        self.gl_widget = QGLControllerWidget(self)
        # Reduce or remove the minimum width to allow smaller window sizes
        self.gl_widget.setMinimumSize(450, 100)

        self.tracking_layout.addWidget(self.gl_widget, 0, 1)
        self.layout.addLayout(self.tracking_layout)
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
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

        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
        timer.timeout.connect(self.gl_widget.updateGL)
        timer.start()
        # wait till window exists to create grid (will error out other wise)
        QtCore.QTimer.singleShot(0, self.gl_widget.create_grid)
        QtCore.QTimer.singleShot(0, self.test_points)

        self.update_enabled_states()

    def test_points(self):
        # mesh = om.read_trimesh(
        #     "computer_code/api/Untitled_Scan_17_01_20/textured_output.obj"
        # )
        # # Example: Rotate mesh 90 degrees around Z axis
        # # Set rotation angles in degrees for x, y, z
        # angle_x = np.radians(90)  # Change as needed

        # # Rotation matrix around X axis
        # Rx = np.array(
        #     [
        #         [1, 0, 0],
        #         [0, np.cos(angle_x), -np.sin(angle_x)],
        #         [0, np.sin(angle_x), np.cos(angle_x)],
        #     ]
        # )

        # # Combined rotation: R = Rz @ Ry @ Rx
        # rotation_matrix = Rx

        # for vh in mesh.vertices():
        #     v = mesh.point(vh)
        #     rotated = rotation_matrix @ np.array([v[0], v[1], v[2]])
        #     mesh.set_point(vh, rotated)

        # self.gl_widget.set_mesh(mesh)
        self.gl_widget.add_point([0, 0, 1])
        self.gl_widget.add_point([0, 0, 2])

        self.gl_widget.add_point([0, 5, 0])

    def setup_scene(self, data):
        self.gl_widget.camera_vertices_list = []
        for camera_transform in data:
            # Convert R and t to 4x4 transformation matrix
            R = np.array(camera_transform["R"])
            t = np.array(camera_transform["t"]).reshape(3, 1)
            cam_matrix = np.eye(4)
            cam_matrix[:3, :3] = R
            cam_matrix[:3, 3] = t.flatten()
            # Apply world transform
            # TODO what order to apply transforms?
            world_matrix = cam_matrix @ self.to_world_coords_matrix
            # Extract world R and t
            world_R = world_matrix[:3, :3].tolist()
            world_t = world_matrix[:3, 3].tolist()
            world_camera_transform = {"R": world_R, "t": world_t}
            self.gl_widget.add_camera(transform=world_camera_transform)
            # self.gl_widget.add_camera(transform=camera_transform)

    # Function to get camera and setup config
    # def openFile(self):
    #     # TODO have to find way for this ro
    #     fname = QtWidgets.QFileDialog.getOpenFileName(
    #         self, "Open file", "", "Camera Configuration files (*.json)"
    #     )
    #     self.camera_thread.update_camera_params(filename=fname[0])
    # Function to save camera and setup config
    
    

    def toggle_live_triangulation(self):
        self.is_triangulating_points = not self.is_triangulating_points
        self.camera_thread.live_mocap(
            "start" if self.is_triangulating_points else "stop",
            self.camera_poses,
            self.to_world_coords_matrix,
        )
        self.live_triangulation.setText(
            "Stop" if self.is_triangulating_points else "Start"
        )
        self.update_enabled_states()

    def toggle_locate_objects(self):
        self.is_locating_objects = not self.is_locating_objects
        self.camera_thread.start_or_stop_locating_objects(
            "start" if self.is_locating_objects else "stop"
        )
        self.locate_objects.setText("Stop" if self.is_locating_objects else "Start")

        self.update_enabled_states()

    def toggle_set_scale(self):
        self.camera_thread.determine_scale(self.object_points, self.camera_poses)
        # self.update_enabled_states()

    def toggle_acquire_floor(self):
        self.camera_thread.acquire_floor(self.object_points)
        # self.update_enabled_states()


    def toggle_set_origin(self):
        self.camera_thread.set_origin(
            self.object_points[-1], self.to_world_coords_matrix
        )
        # self.update_enabled_states()


    def toggle_collect_points(self):
        if not self.collecting_points:
            self.captured_points_for_pose = []
            self.camera_thread.capture_points({"startOrStop": "start"})
            self.collecting_points = True
            self.update_enabled_states()

            self.collect_points.setText("Stop")

        else:
            self.collect_points.setText("Start")
            self.camera_thread.capture_points({"startOrStop": "stop"})
            self.collecting_points = False
            self.update_enabled_states()
        # self.has_collected_points = True
        self.update_enabled_states()

    def toggle_calculate_pose(self):
        # TODO stop point capture (disable button)
        self.collecting_points = False
        self.has_world_calibration = True
        # send data to calculate_camera_pose
        # self.camera_poses, output_data =
        self.camera_thread.calculate_camera_pose(
            {"cameraPoints": self.captured_points_for_pose}
        )

        # print("camera pose",self.camera_poses, output_data)

        # self.setup_scene(self.camera_poses)
        self.update_enabled_states()

    def update_camera_settings(self):
        exposure = self.exposure_slider.value()
        gain = self.gain_slider.value()
        self.camera_thread.change_camera_settings({"exposure": exposure, "gain": gain})
        self.update_enabled_states()

    def toggle_camera_stream(self):

        # TODO cant start then stop camera stream causes paused image
        if not self.camera_stream_running :
            self.camera_stream_running = True
            self.update_enabled_states()
            self.toggle_stream_btn.setText("Stop Camera Stream")
            self.camera_thread.start()
            self.camera_thread.enable()
            # self.update_enabled_states()
        else:
            self.camera_stream_running = False
            self.update_enabled_states()
            self.camera_thread.stop()
            self.toggle_stream_btn.setText("Start Camera Stream")
        self.update_enabled_states()

    def update_enabled_states(self):
        """_summary_ updates if the buttons should be enabled or not based on state"""
        self.live_triangulation.setEnabled(
            self.camera_stream_running and self.has_world_calibration
        )
        self.locate_objects.setEnabled(
            self.camera_stream_running and self.has_world_calibration
        )
        self.set_scale.setEnabled(
            self.camera_stream_running and self.has_world_calibration
        )
        self.acquire_floor.setEnabled(
            self.camera_stream_running and self.has_world_calibration
        )
        self.set_origin.setEnabled(
            self.camera_stream_running
            and self.has_world_calibration
            and len(self.object_points) > 0
        )
        self.toggle_stream_btn.setEnabled(self.camera_params!=[])
        self.update_camera_btn.setEnabled(self.camera_params!=[])
        self.exposure_slider.setEnabled(self.camera_params!=[])

        self.gain_slider.setEnabled(self.camera_params!=[])

        self.collect_points.setEnabled(self.camera_stream_running)

        self.calculate_pose.setEnabled(len(self.captured_points_for_pose) > 0)
    def updates_config(self, camera_params, camera_poses, to_world_coords_matrix):
        """_summary_ gets updated config data from file_mech  and updates the backend 

        Args:
            camera_params (_type_): _description_
            camera_poses (_type_): _description_
            to_world_coords_matrix (_type_): _description_
        """
        self.camera_params  = camera_params
        self.camera_poses  = camera_poses
        self.to_world_coords_matrix = to_world_coords_matrix
        self.camera_thread.update_camera_params(camera_params)
        self.update_enabled_states()


    @Slot(QImage)
    def setImage(self, image):
        self.camera_stream_label.setPixmap(QPixmap.fromImage(image))
        # update fps
        time_now = time.time()
        if self.last_time != 0:
            self.fps = 1 / (time_now - self.last_time)
            self.fps_label.setText("FPS " + str(round(self.fps)))
            print("fps", self.fps)
        self.last_time = time_now

    @Slot(dict)
    def setData(self, data):

        if self.collecting_points and "image-points" in data:
            self.captured_points_for_pose.append(data.get("image-points"))

            self.calculate_pose.setText(
                "calculate with " + str(len(self.captured_points_for_pose)) + " points"
            )
        # todo have to find way to append data in smart way
        if self.is_triangulating_points and "object_points" in data:
            self.gl_widget.points_list = []
            self.gl_widget.point_colors = []
            self.gl_widget.point_size = 3

            objects = data.get("object_points")[0]
            self.object_points.append(objects)
            for object_pos in objects:

                self.gl_widget.add_point(position=object_pos, size=3)
            self.update_enabled_states()
        if "camera_poses" in data:
            self.camera_poses = data.get("camera_poses")
            self.setup_scene(data=self.camera_poses)
            # TODO join setup_scene in camera and world if statements
            self.update_enabled_states()
        if "to_world_coords_matrix" in data:
            self.to_world_coords_matrix = data.get("to_world_coords_matrix")
            self.setup_scene(data=self.camera_poses)
            self.update_enabled_states()


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


# import cProfile
if __name__ == "__main__":
    main()
    # cProfile.run('main()')
