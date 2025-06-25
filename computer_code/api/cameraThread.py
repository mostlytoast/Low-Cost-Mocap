import threading
from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2
import imutils
from threading import Lock

"""_summary_ separate thread to get video from webcam 

Returns:
    _type_: _description_ signal image 
"""

class MyThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.cap = None
        self._running = True
        self._lock = self.mutex()
        self._pending_camera_id = None
        self.detect_board = True
        self.width =800
        self.height = 600
        self.exposure = 100
        self.gain = 0
        self.auto_exposure = 1 #

    def set_camera_id(self, camera_id):
        with self._lock:
            self._pending_camera_id = camera_id

    def set_exposure_gain(self, exposure, gain):
        if self.cap is not None and self.cap.isOpened():

            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.auto_exposure)
            print(exposure)
            success = self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure)

            print("Exposure set:", success, "Current exposure:", self.cap.get(cv2.CAP_PROP_EXPOSURE))
            self.cap.set(cv2.CAP_PROP_GAIN, gain)  # gain = [gain] * self.num_cameras
        else:
            self.exposure = exposure
            self.gain = gain
    def set_resolution(self, height, width):
        
        if self.cap is not None and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(width))
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(height))
        else:
            self.width = width
            self.height = height

    
    def run(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
        self.set_resolution(self.width,self.height)
        while self._running:
            with self._lock:
                if self._pending_camera_id is not None:
                    if self.cap is not None and self.cap.isOpened():
                        self.cap.release()
                    self.camera_id = self._pending_camera_id
                    self.cap = cv2.VideoCapture(self.camera_id)
                    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
                    self._pending_camera_id = None

                if self.cap is not None and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret:
                        # if  self.detect_board:
                        find, image = self.find_chessboard(frame,(9, 6),21.86)
                        #     if find:
                        #         image = self.cvimage_to_label(image)
                        #         self.frame_signal.emit(image)
                        # else:
                        frame = self.cvimage_to_label(image)
                        self.frame_signal.emit(frame)

            self.msleep(10)  # avoid busy loop
    def find_chessboard(self,img,checkerboard, checkerboard_dimension):
        display_img = img.copy()
        # Try to find the checkerboard corners and draw them
        gray = cv2.cvtColor(display_img, cv2.COLOR_BGR2GRAY)
        found = [False]
        corners = [None]
        def detect_chessboard():
                ret, detected_corners = cv2.findChessboardCorners(
                gray,
                checkerboard,
                cv2.CALIB_CB_FAST_CHECK
                )
                if ret:
                    found[0] = True
                    corners[0] = cv2.cornerSubPix(
                        gray, detected_corners, (11, 11), (-1, -1),
                        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, int(checkerboard_dimension), 0.001)
                    )

        # Set timeout in seconds
        timeout = 0.008
        # todo maybe dynamic for timeout DO WITH SENSITIVITY SLIDER 
        thread = threading.Thread(target=detect_chessboard)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            # Timeout reached, stop thread (can't kill thread, just ignore result)
            pass
        if found[0]:
            cv2.drawChessboardCorners(display_img, checkerboard, corners[0], True)
            return True, display_img
        return False, img
        
    def stop(self):
        self._running = False
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

    def mutex(self):
        # Simple cross-thread lock for PyQt5 QThread
        return Lock()

    def cvimage_to_label(self, image):
        image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image