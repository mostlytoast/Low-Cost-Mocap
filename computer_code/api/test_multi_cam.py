import cv2
import threading
from subprocess import PIPE, run

def find_camera_id(camera_name):
    """_summary_ use with macos to ensure proper camera selection 

    Args:
        camera_name (_string_): camera name as listed by lsusb 
    """
    # camera_name = "Arducam OV9281 USB Camera"
    command = ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", '""']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    cam_id = []
    # print(result)
    for item in result.stderr.splitlines():
        if camera_name in item:
            cam_id.append(int(item.split("[")[2].split("]")[0]))
    # print("cam id", cam_id)
    return cam_id

class camThread(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
    def run(self):
        print( "Starting " + self.previewName)
        camPreview(self.previewName, self.camID)

def camPreview(previewName, camID):
    cv2.namedWindow(previewName)
    cam = cv2.VideoCapture(camID)
    if cam.isOpened():  # try to get the first frame
        rval, frame = cam.read()
    else:
        rval = False

    while rval:
        cv2.imshow(previewName, frame)
        rval, frame = cam.read()
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break
    cv2.destroyWindow(previewName)

# Create two threads as follows
ids= find_camera_id("Arducam OV9281 USB Camera")
thread1 = camThread("Camera 1",ids[0])
thread2 = camThread("Camera 2", ids[1])
thread1.start()
thread2.start()