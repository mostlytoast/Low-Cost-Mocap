
from  computer_code.api.videoSubSystem import *
import cv2
import numpy as np
import json
checkerboard = (9,6)
checkerboard_dimension= 21.86
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
        name = "computer_code/api/calibImg" + str(count) + ".jpg" 
        ret, img = cap.read()
        cv2.imshow("img", img)
        if cv2.waitKey(20) & 0xFF == ord("c"):
            images.append(img)
            cv2.imwrite(name, img)
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

    cv2.destroyAllWindows()

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
    checkerboard_size = (6, 5)  # todo have way for user to change checkerboard_size
    num_cameras = 0
    # ! have save file structure as each camera as a sub folder to calib_img
    # get_calibration_images(0,cwd+'/calib_img/') #todo have this work regardless if on windows mac linux
    # generate_calibration_data(cwd+'/calib_img/', (5,6))
    # layout:
    # Q: what do you want to do
    #   A: setup from scratch
    #   A: add camera
    #   A: recalibrate existing camera
    #   A: generate grid
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
    # Q: ask for settings of dimensions and then export as pdf

    option = get_int_input(
        "chose option\n 1. setup from scratch \n 2. add camera to existing setup \n 3. recalibrate existing camera in existing setup\n",
        validator=lambda x: x in [1, 2, 3],
         errorMessage="Invalid option. Please enter 1, 2, or 3."
            )
            
    
    while option == 1:  # from scratch
        output = []
        num_cameras = get_int_input("how many cameras are there?\n",validator=lambda x: x >0, errorMessage ="number of cameras can't be zero" )
        if num_cameras <= 0:
            print("invalid number of cameras")
            continue
        for i in range(0, num_cameras):
            rotation = 0
            camera_name, camera_index = getCameraID()
            camera_number = get_int_input("what id is labeled on the side of this camera?\n",validator=lambda x: x >0, errorMessage ="id on camera can't be zero" )

            print("camera_index", camera_index)
            resolutions = getResolution(camera_index)
            width, height = pick_resolution(
                resolutions
            )  # todo make it so it saves this info for future cameras
            data = get_calibration_data(
                rotation, camera_number, camera_name, camera_index, width, height
            )
            output.append(data)
            with open("computer_code/api/"
            ".json", "w") as f:
                json.dump(output, f, indent=4)
        break

    while option == 2:  # add camera to existing setup
        None
    while option == 3:  # recalibrate existing camera in existing setup
        None
"""_summary_ keeps trying to get int from user by displaying test message if error happens prevents crash and displays error to user
"""
def get_int_input(text, validator=None, errorMessage="error: please provide an integer"):
    while True:
        try:
            output = int(input(text))
            if validator is not None and not validator(output):
                print(errorMessage)
                continue
            break
        except KeyboardInterrupt:
            try:
                input("\nare you sure you want to quit? hit control c again ")
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt detected. Exiting input loop.")
                exit(-1)
        except Exception as e:
            print(f"{errorMessage}\nError details: {e}")
    return output

def get_calibration_data(
    rotation, camera_number, camera_name, camera_index, width, height
):
    images = get_calibration_images(
        camera_index, width, height
    )  # todo have this work regardless if on windows mac linux
    
    mtx, dist = generate_calibration_data(images, checkerboard, checkerboard_dimension)
    return {
        "intrinsic_matrix": mtx.tolist(),
        "distortion_coef": dist.tolist(),
        "rotation": rotation,
        "id": camera_number,  # general id associated with camera for human use
        "name": camera_name,
        "width": width,
        "height": height,
    }
   

def pick_resolution(resolutions):
    output = ""
    for index, line in enumerate(resolutions):
        output += str(index) + ": " + str(line) + "\n"
    choice = get_int_input("select a resolution from this list\n " + output, validator=lambda x: x >=0 and x < len(resolutions), errorMessage ="please select valid option in the list" )
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


if __name__ == "__main__":
    cam_id = get_id_from_name("Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-1.4):")
    res = getResolution(cam_id)[0]
    get_calibration_images(cam_id, res[0],res[1])
# class detectCameraGUI(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()

#         # self.setWindowTitle("HELLO!")

#         # QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

#         # self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
#         # self.buttonBox.accepted.connect(self.accept)
#         # self.buttonBox.rejected.connect(self.reject)

#         # layout = QtWidgets.QVBoxLayout()
#         # message = QtWidgets.QLabel("Something happened, is that OK?")
#         # layout.addWidget(message)
#         # layout.addWidget(self.buttonBox)
#         # self.setLayout(layout)
#         self.setup_button = QtWidgets.QPushButton(" from scratch")
#         # self.setup_button.clicked.connect(self.setup)
#         self.layout1.addWidget(self.setup_button)

#         # self.setup_button = QtWidgets.QPushButton("Setup from scratch")
#         # self.setup_button.clicked.connect(self.handle_option)
#         # self.layout1.addWidget(self.setup_button)
        
#         # self.setup_button = QtWidgets.QPushButton("Setup from scratch")
#         # self.setup_button.clicked.connect(self.handle_option)
#         # self.layout1.addWidget(self.setup_button)
#         # self.output_text = QtWidgets.QTextEdit()
#         # self.output_text.setReadOnly(True)
#         # self.layout1.addWidget(self.output_text)

#         self.setLayout(self.layout1)
# class CameraSetupGUI(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Camera Setup")
#         self.layout1 = QtWidgets.QHBoxLayout()
        
#         # self.option_label = QtWidgets.QLabel("Choose option:")
#         # self.layout1.addWidget(self.option_label)

#         # self.option_combo = QtWidgets.QComboBox()
#         # self.option_combo.addItems([
#         #     "1. Setup from scratch",
#         #     "2. Add camera to existing setup",
#         #     "3. Recalibrate existing camera"
#         # ])
#         # self.layout1.addWidget(self.option_combo)

#         self.setup_button = QtWidgets.QPushButton("Setup from scratch")
#         self.setup_button.clicked.connect(self.setup)
#         self.layout1.addWidget(self.setup_button)

#         # self.setup_button = QtWidgets.QPushButton("Setup from scratch")
#         # self.setup_button.clicked.connect(self.handle_option)
#         # self.layout1.addWidget(self.setup_button)
        
#         # self.setup_button = QtWidgets.QPushButton("Setup from scratch")
#         # self.setup_button.clicked.connect(self.handle_option)
#         # self.layout1.addWidget(self.setup_button)
#         # self.output_text = QtWidgets.QTextEdit()
#         # self.output_text.setReadOnly(True)
#         # self.layout1.addWidget(self.output_text)

#         self.setLayout(self.layout1)

#     def setup(self):
#         # # Remove the old layout and replace it with a new one
#         # QtWidgets.QWidget().setLayout(self.layout())  # Detach old layout
#         # self.layout1 = QtWidgets.QHBoxLayout()        # Create a new layout
#         # self.setLayout(self.layout1)                  # Set the new layout
#         # self.setWindowTitle("scratch")
#         # self.alert =  QtWidgets.QDialog()
#         # self.layout1.addWidget(self.setup_button)
#         dlg = QtWidgets.QDialog(self)
#         dlg.setWindowTitle("HELLO!")
#         dlg.exec()
#     # add camera to existing 
#     # recalibrate camera 
#     # reconfigure connections (usb id's)

       

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     window = CameraSetupGUI()
#     window.show()
#     sys.exit(app.exec_())
