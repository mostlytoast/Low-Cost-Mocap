from helpers import camera_pose_to_serializable, calculate_reprojection_errors, bundle_adjustment, Cameras, triangulate_points, essential_from_fundamental, motion_from_essential
# from KalmanFilter import KalmanFilter

from flask import Flask, Response, request
import cv2 as cv
import numpy as np
# import numpy.linalg as nplinalg
import json
# from scipy import linalg
# from scipy.spatial.transform import Rotation as ROTTT
from scipy import linalg
from flask_socketio import SocketIO
# import copy
import time
# import serial
import threading
# from ruckig import InputParameter, OutputParameter, Result, Ruckig
from flask_cors import CORS
import json
# from scipy.stats import zscore
from line_profiler import profile
serialLock = threading.Lock()
from skspatial.objects import Plane, Points

# ser = serial.Serial("/dev/cu.usbserial-02X2K2GE", 1000000, write_timeout=1, )

from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2
import imutils
from threading import Lock
import index
"""_summary_ separate thread to get video from webcam 

Returns:
    _type_: _description_ signal image 
"""
cameras_init = False

num_objects = 2
class MyThread(QThread):
    frame_signal = Signal(QImage)
    data_signal = Signal(dict)
    def __init__(self):
        super().__init__()
    
        self.cap = None
        self._running = True
        self._lock = self.mutex()
        self._pending_camera_id = None
        self.index_instance = index

    def set_camera_id(self, camera_id):
        with self._lock:
            self._pending_camera_id = camera_id

    def set_resolution(self, height, width):
        RuntimeWarning("not implemented")

    def run(self):
        
        # self.cap = cv2.VideoCapture(self.camera_id)
        while self._running:
            # with self._lock:
            #     if self._pending_camera_id is not None:
            #         if self.cap is not None and self.cap.isOpened():
            #             self.cap.release()
            #         self.camera_id = self._pending_camera_id
            #         self.cap = cv2.VideoCapture(self.camera_id)
            #         self._pending_camera_id = None

            # if self.cap is not None and self.cap.isOpened():
            #     # ret, frame = self.cap.read()
            #     # if ret:
           
            try:
                output= self.camera_stream()
                image, data= next(output)
                # print(data)
                frame = self.cvimage_to_label(image)
                self.frame_signal.emit(frame)
                self.data_signal.emit(data)
            except StopIteration:
                pass
            self.msleep(10)  # avoid busy loop
    def enable(self):
        self._running = True
    def stop(self):
        self._running = False
        # if self.cap is not None and self.cap.isOpened():
        #     self.cap.release()

    def mutex(self):
        # Simple cross-thread lock for PyQt5 QThread
        return Lock()

    def cvimage_to_label(self, image):
        image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image
