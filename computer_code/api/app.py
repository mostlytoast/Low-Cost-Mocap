import sys

# import json
# import requests
# import socketio
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QGridLayout,
)

# import cameraThread
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QPixmap, QImage
import index

from viewer3d import QGLControllerWidget

import calibrationWidget
import moderngl
from PyQt5 import QtOpenGL, QtWidgets, QtCore
# import numpy as np
import openmesh as om
# from pyrr import Matrix44

from ArcBall import ArcBallUtil
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Low-Cost Mocap PyQt")
        # try:
        #     self.sio = socketio.Client()
        #     self.sio.connect('http://localhost:3001')
        # except:
        #     None
        # state variables
        self.camera_stream_running = False
        self.camera_stream_thread = None
        self.has_world_calibration = False
        self.has_collected_points = False
        self.collecting_points = False
        self.is_triangulating_points = False
        #data variables 
        self.captured_points_for_pose = []
        self.camera_poses = []
        self.object_points = []
        self.to_world_coords_matrix = [[0.9941338485260931,0.0986512964608827,-0.04433748889242502,0.9938296704767513],[-0.0986512964608827,0.659022672138982,-0.7456252673517598,2.593331619023365],[0.04433748889242498,-0.7456252673517594,-0.6648888236128887,2.9576262456228286],[0,0,0,1]]

        self.camera_thread = index.MyThread()
        self.camera_thread.frame_signal.connect(self.setImage)
        self.camera_thread.data_signal.connect(self.setData)

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        self.init_ui()
        self.resize(640, 480)
        self.gl_widget = QGLControllerWidget(self)
        self.gl_widget.setMinimumSize(640,100)
        self.layout.addWidget(self.gl_widget)
        # self.setCentralWidget(self.gl_widget)
        self.menu = self.menuBar().addMenu("&File")
        self.menu.addAction('&Open', self.openFile)
        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
        timer.timeout.connect(self.gl_widget.updateGL)
        timer.start()
        # wait till window exists to create grid (will error out other wise)
        QtCore.QTimer.singleShot(0, self.gl_widget.create_grid)
        QtCore.QTimer.singleShot(0, self.test)

        # QtCore.QTimer.singleShot(0, self.setup_scene)

        # 
        # 
        # self.register_socket_handlers()
    def test(self):
        self.gl_widget.add_point([1,2,3])
        self.gl_widget.add_point([1,0,3])
        self.gl_widget.add_point([1,5,3])

    def init_ui(self):
        
        # Camera Stream Viewer
        self.camera_stream_label = QLabel("Camera Stream")
        self.camera_stream_label.setFixedHeight(300)
        self.camera_stream_label.setAlignment(Qt.AlignCenter)
        self.toggle_stream_btn = QPushButton("Start Camera Stream")
        self.toggle_stream_btn.clicked.connect(self.toggle_camera_stream)
        self.layout.addWidget(self.camera_stream_label)
        self.layout.addWidget(self.toggle_stream_btn)

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
        self.layout.addLayout(camera_group)

        self.tracking_group = QGridLayout()
        self.tracking_group.addWidget(QLabel("tracking settings"), 0, 0)
        self.tracking_group.addWidget(QLabel("Live triangulation"), 1, 0)
        self.live_triangulation = QPushButton("start")
        self.live_triangulation.clicked.connect(self.toggle_live_triangulation)
        self.live_triangulation.setEnabled(False)

        self.tracking_group.addWidget(self.live_triangulation, 1, 1)
        self.tracking_group.addWidget(QLabel("Locate Objects"), 2, 0)
        self.locate_objects = QPushButton("start")
        self.locate_objects.clicked.connect(self.toggle_locate_objects)
        self.locate_objects.setEnabled(False)

        self.tracking_group.addWidget(self.locate_objects, 2, 1)
        self.tracking_group.addWidget(QLabel("set Scale Using Points"), 3, 0)
        self.set_scale = QPushButton("start")
        self.set_scale.clicked.connect(self.toggle_set_scale)
        self.set_scale.setEnabled(False)

        self.tracking_group.addWidget(self.set_scale, 3, 1)
        self.tracking_group.addWidget(QLabel("Acquire floor"), 4, 0)
        self.acquire_floor = QPushButton("start")
        self.acquire_floor.clicked.connect(self.toggle_acquire_floor)
        self.acquire_floor.setEnabled(False)

        self.tracking_group.addWidget(self.acquire_floor, 4, 1)
        self.tracking_group.addWidget(QLabel("set origin"), 5, 0)
        self.set_origin = QPushButton("start")
        self.set_origin.clicked.connect(self.toggle_set_origin)
        self.set_origin.setEnabled(False)

        self.tracking_group.addWidget(self.set_origin, 5, 1)
        self.tracking_group.addWidget(
            QLabel("Collect points for camera pose calibration"), 6, 0
        )
        self.collect_points = QPushButton("start")
        self.collect_points.clicked.connect(self.toggle_collect_points)
        self.collect_points.setEnabled(False)
        self.tracking_group.addWidget(self.collect_points, 6, 1)

        self.calculate_pose = QPushButton("calculate camera pose with 0 points")
        self.calculate_pose.clicked.connect(self.toggle_calculate_pose)
        self.calculate_pose.setEnabled(False)
        self.tracking_group.addWidget(self.calculate_pose, 7, 1)

        self.layout.addLayout(self.tracking_group)



        with open("computer_code/api/style.css") as style:
            self.styleText = style.read()
            self.setStyleSheet(self.styleText)
            
        # self.view = QVBoxLayout()
        # # self.view.setFixedHeight(300)
        # # self.view.setAlignment(Qt.AlignCenter)
        # self.gl_widget = QGLControllerWidget(self)
        # self.view.addWidget(self.gl_widget)

        # self.layout.addLayout(self.view)
        # timer = QtCore.QTimer(self)
        # timer.setInterval(20)  # period, in milliseconds
        # timer.timeout.connect(self.gl_widget.updateGL)
        # timer.start()
        # fname = "/home/tom/Projects/new-Low-Cost-Mocap/Low-Cost-Mocap/teapot.obj"
        # mesh = om.read_trimesh(fname)
        # self.gl_widget.set_mesh(mesh)
        
        # 

        
        
        # self.setCentralWidget(central_widget)
    def setup_scene(self,data):
        self.gl_widget.camera_vertices_list =[]
        for camera_transform in data:
            # todo apply the world transform to this 
            
            self.gl_widget.add_camera(transform=camera_transform)
        
        

    # Function to get camera config
    def openFile(self):
        # TODO have to find way for this ro
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open file', '', "Camera Configuration files (*.txt)")
        with open(fname[0],"r") as f:
            self.config_data = f.read()
        # todo might want to clear scene before hand?
        # self.setup_scene()
        # mesh = om.read_trimesh(fname[0])
        # self.gl_widget.set_mesh(mesh)
        # self.gl_widget.create_grid()

        # self.setLayout(self.layout)

    def toggle_live_triangulation(self):
        if not self.is_triangulating_points:
            # self.captured_points_for_pose= []
            # self.camera_thread.live_mocap({"startOrStop": "start"})
            self.camera_thread.live_mocap({"startOrStop": "start","cameraPoses":self.camera_poses,"toWorldCoordsMatrix":self.to_world_coords_matrix})

            self.is_triangulating_points = True
            self.update_enabled_states()
            self.live_triangulation.setText("Stop")


        else:
            self.live_triangulation.setText("Start")
            self.camera_thread.live_mocap({"startOrStop": "stop","cameraPoses":self.camera_poses,"toWorldCoordsMatrix":self.to_world_coords_matrix})
            self.is_triangulating_points = False
            self.update_enabled_states()

        #         <Button
        #           size='sm'
        #           variant={isTriangulatingPoints ? "outline-danger" : "outline-primary"}
        #           disabled={!cameraStreamRunning}
        #           onClick={() => {
        #             if (!isTriangulatingPoints) {
        #               objectPoints.current = []
        #               // plane.current=[]
        #               objectPointErrors.current = []
        #               objects.current = []
        #               filteredObjects.current = []
        #               droneSetpointHistory.current = []
        #             }
        #             setIsTriangulatingPoints(!isTriangulatingPoints);
        #             startLiveMocap(isTriangulatingPoints ? "stop" : "start");
        #           }
        #           }>
        #           {isTriangulatingPoints ? "Stop" : "Start"}
        #         </Button>
