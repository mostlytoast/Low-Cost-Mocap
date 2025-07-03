import math
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QGridLayout,
    QAction,
)
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QPixmap, QImage
import index
from viewer3d import QGLControllerWidget
import time
from PyQt5 import QtWidgets, QtCore
import numpy as np
import file_mech

# import openmesh as om
import style

from helpers import Cameras
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Low-Cost Mocap PyQt")
        # print("parent",parent)
        self.parent = parent
        self.cameras = Cameras.instance()
        self.camera_stream_running = False
        self.camera_stream_thread = None
        self.has_world_calibration = False
        self.has_collected_points = False
        self.collecting_points = False
        self.is_triangulating_points = False
        self.is_locating_objects = False
        self.is_acquiring_floor = False
        self.is_acquiring_origin = False
        self.is_acquiring_scale= False
        self.has_origin = False
        self.has_scale = False
        # data variables
        self.captured_points_for_pose = []
        self.object_points = []

        self.last_time = 0
        # self.cameras.to_world_coords_matrix = [[0.9941338485260931,0.0986512964608827,-0.04433748889242502,0.9938296704767513],[-0.0986512964608827,0.659022672138982,-0.7456252673517598,2.593331619023365],[0.04433748889242498,-0.7456252673517594,-0.6648888236128887,2.9576262456228286],[0,0,0,1]]
        # self.cameras.to_world_coords_matrix = np.eye(4)
        # self.cameras.camera_poses = ([{"R":[[1,0,0],[0,1,0],[0,0,1]],"t":[0,0,0]},{"R":[[-0.13639683654819235,0.5218092394166619,-0.8420872998917929],[-0.4139150519535063,0.7422608899144861,0.5269944032621987],[0.9000390173464546,0.42043297796766566,0.11474266116518528]],"t":[0.26932272217012254,-0.5101944343371594,0.89286825065571]}])

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
        self.setStyleSheet(style.style)

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

        self.update_camera_btn = QPushButton("Update Camera Settings")
        self.update_camera_btn.clicked.connect(self.update_camera_settings)
        self.update_camera_btn.setFixedHeight(30)

        stream_preview.addWidget(self.update_camera_btn)
        self.layout.addLayout(stream_preview)

        self.tracking_layout = QGridLayout()

        # Ensure tracking_layout and tracking_group expand properly
        self.tracking_layout.setColumnStretch(0, 0)
        self.tracking_layout.setColumnStretch(1, 1)
        self.tracking_layout.setRowStretch(0, 1)
        #
        self.tracking_group = QGridLayout()
        row = 0
        self.tracking_group.addWidget(QLabel("tracking settings"), row, 0)
        row += 1

        # collect points
        self.tracking_group.addWidget(QLabel("Collect points"), row, 0)
        self.collect_points = QPushButton("start")
        self.collect_points.clicked.connect(self.toggle_collect_points)
        # self.collect_points.setEnabled(False)
        self.tracking_group.addWidget(self.collect_points, row, 1)
        row += 1

        self.calculate_pose = QPushButton("calculate with 0 points")
        self.calculate_pose.clicked.connect(self.toggle_calculate_pose)
        # self.calculate_pose.setEnabled(False)
        self.tracking_group.setColumnMinimumWidth(0, 20)
        self.tracking_group.setColumnMinimumWidth(1, 20)
        self.tracking_group.addWidget(self.calculate_pose, row, 1)
        row += 1

        # set origin
        self.tracking_group.addWidget(QLabel("set origin"), row, 0)
        self.set_origin = QPushButton("start")
        self.set_origin.clicked.connect(self.toggle_set_origin)
        # self.set_origin.setEnabled(False)
        self.tracking_group.addWidget(self.set_origin, row, 1)
        row += 1

        # scale
        self.tracking_group.addWidget(QLabel("set Scale Using Points"), row, 0)
        self.set_scale = QPushButton("start")
        self.set_scale.clicked.connect(self.toggle_set_scale)
        # self.set_scale.setEnabled(False)
        self.tracking_group.addWidget(self.set_scale, row, 1)
        row += 1

        # get floor
        self.tracking_group.addWidget(QLabel("Acquire floor"), row, 0)
        self.acquire_floor = QPushButton("start")
        self.acquire_floor.clicked.connect(self.toggle_acquire_floor)
        # self.acquire_floor.setEnabled(False)
        self.tracking_group.addWidget(self.acquire_floor, row, 1)
        row += 1

        self.tracking_group.addWidget(QLabel("Live triangulation"), row, 0)
        self.live_triangulation = QPushButton("start")
        self.live_triangulation.clicked.connect(self.toggle_live_triangulation)
        # self.live_triangulation.setEnabled(False)
        self.tracking_group.addWidget(self.live_triangulation, row, 1)
        row += 1

        self.tracking_group.addWidget(QLabel("Locate Objects"), row, 0)
        self.locate_objects = QPushButton("start")
        self.locate_objects.clicked.connect(self.toggle_locate_objects)
        self.tracking_group.addWidget(self.locate_objects, row, 1)
        # self.locate_objects.setEnabled(False)

        # Wrap tracking_group in a QWidget for proper sizing
        tracking_group_widget = QWidget()
        tracking_group_widget.setLayout(self.tracking_group)
        self.tracking_layout.addWidget(tracking_group_widget, 0, 0)

        self.gl_widget = QGLControllerWidget(self)
        # Reduce or remove the minimum width to allow smaller window sizes
        self.gl_widget.setMinimumSize(450, 100)

        self.tracking_layout.addWidget(self.gl_widget, 0, 1)
        self.layout.addLayout(self.tracking_layout)

        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
        timer.timeout.connect(self.gl_widget.updateGL)
        timer.start()
        # wait till window exists to create grid and only if not a child to another window (will error out other wise) also prevent duplicate file menu options
        if self.parent == None:
            self.menu()
            self.startup()
        self.update_enabled_states()

    def menu(self):
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
        def openFile():
            if self.camera_stream_running:
                self.toggle_camera_stream()
            self.file.openFile()

        open_action = QAction("&Open", self)
        open_action.triggered.connect(openFile)
        file_menu.addAction(open_action)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open File")

    def startup(self):
        QtCore.QTimer.singleShot(4, self.gl_widget.create_grid)
        QtCore.QTimer.singleShot(4, self.test_points)

    def test_points(self):
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
            if self.cameras.to_world_coords_matrix != []:
                world_matrix =   np.asarray(self.cameras.to_world_coords_matrix) @ cam_matrix
            else: 
                world_matrix = cam_matrix
            # Extract world R and t
            world_R = world_matrix[:3, :3].tolist()
            world_t = world_matrix[:3, 3].tolist()
            world_camera_transform = {"R": world_R, "t": world_t}
            self.gl_widget.add_camera(transform=world_camera_transform)
            # self.gl_widget.add_camera(transform=camera_transform)

    def toggle_live_triangulation(self):
        self.is_triangulating_points = not self.is_triangulating_points
        self.camera_thread.live_mocap(
            "start" if self.is_triangulating_points else "stop",
            self.cameras.camera_poses,
            self.cameras.to_world_coords_matrix,
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

       
        self.is_acquiring_scale = not self.is_acquiring_scale
        self.camera_thread.live_mocap(
        "start" if self.is_acquiring_scale else "stop",
        self.cameras.camera_poses,
        self.cameras.to_world_coords_matrix,
        )
        self.set_scale.setText(
            "Stop" if self.is_acquiring_scale else "Start"
        )
        if not self.is_acquiring_scale and len(self.object_points) >0:
            if len(self.object_points[-1]) >0:
                # finished capturing points 
                self.camera_thread.determine_scale(self.object_points, self.cameras.camera_poses)
                self.is_acquiring_scale = False
                self.has_scale = True
                self.update_enabled_states()
                self.object_points = []
        # self.update_enabled_states()

    def toggle_acquire_floor(self):
        # starts collecting points and when finished (button is clicked again) it starts calculating floor position 
        self.is_acquiring_floor = not self.is_acquiring_floor
        self.camera_thread.live_mocap(
        "start" if self.is_acquiring_floor else "stop",
        self.cameras.camera_poses,
        self.cameras.to_world_coords_matrix,
        )
        self.acquire_floor.setText(
            "Stop" if self.is_acquiring_floor else "Start"
        )
        
        if not self.is_acquiring_floor:
            # finished capturing points 
            self.update_enabled_states()
            self.camera_thread.acquire_floor(self.object_points)
        # self.update_enabled_states()

    def toggle_set_origin(self):
        self.is_acquiring_origin = not self.is_acquiring_origin
        self.camera_thread.live_mocap(
        "start" if self.is_acquiring_origin else "stop",
        self.cameras.camera_poses,
        self.cameras.to_world_coords_matrix,
        )
        self.set_origin.setText(
            "Stop" if self.is_acquiring_origin else "Start"
        )
        

        if not self.is_acquiring_origin and len(self.object_points) >0:
            if len(self.object_points[-1]) >0:
                # finished capturing points 
                self.camera_thread.set_origin(
                self.object_points[-1], self.cameras.to_world_coords_matrix
            )
                self.is_acquiring_origin = False
                self.has_origin = True
                self.update_enabled_states()
        if not self.is_acquiring_origin: 
            self.object_points = [] 

        # if not self.is_acquiring_origin:
        #     self.camera_thread.live_mocap(
        #     "start",
        #     self.cameras.camera_poses,
        #     self.cameras.to_world_coords_matrix,
        #     )
        #     self.set_origin.setText(
        #         "Stop" 
        #     )
        #     self.is_acquiring_origin = True
            
        # if self.is_acquiring_origin and len(self.object_points) >0:
        #     if len(self.object_points[-1]) >0:
        #         # finished capturing points 
        #         self.camera_thread.set_origin(
        #         self.object_points[-1], self.cameras.to_world_coords_matrix
        #     )
        #         self.is_acquiring_origin = False
        #         self.has_origin = True
        #         self.camera_thread.live_mocap(
        #         "stop",
        #         self.cameras.camera_poses,
        #         self.cameras.to_world_coords_matrix,
        #         )
        #         self.set_origin.setText(
        #             "Start" 
        #         )
        #         self.object_points = []
        #         self.update_enabled_states()

            
    

    def toggle_collect_points(self):
        if not self.collecting_points:
            self.captured_points_for_pose = []
            self.camera_thread.capture_points({"startOrStop": "start"})
            self.collecting_points = True
            # self.update_enabled_states()

            self.collect_points.setText("Stop")
            self.has_origin = False
            self.has_scale = False

        else:
            self.collect_points.setText("Start")
            self.camera_thread.capture_points({"startOrStop": "stop"})
            self.collecting_points = False
            # self.update_enabled_states()
        # self.has_collected_points = True
        self.update_enabled_states()

    def toggle_calculate_pose(self):
        # TODO stop point capture (disable button)
        self.collecting_points = False
        self.has_world_calibration = True
        # send data to calculate_camera_pose
        # self.cameras.camera_poses, output_data =
        self.camera_thread.calculate_camera_pose(
            {"cameraPoints": self.captured_points_for_pose}
        )

        # print("camera pose",self.cameras.camera_poses, output_data)

        # self.setup_scene(self.cameras.camera_poses)
        self.update_enabled_states()

    def update_camera_settings(self):
        exposure = self.exposure_slider.value()
        gain = self.gain_slider.value()
        self.camera_thread.change_camera_settings({"exposure": exposure, "gain": gain})
        self.update_enabled_states()

    def toggle_camera_stream(self):

        # TODO cant start then stop camera stream causes paused image
        if not self.camera_stream_running:
            self.camera_stream_running = True
            # self.update_enabled_states()
            self.toggle_stream_btn.setText("Stop Camera Stream")
            self.camera_thread.start()
            self.camera_thread.enable()
            # self.update_enabled_states()
        else:
            self.camera_stream_running = False
            # self.update_enabled_states()
            self.camera_thread.stop()
            self.toggle_stream_btn.setText("Start Camera Stream")
        self.update_enabled_states()

    def update_enabled_states(self):
        has_configuration = self.cameras.camera_params != [] 
        has_camera_poses =  self.cameras.camera_poses != {}
        has_world_calibration = self.cameras.to_world_coords_matrix != []
        """_summary_ updates if the buttons should be enabled or not based on state"""
        can_triangulate = self.camera_stream_running and has_world_calibration
        self.live_triangulation.setEnabled(can_triangulate)
        self.locate_objects.setEnabled(can_triangulate)
    
        # ensure calibration buttons are enabled in order
        self.set_origin.setEnabled(
            self.camera_stream_running
            and has_camera_poses
        )
        self.set_scale.setEnabled(self.has_origin and self.set_origin.isEnabled())
        self.acquire_floor.setEnabled(self.camera_stream_running
            and has_camera_poses)

        self.toggle_stream_btn.setEnabled(has_configuration)
        self.update_camera_btn.setEnabled(has_configuration)
        self.exposure_slider.setEnabled(has_configuration)
        self.gain_slider.setEnabled(has_configuration)
        calib_happening = self.is_acquiring_origin or self.is_acquiring_scale or self.is_acquiring_floor
        self.collect_points.setEnabled(self.camera_stream_running and not calib_happening)

        self.calculate_pose.setEnabled(len(self.captured_points_for_pose) > 0)

    def updates_config(self, camera_params, camera_poses, to_world_coords_matrix):
        """gets updated config data from file_mech  and updates the backend

        Args:
            camera_params (_type_): _description_
            camera_poses (_type_): _description_
            to_world_coords_matrix (_type_): _description_
        """
        self.camera_thread.stop()
        
        self.cameras.camera_params = camera_params
        self.cameras.camera_poses = camera_poses
        self.cameras.to_world_coords_matrix = to_world_coords_matrix

        if camera_poses != None or camera_poses != []:
            self.setup_scene(data=self.cameras.camera_poses)
        
            
        if to_world_coords_matrix != []:
            self.has_origin = self.has_scale = True

        #   print("fix matrix")
        #   to_world_coords_matrix = np.eye(4).tolist()
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
            # print("fps", self.fps)
        self.last_time = time_now

    @Slot(dict)
    def setData(self, data):
        # if data != {}:
        #     print(data)
        if self.collecting_points and "image-points" in data:
            self.captured_points_for_pose.append(data.get("image-points"))

            self.calculate_pose.setText(
                "calculate with " + str(len(self.captured_points_for_pose)) + " points"
            )
        # todo have to find way to append data in smart way
        if "object_points" in data:
            objects = data.get("object_points")[0]
            self.object_points.append(objects)
            if len(objects) == 2:
                print(math.dist(objects[0],objects[1]))
        if self.is_triangulating_points and "object_points" in data:
            self.gl_widget.points_list = []
            self.gl_widget.point_colors = []
            self.gl_widget.point_size = 3

            # objects = data.get("object_points")[0]
            # self.object_points.append(objects)
            for object_pos in objects:

                self.gl_widget.add_point(position=object_pos, size=3)
            self.update_enabled_states()
        if "camera_poses" in data:
            self.cameras.camera_poses = data.get("camera_poses")
            self.setup_scene(data=self.cameras.camera_poses)
            # TODO join setup_scene in camera and world if statements
            self.update_enabled_states()
        if "to_world_coords_matrix" in data:
            self.cameras.to_world_coords_matrix = data.get("to_world_coords_matrix")
            self.setup_scene(data=self.cameras.camera_poses)
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
