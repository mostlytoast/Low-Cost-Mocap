from helpers import camera_pose_to_serializable, calculate_reprojection_errors, bundle_adjustment, Cameras, triangulate_points, essential_from_fundamental, motion_from_essential
from KalmanFilter import KalmanFilter

from flask import Flask, Response, request
import cv2 as cv
import numpy as np
import numpy.linalg as nplinalg
import json
from scipy import linalg
from scipy.spatial.transform import Rotation as ROTTT

from flask_socketio import SocketIO
import copy
import time
# import serial
import threading
from ruckig import InputParameter, OutputParameter, Result, Ruckig
from flask_cors import CORS
import json
from scipy.stats import zscore

serialLock = threading.Lock()

# ser = serial.Serial("/dev/cu.usbserial-02X2K2GE", 1000000, write_timeout=1, )

app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins='*')

cameras_init = False

num_objects = 2

@app.route("/api/camera-stream")
def camera_stream():
    cameras = Cameras.instance()
    cameras.set_socketio(socketio)
    # cameras.set_ser(ser)
    cameras.set_serialLock(serialLock)
    cameras.set_num_objects(num_objects)
    
    def gen(cameras):
        frequency = 150
        loop_interval = 1.0 / frequency
        last_run_time = 0
        i = 0

        while True:
            time_now = time.time()

            i = (i+1)%10
            if i == 0:
                socketio.emit("fps", {"fps": round(1/(time_now - last_run_time))})

            if time_now - last_run_time < loop_interval:
                time.sleep(last_run_time - time_now + loop_interval)
            last_run_time = time.time()
            frames = cameras.get_frames()
            jpeg_frame = cv.imencode('.jpg', frames)[1].tostring()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame + b'\r\n')

    return Response(gen(cameras), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/api/trajectory-planning", methods=["POST"])
def trajectory_planning_api():
    data = json.loads(request.data)

    waypoint_groups = [] # grouped by continuious movement (no stopping)
    for waypoint in data["waypoints"]:
        stop_at_waypoint = waypoint[-1]
        if stop_at_waypoint:
            waypoint_groups.append([waypoint[:3*num_objects]])
        else:
            waypoint_groups[-1].append(waypoint[:3*num_objects])
    
    setpoints = []
    for i in range(0, len(waypoint_groups)-1):
        start_pos = waypoint_groups[i][0]
        end_pos = waypoint_groups[i+1][0]
        waypoints = waypoint_groups[i][1:]
        setpoints += plan_trajectory(start_pos, end_pos, waypoints, data["maxVel"], data["maxAccel"], data["maxJerk"], data["timestep"])

    return json.dumps({
        "setpoints": setpoints
    })

def plan_trajectory(start_pos, end_pos, waypoints, max_vel, max_accel, max_jerk, timestep):
    otg = Ruckig(3*num_objects, timestep, len(waypoints))  # DoFs, timestep, number of waypoints
    inp = InputParameter(3*num_objects)
    out = OutputParameter(3*num_objects, len(waypoints))

    inp.current_position = start_pos
    inp.current_velocity = [0,0,0]*num_objects
    inp.current_acceleration = [0,0,0]*num_objects

    inp.target_position = end_pos
    inp.target_velocity = [0,0,0]*num_objects
    inp.target_acceleration = [0,0,0]*num_objects

    inp.intermediate_positions = waypoints

    inp.max_velocity = max_vel*num_objects
    inp.max_acceleration = max_accel*num_objects
    inp.max_jerk = max_jerk*num_objects

    setpoints = []
    res = Result.Working
    while res == Result.Working:
        res = otg.update(inp, out)
        setpoints.append(copy.copy(out.new_position))
        out.pass_to_input(inp)

    return setpoints

@socketio.on("arm-drone")
def arm_drone(data):
    global cameras_init
    if not cameras_init:
        return
    
    Cameras.instance().drone_armed = data["droneArmed"]
    for droneIndex in range(0, num_objects):
        serial_data = {
            "armed": data["droneArmed"][droneIndex],
        }
        with serialLock:
            # ser.write(f"{str(droneIndex)}{json.dumps(serial_data)}".encode('utf-8'))
            None
        
        time.sleep(0.01)

@socketio.on("set-drone-pid")
def arm_drone(data):
    serial_data = {
        "pid": [float(x) for x in data["dronePID"]],
    }
    with serialLock:
        # ser.write(f"{str(data['droneIndex'])}{json.dumps(serial_data)}".encode('utf-8'))
        time.sleep(0.01)

@socketio.on("set-drone-setpoint")
def arm_drone(data):
    serial_data = {
        "setpoint": [float(x) for x in data["droneSetpoint"]],
    }
    with serialLock:
        # ser.write(f"{str(data['droneIndex'])}{json.dumps(serial_data)}".encode('utf-8'))
        time.sleep(0.01)

@socketio.on("set-drone-trim")
def arm_drone(data):
    serial_data = {
        "trim": [int(x) for x in data["droneTrim"]],
    }
    with serialLock:
        # ser.write(f"{str(data['droneIndex'])}{json.dumps(serial_data)}".encode('utf-8'))
        time.sleep(0.01)


@socketio.on("acquire-floor")
def acquire_floor(data):
    cameras = Cameras.instance()
    object_points = data["objectPoints"]
    print("object_points",object_points)
    # Load object_points from file
    # with open("object_points.json", "r") as f:
    #     object_points = np.array(json.load(f))
    # print("object_points", object_points)
    object_points = np.array([item for sublist in object_points for item in sublist])
    # Remove outliers using z-score method

    # Compute z-scores for each coordinate
    z_scores = np.abs(zscore(object_points, axis=0, nan_policy='omit'))
    # Keep points where all coordinates are within 2.5 standard deviations
    inliers = np.all(z_scores < 2.5, axis=1)
    object_points = object_points[inliers]
    # Fit plane z = ax + by + c
    tmp_A = []
    tmp_b = []
    for i in range(len(object_points)):
        tmp_A.append([object_points[i, 0], object_points[i, 1], 1])
        tmp_b.append(object_points[i, 2])
    b = np.matrix(tmp_b).T
    A = np.matrix(tmp_A)
    fit = nplinalg.lstsq(A, b, rcond=None)[0]
    fit = np.array(fit).flatten()  # Ensure fit is a 1D array with 3 elements: [a, b, c]
    
    # Plane normal
    plane_normal = np.array([[fit[0]], [fit[1]], [-1]])
    plane_normal = plane_normal / nplinalg.norm(plane_normal)
    up_normal = np.array([[0], [0], [1]], dtype=np.float32)
    print("plane_normal ", plane_normal, " \n up_normal ", up_normal)

    # Find rotation matrix to align plane_normal to up_normal
    v = np.cross(plane_normal.T[0], up_normal.T[0])
    c = np.dot(plane_normal.T[0], up_normal.T[0])
    if nplinalg.norm(v) < 1e-8:
        R = np.eye(3)
    else:
        s = nplinalg.norm(v)
        k_mat = np.array([[0, -v[2], v[1]],
                          [v[2], 0, -v[0]],
                          [-v[1], v[0], 0]])
        R = np.eye(3) + k_mat + k_mat @ k_mat * ((1 - c) / (s ** 2))

    # Fix 90-degree misalignment by rotating around the X axis
    # rot_flip_y = np.array([[-1, 0, 0],
    #                        [0, 1, 0],
    #                        [0, 0, 1]])
    # R = rot_flip_y @ R
    # Swap z and x axis in the rotation matrix R
    swap_zx = np.array([[0, 0, 1],
                        [0, 1, 0],
                        [1, 0, 0]])
    R = swap_zx @ R
    cameras.to_world_coords_matrix = np.array(np.vstack((np.c_[R, [0, 0, 0]], [[0, 0, 0, 1]])))
    print(cameras.to_world_coords_matrix)
    socketio.emit("to-world-coords-matrix", {"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})
    socketio.emit("to-world-coords-matrix", {"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})


@socketio.on("set-origin")
def set_origin(data):
    cameras = Cameras.instance()
    object_point = np.array(data["objectPoint"])
    to_world_coords_matrix = np.array(data["toWorldCoordsMatrix"])
    transform_matrix = np.eye(4)

    object_point[1], object_point[2] = object_point[2], object_point[1] # i dont fucking know why
    transform_matrix[:3, 3] = -object_point

    to_world_coords_matrix = transform_matrix @ to_world_coords_matrix
    cameras.to_world_coords_matrix = to_world_coords_matrix

    socketio.emit("to-world-coords-matrix", {"to_world_coords_matrix": cameras.to_world_coords_matrix.tolist()})

@socketio.on("update-camera-settings")
def change_camera_settings(data):
    cameras = Cameras.instance()
    
    cameras.edit_settings(data["exposure"], data["gain"])

@socketio.on("capture-points")
def capture_points(data):
    start_or_stop = data["startOrStop"]
    cameras = Cameras.instance()

    if (start_or_stop == "start"):
        cameras.start_capturing_points()
        return
    elif (start_or_stop == "stop"):
        cameras.stop_capturing_points()

@socketio.on("calculate-camera-pose")
def calculate_camera_pose(data):
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

    camera_poses = bundle_adjustment(image_points, camera_poses, socketio)

    object_points = triangulate_points(image_points, camera_poses)
    error = np.mean(calculate_reprojection_errors(image_points, object_points, camera_poses))

    socketio.emit("camera-pose", {"camera_poses": camera_pose_to_serializable(camera_poses)})

@socketio.on("locate-objects")
def start_or_stop_locating_objects(data):
    cameras = Cameras.instance()
    start_or_stop = data["startOrStop"]

    if (start_or_stop == "start"):
        cameras.start_locating_objects()
        return
    elif (start_or_stop == "stop"):
        cameras.stop_locating_objects()

@socketio.on("determine-scale")
def determine_scale(data):
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

    socketio.emit("camera-pose", {"error": None, "camera_poses": camera_poses})


@socketio.on("triangulate-points")
def live_mocap(data):
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
    socketio.run(app, port=3001, debug=True)