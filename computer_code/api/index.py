from helpers import camera_pose_to_serializable, calculate_reprojection_errors, bundle_adjustment, Cameras, triangulate_points, essential_from_fundamental, motion_from_essential
import cv2 as cv
import numpy as np
from scipy import linalg
import json
from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2
import imutils
from threading import Lock
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
        self._running = True
        self._lock = self.mutex()


    def set_resolution(self, height, width):
        RuntimeWarning("not implemented")

    def run(self):
        cameras = Cameras.instance()
        cameras.set_num_objects(num_objects)
        output = self.camera_stream()
        while self._running:

            try:
                image, data= next(output)
                frame = self.cvimage_to_label(image)
                self.frame_signal.emit(frame)
                self.data_signal.emit(data)
                
                self.msleep(10)  # avoid busy loop
                
            except StopIteration:
                pass
    def enable(self):
        self._running = True
    def stop(self):
        self._running = False

    def mutex(self):
        # Simple cross-thread lock for PyQt5 QThread
        return Lock()

    def cvimage_to_label(self, image):
        image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image

    def camera_stream(self):
        cameras = Cameras.instance()
        cameras.set_num_objects(num_objects)
        self.i = 0
        def gen(cameras):
            while True:
                yield cameras.get_frames()
          
        # TODO return fps
        return gen(cameras)





    # @socketio.on("acquire-floor")
    def acquire_floor(self,object_points):
        cameras = Cameras.instance()
        # object_points = data["objectPoints"]
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

        # R = R @ [[1,0,0],[0,-1,0],[0,0,1]] # i dont fucking know why
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
        self.data_signal.emit({"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})

        # socketio.emit("to-world-coords-matrix", {"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})

    # @socketio.on("acquire-floor")

    def set_origin(self,object_point, toWorldCoordsMatrix):
        cameras = Cameras.instance()

        object_point = np.array(object_point)
        to_world_coords_matrix = np.array(toWorldCoordsMatrix)
        transform_matrix = np.eye(4)

        # object_point[1], object_point[2] = object_point[2], object_point[1] # i dont fucking know why
        transform_matrix[:3, 3] = -object_point

        to_world_coords_matrix = transform_matrix @ to_world_coords_matrix
        cameras.to_world_coords_matrix = to_world_coords_matrix
        self.data_signal.emit({"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})
        
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

    def calculate_camera_pose(self,data):
        cameras = Cameras.instance()
        image_points = np.array(data["cameraPoints"])
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
        # TODO is there any point to run this calculate_reprojection_errors if output is not used? likely causing slow down 
        object_points = triangulate_points(image_points, camera_poses)
        error = np.mean(calculate_reprojection_errors(image_points, object_points, camera_poses))
        self.data_signal.emit({"camera_poses": camera_pose_to_serializable(camera_poses)})
        
        # return camera_poses, output_data
        # socketio.emit("camera-pose", {"camera_poses": camera_pose_to_serializable(camera_poses)})
    # @profile
    # @socketio.on("locate-objects")
    def start_or_stop_locating_objects(self,start_or_stop):
        cameras = Cameras.instance()
        # start_or_stop = data["startOrStop"]

        if (start_or_stop == "start"):
            cameras.start_locating_objects()
            return
        elif (start_or_stop == "stop"):
            cameras.stop_locating_objects()
    # @profile
    # @socketio.on("determine-scale")
    def determine_scale(self,object_points, camera_poses):
        # object_points = data["objectPoints"]
        # camera_poses = data["cameraPoses"]
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
        self.data_signal.emit({"error": None, "camera_poses": camera_poses})
        # return (camera_poses)
    
        # socketio.emit("camera-pose", {"error": None, "camera_poses": camera_poses})

    # @profile
    # @socketio.on("triangulate-points")
    def live_mocap(self,start_or_stop, camera_poses, to_world_coords_matrix):
        cameras = Cameras.instance()
        # start_or_stop = data["startOrStop"]
        # camera_poses = data["cameraPoses"]
        cameras.to_world_coords_matrix = to_world_coords_matrix

        if (start_or_stop == "start"):
            cameras.start_trangulating_points(camera_poses)
            return
        elif (start_or_stop == "stop"):
            cameras.stop_trangulating_points()
    
    def update_camera_params(self, filename):
        cameras = Cameras.instance()
        f = open(filename)
        data = json.load(f)
        cameras.camera_params = data["camera-params"]
        cameras.configure()
        print(cameras.camera_params)
        cameras.to_world_coords_matrix = data["to_world_coords_matrix"]
        cameras.camera_poses = data["camera_poses"]
        self.data_signal.emit({ "camera_poses": cameras.camera_poses})

        # TODO how do we do camera poses 

