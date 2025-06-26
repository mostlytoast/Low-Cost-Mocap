import threading
from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2
import imutils
from threading import Lock

import numpy as np

"""_summary_ separate thread to get video from webcam 

Returns:
    _type_: _description_ signal image 
"""
from helpers import find_chessboard
import time
class MyThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.cap = None
        self._running = False
        self._lock = self.mutex()
        self._pending_camera_id = None
        self.detect_board = True
        self.width =800
        self.height = 600
        self.exposure = 100
        self.max_exposure = 0 
        self.min_exposure = 100
        self.gain = 0
        self.auto_exposure = 1 #
        self.rotation = 0
        self.sensitivity = 0.005
        self.auto_time = 5
        self.buffer = []
        self.prev_time = None
        self.auto_capture_state = False
        self.take_capture_state = False
    def set_rotation(self, rot):
        self.rotation = rot
    def set_camera_id(self, camera_id):
        with self._lock:
            self._pending_camera_id = camera_id
    def set_camera_settings(self, settings):
        """set the camera settings received from videosubsystem.getSettings()

        Args:
            settings (_type_): _description_
        """
        
        self.max_exposure = settings["max_exposure"]
        self.min_exposure = settings["min_exposure"]
        self.auto_exposure = settings["manual_mode"] 

    def capture(self,frame):
        if self.prev_time == None:
            self.prev_time = time.time()
        time_passed = time.time() - self.prev_time
        if (time_passed >= self.auto_time and self.auto_capture_state) or self.take_capture_state:
            self.buffer.append(frame)
            print("buffer", len(self.buffer))
            self.take_capture_state = False
            self.prev_time = time.time()
   
    def set_exposure(self, exposure):
        if self.cap is not None and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.auto_exposure)
            self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
        else:
            self.exposure = exposure
    def set_gain(self, gain):
        if self.cap is not None and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.auto_exposure)
            self.cap.set(cv2.CAP_PROP_GAIN, gain)  # gain = [gain] * self.num_cameras
        else:
            self.gain = gain

    def set_resolution(self, height, width):
        if self.cap is not None and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(width))
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(height))
        else:
            self.width = width
            self.height = height

    
    def run(self):
        self._running = True
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
                        image = frame
                        if  self.detect_board:
                            find, image = find_chessboard(frame,(9, 6),21.86, self.sensitivity)
                            #     if find:
                            #         image = self.cvimage_to_label(image)
                            #         self.frame_signal.emit(image)
                            # else:
                        self.capture(frame)
                        image = np.rot90(image, k=self.rotation)
                        
                        image = self.cvimage_to_label(image)
                        self.frame_signal.emit(image)

            self.msleep(10)  # avoid busy loop
    def set_find_chessboard(self, state):
        self.detect_board = state
    
        
    def stop(self):
        # # Send an empty frame (black image) through the signal
        # empty_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # empty_qimage = self.cvimage_to_label(empty_image)
        # self.frame_signal.emit(empty_qimage)

        self._running = False
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        
    def mutex(self):
        # Simple cross-thread lock for PyQt5 QThread
        return Lock()

    def cvimage_to_label(self, image):
        # image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image