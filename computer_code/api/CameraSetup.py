
import cv2
import numpy as np
import os
import glob
import subprocess
import os
import cv2  # OpenCV for image handling
import time
import json
#todo document 

# todo enable ability to get id from device id 
def lsusb():

    result = subprocess.run("lsusb", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
    if result[-1] == '':
        result.pop()
    return result

def find_camera_prod_vend():
    """_summary_

    Returns:
        _type_: _description_
    """
    # print()
    input("remove camera and press enter to continue") 
    result_no_cam = lsusb()
    # todo make easier to use by having it wait for connect and disconnect instead of waiting for prompt
    input("connect the camera and press enter to continue") 
    result_with_cam = lsusb()
    lsusb_diff = []
    # print("result_no_cam", result_no_cam)

    # print("result_with_cam", result_with_cam)
    s = set(result_no_cam)
    lsusb_diff = [x for x in result_with_cam if x not in s]
    # for element in result_no_cam: #https://www.geeksforgeeks.org/python-difference-two-lists/
    #     if element not in result_with_cam:
    #         lsusb_diff.append(element)

    
    if len(lsusb_diff) > 1:
        print("error to many devices were disconnected try again")
        exit(-1)
    if len(lsusb_diff) <= 0:
        print("no devices were disconnected try again")
        exit(-1)
    # print(lsusb_diff[0].split(' ')[5])
    return lsusb_diff[0].split(' ')[5]

def find_device_id(prod_vend_id):
    """_summary_ find the device id for a given usb product and vendor id which can be found with lsusb or find_camera_prod_vend() used to determine the opencv id for cv.VideoCapture(id)
    Args:
        prod_vend_id (_str_): the product and vendor id separated by a ':'
    Example: 
        find_device_id("0c45:6366")
    """
     #
    # 
    lines = lsusb()
    # print(result)
    # output = result.stdout.decode('utf-8').strip()
    # lines = output.split('\n')
    # # if lines[-1] == '' :
    #     lines.pop()
    cameras = []
    for line in lines:
        # print(line)
        # print(line.split(' ')[3].strip(":"))
        Device_id = int(line.split(' ')[3].strip(":"))
        if prod_vend_id in line:
            cameras.append(Device_id)
        # if 'Webcam' in line:
        # vendor_id = line.split(' ')[5].split(':')[0]
        # product_id = line.split(' ')[5].split(':')[1]
        # # print(vendor_id, ", ", product_id)
        # if vendor_id == '0c45' and product_id == '6366':
        #     webcam = line.split(':')[-1].strip()
        #     cameras.append(webcam)
    return cameras


# code based on https://github.com/jyjblrd/Low-Cost-Mocap/discussions/11#discussioncomment-9380283


def get_calibration_images(camera_id, path):
    """_summary_ takes and saves images to path
    """
    # todo check if theres already images in file if so error out or clear them?

    cap = cv2.VideoCapture(camera_id) 
    # todo have default to specific resolution of cameras 
    count = 0
    while True:
        name = path + str(count)+".jpg" 
        ret, img = cap.read()
        cv2.imshow("img", img)
        if cv2.waitKey(20) & 0xFF == ord('c'):
            cv2.imwrite(name, img)
            cv2.imshow("img", img)
            count += 1
            # todo make it so you can quit whenever not just after you take a capture 
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
    cap.release()


def generate_calibration_data(cam_images_folder_name,checkerboard,dimension):
    # dimension = width of block in mm

    
    # cam_images_folder_name = 'cam_1'
    cam_images_folder_name_calibrated = f'{cam_images_folder_name}_c'

    # Defining the dimensions of checkerboard
    # CHECKERBOARD = (6,9)
    # CHECKERBOARD = (5,6)

    # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, dimension, 0.001)
    CHECKERBOARD = checkerboard
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = [] 
    
    
    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None
    
    # Extracting path of individual image stored in a given directory
    images = glob.glob(f'{cam_images_folder_name}/*.jpg')
    print(len(images))
    if len(images) < 9:
        print("Not enough images were found: at least 9 shall be provided!!!")
        exit(-1)

    for fname in images:
        print(fname)
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        # If desired number of corners are found in the image then ret = true
        # ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE)
        
        """
        If desired number of corner are detected,
        we refine the pixel coordinates and display 
        them on the images of checker board
        """
        if ret == True:
            print("Pattern found! Press ESC to skip or ENTER to accept")
            objpoints.append(objp)
            # refining pixel coordinates for given 2d points.
            corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
            
            
            imgpoints.append(corners2)
    
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        
            cv2.imshow('img',img)
            # cv2.waitKey(0)
            k = cv2.waitKey(0) & 0xFF
            if k == 27: #-- ESC Button
                print("Image Skipped")
                imgNotGood = fname
                continue

        
        new_frame_name = cam_images_folder_name_calibrated + '/' + os.path.basename(fname)
        # print(new_frame_name)
        cv2.imwrite(new_frame_name, img)

    
    # cv2.destroyAllWindows()
    
    h,w = img.shape[:2]
    
    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    print("Camera matrix : \n")
    print(mtx)
    print("dist : \n")
    print(dist)
   
    return(mtx, dist)



def default_setup(): 
    cwd = os.getcwd()
    calib_folder = cwd+'/calib_img/' #todo have way for user to change calib_folder 
    checkerboard_size = (6,5) #todo have way for user to change checkerboard_size 
    num_cameras = 0
    camera_id= []
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
            #  use result with find_device_id()
            #  then run calibration and save calibration and device id to camera-params.json
    # Q: add camera 
        #  run find_camera_prod_vend()
        #  use result with find_device_id()
        #  then run calibration and save calibration and device id to camera-params.json
    # Q: recalibrate existing camera 
        #  ask for camera id 

    option = int(input("chose option\n 1. setup from scratch \n 2. add camera to existing setup \n 3. recalibrate existing camera in existing setup\n"))
    while option == 1: #scratch
        num_cameras = int(input("how many cameras are there?\n"))
        if num_cameras <= 0:
            print("invalid number of cameras")
            continue
        for i in range(0, num_cameras):
            find_device_id(find_camera_prod_vend()) #?should i find prod_vend of all cameras first then do calib for each or just do entire setup for each?

        break

            
    while option == 2: #add camera to existing setup
        None
    while option == 3: #recalibrate existing camera in existing setup
        None
   
    # cameras = find_device_id(find_camera_prod_vend())
    # print(f"USB cameras: {cameras}")
    # 0c45:6366 

if __name__ == '__main__':
    cwd = os.getcwd()
    # print(find_device_id("0c45:6366"))
    # get_calibration_images(0,cwd+'/calib_img/') #todo have this work regardless if on windows mac linux 
    generate_calibration_data(cwd+'/calib_img/', (5,6),31.69)
    # print(find_device_id(find_camera_prod_vend()))
    # default_setup() 
# ffmpeg -f  avfoundation -list_devices true -i
# 
# [[903.15174004   0.         660.17663279]
#  [  0.         894.18054275 403.93314412]
#  [  0.           0.           1.        ]]
# dist : 

# [[ 0.01396426 -0.00322745  0.00653061  0.01614453 -0.04478135]]