#          const startLiveMocap = (startOrStop: string) => {
#     socket.emit("triangulate-points", { startOrStop, cameraPoses, toWorldCoordsMatrix })
#   }

    def toggle_locate_objects(self):
        print()
        # setIsLocatingObjects(!isLocatingObjects);
        # self.sio.emit("locate-objects", { startOrStop: isLocatingObjects ? "stop" : "start" })

    def toggle_set_scale(self):
        print()

    def toggle_acquire_floor(self):
        print()

    def toggle_set_origin(self):
        print()

    def toggle_collect_points(self):
        if not self.collecting_points:
            self.captured_points_for_pose= []
            self.camera_thread.capture_points({"startOrStop": "start"})
            self.collecting_points = True
            self.update_enabled_states()
    
            self.collect_points.setText("Stop")


        else:
            self.collect_points.setText("Start")
            self.camera_thread.capture_points({"startOrStop": "stop"})
            self.collecting_points = False
            self.update_enabled_states()

        # <Row>
        #   <Col xs="auto">
        #     <h4></h4>
        #   </Col>
        #   <Col>
        #     <Tooltip id="collect-points-for-pose-button-tooltip" />
        #     <a data-tooltip-hidden={cameraStreamRunning} data-tooltip-variant='error' data-tooltip-id='collect-points-for-pose-button-tooltip' data-tooltip-content="Start camera stream first">
        #       <Button
        #         size='sm'
        #         variant={capturingPointsForPose ? "outline-danger" : "outline-primary"}
        #         disabled={!cameraStreamRunning}
        #         onClick={() => {
        #           setCapturingPointsForPose(!capturingPointsForPose);
        #           capturePointsForPose(capturingPointsForPose ? "stop" : "start");
        #         }
        #         }>
        #         {capturingPointsForPose ? "Stop" : "Start"}
        #       </Button>
        #     </a>
        #   </Col>
        # </Row>
        #               const capturePointsForPose = async (startOrStop: string) => {
        #     if (startOrStop === "start") {
        #       setCapturedPointsForPose("")
        #     }
        #     socket.emit("capture-points", { startOrStop })
        #   }
        """_summary_ function to update if points for camera pose state and update whats tied to that variable (buttons)

        Args:
            state (bool): if that state is active
        """
        # self.has_collected_points = True
        self.update_enabled_states()
      

    def toggle_calculate_pose(self):
        # <Button
        #           size='sm'
        #           className='float-end'
        #           variant="outline-primary"
        #           disabled={!(isValidJson(`[${capturedPointsForPose.slice(0, -1)}]`) && JSON.parse(`[${capturedPointsForPose.slice(0, -1)}]`).length !== 0)}
        #           onClick={() => {
        #             calculateCameraPose(JSON.parse(`[${capturedPointsForPose.slice(0, -1)}]`))
        #           }}>
        #           Calculate Camera Pose with {isValidJson(`[${capturedPointsForPose.slice(0, -1)}]`) ? JSON.parse(`[${capturedPointsForPose.slice(0, -1)}]`).length : 0} points
        #         </Button>
        #   const calculateCameraPose = async (cameraPoints: Array<Array<Array<number>>>) => {
