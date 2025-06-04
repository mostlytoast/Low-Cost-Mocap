from helpers import find_camera_id
from videoSubSystem import *
import cv2
import numpy as np
import os

import subprocess
import os
import cv2  # OpenCV for image handling
import time
import json
import shutil

# todo document






# code based on https://github.com/jyjblrd/Low-Cost-Mocap/discussions/11#discussioncomment-9380283


def get_calibration_images(camera_id, width, height):
    """_summary_ takes and saves images to path"""
    images = []
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(width))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(height))
    # TODO have to get this working

    # Check if resolution was set successfully
    cap_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cap_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Resolution: {width} x {height}")
    if cap_width != width or cap_height != height:
        print("error resolution cant be changed to whats specified")

    # todo have default to specific resolution of cameras
    count = 0
    while True:

        ret, img = cap.read()
        cv2.imshow("img", img)
        if cv2.waitKey(20) & 0xFF == ord("c"):
            images.append(img)
            # cv2.imwrite(name, img)
            cv2.imshow("img", img)
            count += 1
            # todo make it so you can quit whenever not just after you take a capture
            if cv2.waitKey(0) & 0xFF == ord("q"):
                break
    cap.release()
    return images


def generate_calibration_data(images, checkerboard, dimension):
    # dimension = width of block in mm

    # Defining the dimensions of checkerboard
    # CHECKERBOARD = (6,9)
    # CHECKERBOARD = (5,6)

    CHECKERBOARD = checkerboard
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        int(dimension),
        0.001,
    )
    # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = []

    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0, :, :2] = np.mgrid[0 : CHECKERBOARD[0], 0 : CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None

    # Extracting path of individual image stored in a given directory
    # images = glob.glob(f'{cam_images_folder_name}/*.jpg')
    print(len(images))
    if len(images) < 9:
        print("Not enough images were found: at least 9 shall be provided!!!")
        exit(-1)

    for index, img in enumerate(images):
        print("image: ", index)
        # img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        # If desired number of corners are found in the image then ret = true
        # ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
        ret, corners = cv2.findChessboardCorners(
            gray,
            CHECKERBOARD,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
        )

        """
        If desired number of corner are detected,
        we refine the pixel coordinates and display 
        them on the images of checker board
        """
        if ret == True:
            print("Pattern found! Press ESC to skip or ENTER to accept")
            objpoints.append(objp)
            # refining pixel coordinates for given 2d points.
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)

            cv2.imshow("img", img)
            # cv2.waitKey(0)
            k = cv2.waitKey(0) & 0xFF
            if k == 27:  # -- ESC Button
                print("Image Skipped")
                imgNotGood = index
                continue

        # new_frame_name = cam_images_folder_name_calibrated + '/' + os.path.basename(fname)
        # # print(new_frame_name)
        # cv2.imwrite(new_frame_name, img)

    # cv2.destroyAllWindows()

    h, w = img.shape[:2]

    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    print("Camera matrix : \n")
    print(mtx.tolist())
    print("dist : \n")
    print(dist.tolist())
    return (mtx, dist)


