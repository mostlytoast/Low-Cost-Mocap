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

    def set_camera_id(self, camera_id):
        with self._lock:
            self._pending_camera_id = camera_id

    def set_resolution(self, height, width):
        RuntimeWarning("not implemented")

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        while self._running:
            with self._lock:
                if self._pending_camera_id is not None:
                    if self.cap is not None and self.cap.isOpened():
                        self.cap.release()
                    self.camera_id = self._pending_camera_id
                    self.cap = cv2.VideoCapture(self.camera_id)
                    self._pending_camera_id = None

            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    frame = self.cvimage_to_label(frame)
                    self.frame_signal.emit(frame)
            self.msleep(10)  # avoid busy loop

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