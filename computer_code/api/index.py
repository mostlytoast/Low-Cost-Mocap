from computer_code.api.helpers import camera_pose_to_serializable, calculate_reprojection_errors, bundle_adjustment, Cameras, triangulate_points, essential_from_fundamental, motion_from_essential
import cv2 as cv
import numpy as np
from scipy import linalg
import json
from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2
import imutils
from threading import Lock
from skspatial.objects import Plane, Points

cameras_init = False
num_objects = 2
class MyThread(QThread):
    """separate thread to handle camera input 

    Args:
        QThread (_type_): _description_

    Returns:
        _type_: _description_

    Yields:
        _type_: _description_
    """
    frame_signal = Signal(QImage)
    data_signal = Signal(dict)
    def __init__(self):
        super().__init__()
        self._running = True
        self._lock = self.mutex()

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
 
    def acquire_floor(self,object_points):
        cameras = Cameras.instance()
        # object_points = data["objectPoints"]
        object_points = np.array([item for sublist in object_points for item in sublist])
        print("\nobject_points",object_points.tolist())
        print("cameras.to_world_coords_matrix",cameras.to_world_coords_matrix )

        temp_points = []
        for temp_obj in object_points:
            # object_point[1], object_point[2] = object_point[2], object_point[1] # i dont fucking know why

            # temp_obj[1], temp_obj[2] = temp_obj[2], temp_obj[1]
            temp_points.append([temp_obj[0], temp_obj[1], temp_obj[2]])

        points = Points(temp_points)
        plane = Plane.best_fit(points)
        # Get the normal vector and a point on the plane
        plane_normal = plane.normal
        plane_point = plane.point
        #https://mattloftus.github.io/2016/01/23/threejs-p1/
        # The floor of the coordinate space is assumed to be y=0, normal [0,1,0]
        floor_normal = np.array([0, 0,1])
        floor_point = np.array([0, 0, 0])

        # Compute rotation to align plane_normal to floor_normal
        v = np.cross(plane_normal, floor_normal)
        c = np.dot(plane_normal, floor_normal)
        if np.linalg.norm(v) < 1e-8:
            R = np.eye(3)
        else:
            vx = np.array([[0, -v[2], v[1]],
                        [v[2], 0, -v[0]],
                        [-v[1], v[0], 0]])
            R = np.eye(3) + vx + vx @ vx * ((1 - c) / (np.linalg.norm(v) ** 2))

        # Compute translation to move plane_point onto the floor (y=0 after rotation)
        rotated_plane_point = R @ plane_point
        translation = floor_point - rotated_plane_point

        # Build 4x4 transformation matrix
        new_to_world_coords_matrix = np.eye(4)
        new_to_world_coords_matrix[:3, :3] = R
        new_to_world_coords_matrix[:3, 3] = translation
        rotate_180_x = np.array([
            [1,  0,  0, 0],
            [0, -1,  0, 0],
            [0,  0, -1, 0],
            [0,  0,  0, 1]
        ])
        new_to_world_coords_matrix = rotate_180_x @ new_to_world_coords_matrix
        cameras.to_world_coords_matrix =  cameras.to_world_coords_matrix @ new_to_world_coords_matrix
        self.data_signal.emit({"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})
        
    def set_origin(self,object_point, toWorldCoordsMatrix):
        if toWorldCoordsMatrix == []:
            toWorldCoordsMatrix = np.eye(4).tolist()
        cameras = Cameras.instance()

        object_point = np.array(object_point)
        to_world_coords_matrix = np.array(toWorldCoordsMatrix)
        transform_matrix = np.eye(4)
        transform_matrix[:3, 3] = -object_point
       
        to_world_coords_matrix = transform_matrix @ to_world_coords_matrix
        cameras.to_world_coords_matrix = to_world_coords_matrix
        self.data_signal.emit({"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})
        
    def change_camera_settings(self,data):
        cameras = Cameras.instance()
        
        cameras.edit_settings(data["exposure"], data["gain"])

    def capture_points(self,data):
        start_or_stop = data["startOrStop"]
        cameras = Cameras.instance()

        if (start_or_stop == "start"):
            cameras.start_capturing_points()
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
            if F is None or F.size == 0:
                RED = '\033[91m'  # ANSI code for red text
                RESET = '\033[0m' # ANSI code to reset formatting
                # TODO put proper error message for this in the gui 
                error_message = "Error: Unable to find a fundamental matrix, try again ensuring no points are obstructed!"
                error_type = "findFundamentalMat return None"
                print(f"{RED}{error_message}{RESET}")
                self.data_signal.emit({"error": error_type, "error_message":error_message})

                break
            # E = cv.sfm.essentialFromFundamental(F, cameras.get_camera_params(0)["intrinsic_matrix"], cameras.get_camera_params(1)["intrinsic_matrix"])
            E = essential_from_fundamental(F, cameras.get_camera_params(0)["intrinsic_matrix"], cameras.get_camera_params(1)["intrinsic_matrix"])
            possible_Rs, possible_ts = motion_from_essential(E)
            # possible_Rs, possible_ts = cv.sfm.motionFromEssential(E)

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
        
    def start_or_stop_locating_objects(self,start_or_stop):
        cameras = Cameras.instance()
        if (start_or_stop == "start"):
            cameras.start_locating_objects()
            return
        elif (start_or_stop == "stop"):
            cameras.stop_locating_objects()
 
    def determine_scale(self,object_points, camera_poses):
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
 
    def live_mocap(self,start_or_stop, camera_poses, to_world_coords_matrix):
        cameras = Cameras.instance()
        cameras.to_world_coords_matrix = to_world_coords_matrix

        if (start_or_stop == "start"):
            cameras.start_trangulating_points(camera_poses)
            return
        elif (start_or_stop == "stop"):
            cameras.stop_trangulating_points()

    def update_camera_params(self,camera_params):
        cameras = Cameras.instance()
        cameras.camera_params = camera_params
        cameras.configure()
  