def default_setup():
    cwd = os.getcwd()
    calib_folder = cwd + "/calib_img/"  # todo have way for user to change calib_folder

    checkerboard_size = (6, 5)  # todo have way for user to change checkerboard_size
    num_cameras = 0
    camera_id = []
    cameras = []
    # filename = f'cam_{cam_index}/image_{i}.jpg'
    # ! have save file structure as each camera as a sub folder to calib_img
    # get_calibration_images(0,cwd+'/calib_img/') #todo have this work regardless if on windows mac linux
    # generate_calibration_data(cwd+'/calib_img/', (5,6))
    # layout:
    # Q: what do you want to do
    #   A: setup from scratch
    #   A: add camera
    #   A: recalibrate existing camera
    # Q: setup from scratch
    # ask what name of setup (save to specific directory )
    #  ask for num_cameras (double check with amount connected) then repeat the following num_cameras times
    #  run find_camera_prod_vend()
    #  use result with get_id_from_name()
    #  then run calibration and save calibration and device id to camera-params.json
    # Q: add camera
    #  run find_camera_prod_vend()
    #  use result with get_id_from_name()
    #  then run calibration and save calibration and device id to camera-params.json
    # Q: recalibrate existing camera
    #  ask for camera id

    option = int(
        input(
            "chose option\n 1. setup from scratch \n 2. add camera to existing setup \n 3. recalibrate existing camera in existing setup\n"
        )
    )
    while option == 1:  # scratch
        output = []
        num_cameras = int(input("how many cameras are there?\n"))
        if num_cameras <= 0:
            print("invalid number of cameras")
            continue
        for i in range(0, num_cameras):
            rotation = 0
            camera_number = int(
                input("what id is labeled on the side of this camera?\n")
            )
            camera_name, camera_index = getCameraID()
           
            print("camera_index",camera_index)
            resolutions = getResolution(camera_index)
            width, height = pick_resolution(resolutions)#todo make it so it saves this info for future cameras 
            images = get_calibration_images(
                camera_index, width, height
            )  # todo have this work regardless if on windows mac linux
            mtx, dist = generate_calibration_data(images, (5, 6), 31.69)
            data = {
                "intrinsic_matrix": mtx,
                "distortion_coef": dist,
                "rotation": rotation,
                "id": camera_number,  # general id associated with camera for human use
                "name": camera_name,
                "width": width,
                "height": height,
            }
            output.append(data)
            with open("computer_code/api/camera-params.json", "w") as f:
                json.dump(output, f, indent=4)
        break

    while option == 2:  # add camera to existing setup
        None
    while option == 3:  # recalibrate existing camera in existing setup
        None


def pick_resolution(resolutions):
    output = ""
    for index, line in enumerate(resolutions):
        output += str(index) + ": " + str(line) + "\n"
    choice = input("select a resolution from this list\n " + output)
    width, height = resolutions[int(choice)]
    return width, height


def getCameraID():
    while True:

        output = find_camera()
        if len(output) > 1:
            print("error to many devices were disconnected try again")

        elif len(output) <= 0:
            print("no devices were disconnected try again")
        else:

            break
    return output[0]


def getResolution(camera_id):
    # TODO have to use v4l2 to get list of supported resolution that user can select from and return that resolution as 2 vars width height
    # command to use
    command = "v4l2-ctl -d /dev/video" + str(camera_id) + " --list-formats-ext"
    result = (
        subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .split("\n")
    )
    if result[-1] == "":
        result.pop()
    resolutions = []
    for line in result:
        if "Size: Discrete" in line:
            parts = line.strip().split()
            if len(parts) >= 3:
                size = parts[2]
                if "x" in size:
                    w, h = size.split("x")
                    resolutions.append((int(w), int(h)))

    return resolutions

if __name__ == "__main__":
    # camera_number = 0
    # rotation = 0
    # output=""
    # camera_name, camera_index = [
    #     "Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)",
    #     4,
    # ]
    # camera_index = get_id_from_name(camera_name)
    # print("camera_index",camera_index)
    # resolutions = getResolution(camera_index)
    # width, height = pick_resolution(resolutions)

    
    # images = get_calibration_images(
    #     camera_index, width, height
    # )  # todo have this work regardless if on windows mac linux
    # mtx, dist = generate_calibration_data(images, (5, 6), 31.69)
    # data = {
    #     "intrinsic_matrix": mtx,
    #     "distortion_coef": dist,
    #     "rotation": rotation,
    #     "id": camera_number,  # general id associated with camera for human use
    #     "name": camera_name,
    #     "width": width,
    #     "height": height,
    # }
    # output.append(data)
    # with open("computer_code/api/camera-params.json", "w") as f:
    #     json.dump(output, f, indent=4)
    default_setup()
