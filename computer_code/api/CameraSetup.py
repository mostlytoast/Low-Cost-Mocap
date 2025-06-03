from helpers import find_camera_id
import cv2
import numpy as np
import os
import glob
import subprocess
import os
import cv2  # OpenCV for image handling
import time
import json
import shutil
calib_img_dir = os.path.join(os.getcwd(), 'calib_img')

#todo document 


# todo enable ability to get id from device id 
res_width = 320
res_height = 240
def lsusb():

    result = subprocess.run("lsusb", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
    if result[-1] == '':
        result.pop()
    return result

def listWebcams(): 
    result = subprocess.run("v4l2-ctl --list-devices", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
    if result[-1] == '':
        result.pop()
    return result
def find_camera():
    """_summary_

    Returns:
        _type_: _description_
    """
    # print()
    input("remove camera and press enter to continue") 
    result_no_cam = listWebcams()
  
    input("connect the camera and press enter to continue") 
    result_with_cam = listWebcams()
    # todo make easier to use by having it wait for connect and disconnect instead of waiting for prompt
    # result_with_cam = listWebcams()
    # result_no_cam = []
    # input("remove camera") 
    # while(True):
    #     result_no_cam = listWebcams()
    #     if result_no_cam != result_with_cam:
    #         break
    #     time.sleep(0.5)
    # input("reconnect camera camera")                   
    # while(True):
    #     third_result = listWebcams()
    #     if result_no_cam != third_result:
    #         break
    #     time.sleep(0.5)

    diff = []
    # print("result_no_cam", result_no_cam)

    # print("result_with_cam", result_with_cam)
    s = set(result_no_cam)
    diff = [x for x in result_with_cam if x not in s]
    # for element in result_no_cam: #https://www.geeksforgeeks.org/python-difference-two-lists/
    #     if element not in result_with_cam:
    #         diff.append(element)
    output = []#list of cameras and their name and id (id will change after this program so done use it for long )
    
    for i,line in enumerate(diff):
        if "\t" not in line:
            #camera name found 
            #todo get error checking working 
            # Extract the last number from the next line (device id)
            device_line = diff[i+1]
            # Extract the device id from a line like '\t/dev/video4'
            device_id_str = device_line.strip().split('/')[-1].replace('video', '')
            device_id = int(device_id_str)
            output.append([line, device_id])
            #should this include the id of the camera? this could change immediately after running this code 
    
  

    return output

def find_device_id(name):
    """_summary_ find the device id for a given usb product and vendor id which can be found with v4l2-ctl --list-devices or listWebcams() used to determine the opencv id for cv.VideoCapture(id)
    Args:
        name (_str_): the name of camera with id info given by v4l2-ctl --list-devices or listWebcams()
    Example: 
        find_device_id("Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)")
    """
     #
    # 
    lines = find_camera()
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
        if name in line:
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


def get_calibration_images(camera_id,width, height):

    """_summary_ takes and saves images to path
    """
    images = []
    # todo check if theres already images in file if so error out or clear them?

    cap = cv2.VideoCapture(camera_id) 
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    # TODO have to get this working 

    # Check if resolution was set successfully
    cap_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cap_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Resolution: {width} x {height}")
    if(cap_width != width or cap_height != height):
        print("error resolution cant be changed to whats specified")
        
    # todo have default to specific resolution of cameras 
    count = 0
    while True:
        
        ret, img = cap.read()
        cv2.imshow("img", img)
        if cv2.waitKey(20) & 0xFF == ord('c'):
            images.append(img)
            # cv2.imwrite(name, img)
            cv2.imshow("img", img)
            count += 1
            # todo make it so you can quit whenever not just after you take a capture 
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
    cap.release()
    return images

def generate_calibration_data(images,checkerboard,dimension):
    # dimension = width of block in mm


    # Defining the dimensions of checkerboard
    # CHECKERBOARD = (6,9)
    # CHECKERBOARD = (5,6)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, dimension, 0.001)
    CHECKERBOARD = checkerboard
    # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = [] 
    
    
    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None
    
    # Extracting path of individual image stored in a given directory
    # images = glob.glob(f'{cam_images_folder_name}/*.jpg')
    print(len(images))
    if len(images) < 9:
        print("Not enough images were found: at least 9 shall be provided!!!")
        exit(-1)
    
    for index, img in enumerate(images):
        print("image: " , index)
        # img = cv2.imread(fname)
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
                imgNotGood = index
                continue

        
        # new_frame_name = cam_images_folder_name_calibrated + '/' + os.path.basename(fname)
        # # print(new_frame_name)
        # cv2.imwrite(new_frame_name, img)

    
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

# def create_dir():
#     """_summary_ creates /calib_img/ directory if it does not exist already 
#     """
    
#     if not os.path.exists(calib_img_dir):
#         os.makedirs(calib_img_dir)
# # def remove_dir():
# #     """Removes the /calib_img/ directory after listing its contents and confirming with the user."""
# #     if os.path.exists(calib_img_dir):
# #         files = os.listdir(calib_img_dir)
# #         print("Contents of calib_img_dir:")
# #         for f in files:
# #             print(f"  {f}")
# #         confirm = input("Are you sure you want to delete the calib_img_dir and all its contents? (y/n): ")
# #         if confirm.lower() == 'y':
# #             shutil.rmtree(calib_img_dir)
# #             print("calib_img_dir removed.")
# #         else:
# #             print("Operation cancelled.")
# #     else:
# #         print("calib_img_dir does not exist.")
# def detect_dir():
#     return os.path.exists(calib_img_dir)


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
        output = []
        num_cameras = int(input("how many cameras are there?\n"))
        if num_cameras <= 0:
            print("invalid number of cameras")
            continue
        for i in range(0, num_cameras):
            rotation = 0 
            camera_number = int(input("what id is labeled on the side of this camera?\n"))
            camera_name, camera_index  = getCameraID()
            width, height = getResolution(camera_name)
            images =  get_calibration_images(camera_index,width, height) #todo have this work regardless if on windows mac linux 
            mtx, dist = generate_calibration_data(images, (5,6),31.69)
            # print(find_device_id(find_camera_prod_vend()))
            # default_setup() 
            data = {
                "intrinsic_matrix": mtx,
                "distortion_coef": dist,
                "rotation": rotation,
                "id": camera_number, #general id associated with camera for human use 
                "name": camera_name,
                "width": width,
                "height":height 
            }
            output.append(data)
            with open("computer_code/api/camera-params.json", "w") as f:
                json.dump(output, f, indent=4)
        break

            
    while option == 2: #add camera to existing setup
        None
    while option == 3: #recalibrate existing camera in existing setup
        None
   


def getCameraID():
    while (True):

        output = find_camera()
        if len(output) > 1:
            print("error to many devices were disconnected try again")
            
        elif len(output) <= 0:
            print("no devices were disconnected try again")
        else:
            
            break
    return output[0]
def getResolution(camera_name):
    # TODO have to use v4l2 to get list of supported resolution that user can select from and return that resolution as 2 vars width height 
    # command to use v4l2-ctl -d /dev/video4 --list-formats-ext
    return 1280, 800
if __name__ == '__main__':
    # camera_name, camera_index = ["Arducam OV9281 USB Camera: Ardu (usb-0000:02:00.0-1.1.1):"
    #     ,4]
    # camera_number = 0
    # rotation = 0 
    default_setup()

  