#     socket.emit("calculate-camera-pose", { cameraPoints })
        # TODO stop point capture (disable button)
        self.collecting_points = False
        self.has_world_calibration = True
        # send data to calculate_camera_pose
        self.camera_poses, output_data = self.camera_thread.calculate_camera_pose({"cameraPoints":self.captured_points_for_pose})
        
        print("camera pose",self.camera_poses, output_data)
        self.update_enabled_states()
        self.setup_scene(self.camera_poses)
#   }


    def update_camera_settings(self):
        exposure = self.exposure_slider.value()
        gain = self.gain_slider.value()

        self.camera_thread.change_camera_settings({"exposure": exposure, "gain": gain})
        self.update_enabled_states()
    def toggle_camera_stream(self):

        # TODO cant start then stop camera stream causes paused image
        if not self.camera_stream_running:
            self.camera_stream_running = True
            self.update_enabled_states()
            self.toggle_stream_btn.setText("Stop Camera Stream")
            self.camera_thread.start()
            self.camera_thread.enable()
            self.update_enabled_states()
        else:
            self.camera_stream_running = False
            self.update_enabled_states()
            self.camera_thread.stop()
            self.toggle_stream_btn.setText("Start Camera Stream")
            self.update_enabled_states()

    # def update_has_collected_points(self,state):

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
            self.camera_stream_running and self.has_world_calibration
        )

        self.collect_points.setEnabled(self.camera_stream_running)
       


        self.calculate_pose.setEnabled(
            len(self.captured_points_for_pose)>0
        )
        # self.tracking_group.setEnabled(False)

   
    @Slot(QImage)
    def setImage(self, image):
        self.camera_stream_label.setPixmap(QPixmap.fromImage(image))
    @Slot(dict)
    def setData(self,data):
        print("im getting data",data)
        if self.collecting_points and "image-points" in data:
            self.captured_points_for_pose.append(data.get("image-points"))
            # print(len(self.captured_points_for_pose))
            self.calculate_pose.setText("calculate camera pose with "+str(len(self.captured_points_for_pose))+" points")
        # todo have to find way to append data in smart way 
        if self.is_triangulating_points and "object_points" in data:
            objects =  data.get("object_points")[0]
            self.object_points.append(objects)
            for object_pos in objects:

                self.gl_widget.add_point(object_pos)

        # im getting data {'object_points': ([],), 'errors': ([],), 'objects': ([],), 'filtered_objects': []}

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
