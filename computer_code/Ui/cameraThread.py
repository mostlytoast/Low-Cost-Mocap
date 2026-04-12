import os
from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2

from threading import Lock
from computer_code.api.Singleton import Singleton
import numpy as np

"""_summary_ separate thread to get video from webcam 

Returns:
    _type_: _description_ signal image 
"""
from computer_code.api.helpers import find_chessboard, Cameras
import time
@Singleton
class MyThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self):
        super().__init__()
        
        self.camera_id = 0
        self.cap = None
        self._running = False
        self._lock = self.mutex()
        self._pending_camera_id = None
        self.detect_board = True
        self.sensitivity = 0.005
        self.auto_time = 5
        self.imgpoints = []
        self.objpoints = []
        self.img = None
        self.prev_time = None
        self.auto_capture_state = False
        self.take_capture_state = False
        self.count = 0 
        self.set_checkerboard()
    def clearData(self):
        self.imgpoints = []
        self.objpoints = []
        self.count = 0 

    def set_checkerboard(self, checkerboard = (9, 6), dimension = 21.86):
        self.checkerboard = checkerboard
        self.dimension = dimension
        self.objp = np.zeros((1, self.checkerboard[0] * self.checkerboard[1], 3), np.float32)
        self.objp[0, :, :2] = np.mgrid[0 : self.checkerboard[0], 0 : self.checkerboard[1]].T.reshape(-1, 2)

    def set_camera_id(self, camera_id):
        with self._lock:
            self._pending_camera_id = camera_id
  
    def calc_calib(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints, self.imgpoints, gray.shape[::-1], None, None
        )
        cameras = Cameras.instance() 
        cameras.camera_params[self.camera_id]["intrinsic_matrix"] = mtx.tolist()
        cameras.camera_params[self.camera_id]["distortion_coef"] = dist.tolist()

    def _capture(self,corners,img):
        if self.prev_time == None:
            self.prev_time = time.time()
        time_passed = time.time() - self.prev_time
        # take picture if a board is in view and either capture button clicked or auto auto capture says so 
        if ((time_passed >= self.auto_time and self.auto_capture_state) or self.take_capture_state):
            # folder = f'cam_{self.camera_id}'
            # os.makedirs(folder, exist_ok=True)
            # filename = f'cam_{self.camera_id}/image_{self.count}.jpg'
            # cv2.imwrite(str(filename),img)
            # if(corners != []):
            self.imgpoints.append(corners)
            print("imgpoints", len(self.imgpoints))
            self.take_capture_state = False
            self.prev_time = time.time()
            self.objpoints.append(self.objp)
            self.count +=1
    
    def run(self):
        self._running = True
        cameras = Cameras.instance()
        self.cap = cameras.cameras[self.camera_id]
        while self._running:
            with self._lock:
   
                if self._pending_camera_id is not None:
                    self.camera_id = self._pending_camera_id
                    self.cap = cameras.cameras[self.camera_id]
                    self._pending_camera_id = None

                if self.cap is not None and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret:
                        frame = self.chessboard(frame)
                        frame = np.rot90(frame, k=cameras.camera_params[self.camera_id].get("rotation",0))
                        frame = self.cvimage_to_label(frame)
                        self.frame_signal.emit(frame)

            self.msleep(10)  # avoid busy loop
    def set_find_chessboard(self, state):
        self.detect_board = state

    def chessboard(self,frame):
        if  self.detect_board:
            find, frame, corners = find_chessboard(frame,self.checkerboard,self.dimension, self.sensitivity)
            if find:
                self.img = frame
                self._capture(corners,frame)
        return frame
    def stop(self):
        cameras = Cameras.instance()
        cap = cameras.cameras[self.camera_id]
        self._running = False
        if cap is not None and cap.isOpened():
            cap.release()
        return True
        
    def mutex(self):

        # Simple cross-thread lock for PyQt5 QThread
        return Lock()

    def cvimage_to_label(self, image):
        # image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image