# from engineio.async_drivers import gevent
# socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')


    def camera_stream(self):
        cameras = Cameras.instance()
        # cameras.set_socketio(socketio)
        # cameras.set_ser(ser)
        # cameras.set_serialLock(serialLock)
        cameras.set_num_objects(num_objects)
        
        def gen(cameras):
            frequency = 150
            loop_interval = 1.0 / frequency
            last_run_time = 0
            i = 0
            fps = 0
            while True:
                time_now = time.time()

                i = (i+1)%10
                if i == 0:
                    fps = round(1/(time_now - last_run_time))
                    # socketio.emit("fps", {"fps": fps })

                if time_now - last_run_time < loop_interval:
                    time.sleep(last_run_time - time_now + loop_interval)
                last_run_time = time.time()
                frames, data = cameras.get_frames()
                # jpeg_frame = cv.imencode('.jpg', frames)[1].tostring()
                yield frames, data
                # yield (b'--frame\r\n'
                #     b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame + b'\r\n')
        # TODO return fps
        return gen(cameras)


    # def acquire_floor(data):
    #     cameras = Cameras.instance()
    #     object_points = data["objectPoints"]
    #     object_points = np.array([item for sublist in object_points for item in sublist])
    #     print("\nobject_points",object_points.tolist())
    #     print("cameras.to_world_coords_matrix",cameras.to_world_coords_matrix )

    #     temp_points = []
    #     for temp_obj in object_points:
    #         # object_point[1], object_point[2] = object_point[2], object_point[1] # i dont fucking know why

    #         temp_obj[1], temp_obj[2] = temp_obj[2], temp_obj[1]
    #         temp_points.append([temp_obj[0], temp_obj[1], temp_obj[2]])

    #     points = Points(temp_points)
    #     plane = Plane.best_fit(points)
    #     # Get the normal vector and a point on the plane
    #     plane_normal = plane.normal
    #     plane_point = plane.point
    #     #https://mattloftus.github.io/2016/01/23/threejs-p1/
    #     # The floor of the coordinate space is assumed to be y=0, normal [0,1,0]
    #     floor_normal = np.array([0, 1,0])
    #     floor_point = np.array([0, 0, 0])

    #     # Compute rotation to align plane_normal to floor_normal
    #     v = np.cross(plane_normal, floor_normal)
    #     c = np.dot(plane_normal, floor_normal)
    #     if np.linalg.norm(v) < 1e-8:
    #         R = np.eye(3)
    #     else:
    #         vx = np.array([[0, -v[2], v[1]],
    #                        [v[2], 0, -v[0]],
    #                        [-v[1], v[0], 0]])
    #         R = np.eye(3) + vx + vx @ vx * ((1 - c) / (np.linalg.norm(v) ** 2))

    #     # Compute translation to move plane_point onto the floor (y=0 after rotation)
    #     rotated_plane_point = R @ plane_point
    #     translation = floor_point - rotated_plane_point

    #     # Build 4x4 transformation matrix
    #     new_to_world_coords_matrix = np.eye(4)
    #     new_to_world_coords_matrix[:3, :3] = R
    #     new_to_world_coords_matrix[:3, 3] = translation
    #     # Swap y and z axes in the transformation matrix
    #     # swap_yz = np.array([
    #     #     [1, 0, 0, 0],
    #     #     [0, 0, 1, 0],
    #     #     [0, 1, 0, 0],
    #     #     [0, 0, 0, 1]
    #     # ])
    #     # new_to_world_coords_matrix = new_to_world_coords_matrix @ swap_yz

    

    #     # Swap y and z axes in the transformation matrix
    #     swap_yz = np.array([
    #         [1, 0, 0, 0],
    #         [0, 0, 1, 0],
    #         [0, 1, 0, 0],
    #         [0, 0, 0, 1]
    #     ])
    #     new_to_world_coords_matrix = new_to_world_coords_matrix @ swap_yz
        
        
    #     # perm = [0, 2, 1, 3]
    #     # cameras.to_world_coords_matrix = cameras.to_world_coords_matrix[perm, :][:, perm]
    
        
    #     cameras.to_world_coords_matrix =  cameras.to_world_coords_matrix @ new_to_world_coords_matrix
    #     # cameras.to_world_coords_matrix = new_to_world_coords_matrix
    #     # Convert the 3x3 matrix to a 4x4 matrix for proper multiplication
    #     swap_yz_4x4 = np.eye(4)
    #     swap_yz_4x4[:3, :3] = np.array([[1,0,0],[0,-1,0],[0,0,1]])
    #     cameras.to_world_coords_matrix = cameras.to_world_coords_matrix @ swap_yz_4x4 # i dont fucking know why
        
    #     print("new_to_world_coords_matrix",new_to_world_coords_matrix.tolist())
        
    #     socketio.emit("to-world-coords-matrix", {"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})



    # @socketio.on("acquire-floor")
    def acquire_floor(self,data):
        cameras = Cameras.instance()
        object_points = data["objectPoints"]
        object_points = np.array([item for sublist in object_points for item in sublist])

        tmp_A = []
        tmp_b = []
        for i in range(len(object_points)):
            tmp_A.append([object_points[i,0], object_points[i,1], 1])
            tmp_b.append(object_points[i,2])
        b = np.matrix(tmp_b).T
        A = np.matrix(tmp_A)

        fit, residual, rnk, s = linalg.lstsq(A, b)
        fit = fit.T[0]

        plane_normal = np.array([[fit[0]], [fit[1]], [-1]])
        plane_normal = plane_normal / linalg.norm(plane_normal)
        up_normal = np.array([[0],[0],[1]], dtype=np.float32)

        plane = np.array([fit[0], fit[1], -1, fit[2]])

        # https://math.stackexchange.com/a/897677/1012327
        G = np.array([
            [np.dot(plane_normal.T,up_normal)[0][0], -linalg.norm(np.cross(plane_normal.T[0],up_normal.T[0])), 0],
            [linalg.norm(np.cross(plane_normal.T[0],up_normal.T[0])), np.dot(plane_normal.T,up_normal)[0][0], 0],
            [0, 0, 1]
        ])
        F = np.array([plane_normal.T[0], ((up_normal-np.dot(plane_normal.T,up_normal)[0][0]*plane_normal)/linalg.norm((up_normal-np.dot(plane_normal.T,up_normal)[0][0]*plane_normal))).T[0], np.cross(up_normal.T[0],plane_normal.T[0])]).T
        R = F @ G @ linalg.inv(F)

        R = R @ [[1,0,0],[0,-1,0],[0,0,1]] # i dont fucking know why
        # Remove translation component from R by ensuring it's a pure rotation matrix
        U, _, Vt = np.linalg.svd(R[:3, :3])
        R = U @ Vt
        # # Swap y and z axes in the rotation matrix
        # swap_yz = np.array([
        #     [1, 0, 0],
        #     [0, 0, 1],
        #     [0, 1, 0]
        # ])
        # R = R @ swap_yz
        cameras.to_world_coords_matrix = np.array(np.vstack((np.c_[R, [0,0,0]], [[0,0,0,1]])))

        # socketio.emit("to-world-coords-matrix", {"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})

    # @socketio.on("acquire-floor")

    def set_origin(self,data):
        cameras = Cameras.instance()

        object_point = np.array(data["objectPoint"])
        to_world_coords_matrix = np.array(data["toWorldCoordsMatrix"])
        transform_matrix = np.eye(4)

        object_point[1], object_point[2] = object_point[2], object_point[1] # i dont fucking know why
        transform_matrix[:3, 3] = -object_point

        to_world_coords_matrix = transform_matrix @ to_world_coords_matrix
        cameras.to_world_coords_matrix = to_world_coords_matrix

        # socketio.emit("to-world-coords-matrix", {"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})
    # @profile
    # @socketio.on("update-camera-settings")
    def change_camera_settings(self,data):
        cameras = Cameras.instance()
        
        cameras.edit_settings(data["exposure"], data["gain"])
    # @profile
    # @socketio.on("capture-points")
    def capture_points(self,data):
        start_or_stop = data["startOrStop"]
        cameras = Cameras.instance()

        if (start_or_stop == "start"):
            cameras.start_capturing_points()
            # socketio.emit("object-points", {
            #                 "object_points":[0,0,1]
                        
            #             })
            return
        elif (start_or_stop == "stop"):
            cameras.stop_capturing_points()
    # @profile
    # @socketio.on("calculate-camera-pose")
    def calculate_camera_pose(self,data):
        cameras = Cameras.instance()
        image_points = np.array(data["cameraPoints"])
        # Save image_points to a file
    
        image_points_t = image_points.transpose((1, 0, 2))

        camera_poses = [{
            "R": np.eye(3),
            "t": np.array([[0],[0],[0]], dtype=np.float32)
        }]
        for camera_i in range(0, cameras.num_cameras-1):
            camera1_image_points = image_points_t[camera_i]
            camera2_image_points = image_points_t[camera_i+1]
            not_none_indicies = np.where(np.all(camera1_image_points != None, axis=1) & np.all(camera2_image_points != None, axis=1))[0]
            camera1_image_points = np.take(camera1_image_points, not_none_indicies, axis=0).astype(np.float32)
            camera2_image_points = np.take(camera2_image_points, not_none_indicies, axis=0).astype(np.float32)

            F, _ = cv.findFundamentalMat(camera1_image_points, camera2_image_points, cv.FM_RANSAC, 1, 0.99999)
            E = essential_from_fundamental(F, cameras.get_camera_params(0)["intrinsic_matrix"], cameras.get_camera_params(1)["intrinsic_matrix"])
            possible_Rs, possible_ts = motion_from_essential(E)

            R = None
            t = None
            max_points_infront_of_camera = 0
            for i in range(0, 4):
                object_points = triangulate_points(np.hstack([np.expand_dims(camera1_image_points, axis=1), np.expand_dims(camera2_image_points, axis=1)]), np.concatenate([[camera_poses[-1]], [{"R": possible_Rs[i], "t": possible_ts[i]}]]))
                object_points_camera_coordinate_frame = np.array([possible_Rs[i].T @ object_point for object_point in object_points])

                points_infront_of_camera = np.sum(object_points[:,2] > 0) + np.sum(object_points_camera_coordinate_frame[:,2] > 0)

                if points_infront_of_camera > max_points_infront_of_camera:
                    max_points_infront_of_camera = points_infront_of_camera
                    R = possible_Rs[i]
                    t = possible_ts[i]

            R = R @ camera_poses[-1]["R"]
            t = camera_poses[-1]["t"] + (camera_poses[-1]["R"] @ t)

            camera_poses.append({
                "R": R,
                "t": t
            })

        camera_poses, output_data = bundle_adjustment(image_points, camera_poses)
        # todo what to do with output_data
        object_points = triangulate_points(image_points, camera_poses)
        error = np.mean(calculate_reprojection_errors(image_points, object_points, camera_poses))
        return camera_poses, output_data
        # socketio.emit("camera-pose", {"camera_poses": camera_pose_to_serializable(camera_poses)})
    # @profile
    # @socketio.on("locate-objects")
    def start_or_stop_locating_objects(self,data):
        cameras = Cameras.instance()
        start_or_stop = data["startOrStop"]

        if (start_or_stop == "start"):
            cameras.start_locating_objects()
            return
        elif (start_or_stop == "stop"):
            cameras.stop_locating_objects()
    # @profile
    # @socketio.on("determine-scale")
    def determine_scale(self,data):
        object_points = data["objectPoints"]
        camera_poses = data["cameraPoses"]
        actual_distance = 0.15
        observed_distances = []

        for object_points_i in object_points:
            if len(object_points_i) != 2:
                continue

            object_points_i = np.array(object_points_i)

            observed_distances.append(np.sqrt(np.sum((object_points_i[0] - object_points_i[1])**2)))

        scale_factor = actual_distance/np.mean(observed_distances)
        for i in range(0, len(camera_poses)):
            camera_poses[i]["t"] = (np.array(camera_poses[i]["t"]) * scale_factor).tolist()

        # socketio.emit("camera-pose", {"error": None, "camera_poses": camera_poses})

    # @profile
    # @socketio.on("triangulate-points")
    def live_mocap(self,data):
        cameras = Cameras.instance()
        start_or_stop = data["startOrStop"]
        camera_poses = data["cameraPoses"]
        cameras.to_world_coords_matrix = data["toWorldCoordsMatrix"]

        if (start_or_stop == "start"):
            cameras.start_trangulating_points(camera_poses)
            return
        elif (start_or_stop == "stop"):
            cameras.stop_trangulating_points()


if __name__ == '__main__':
    print()
    # socketio.run(app, port=3001, debug=True)