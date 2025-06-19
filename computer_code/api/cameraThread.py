from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2
import imutils

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

    def set_camera_id(self, camera_id):
        if self.cap != None:
            if self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_id)
        self.camera_id = camera_id
    def set_resolution(self, height, width):
        RuntimeWarning("not implemented")
    
    def run(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        while self.cap.isOpened():
            _, frame = self.cap.read()
            frame = self.cvimage_to_label(frame)
            self.frame_signal.emit(frame)

    def cvimage_to_label(self, image):
        image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image