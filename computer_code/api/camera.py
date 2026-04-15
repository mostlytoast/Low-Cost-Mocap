import numpy as np

import computer_code.api.videoSubSystem as videoSubSystem 
import cv2 as cv

import logging
logger = logging.getLogger(__name__)
class Camera:
    # @profile
    def __init__(self, camera_system_name):
        # system vars (immutable)
        self.camera_system_name = camera_system_name
        camera_system_id = videoSubSystem.get_id_from_name(camera_system_name)
        self.resolution_list = videoSubSystem.getResolution(camera_system_id)
        settings = videoSubSystem.getSettings(camera_system_id)
        self.manual_mode = settings["manual_mode"],
        self.auto_exposure_mode = settings["auto_exposure_mode"],
        self.min_exposure = settings["min_exposure"],
        self.max_exposure = settings["max_exposure"]
        
        
        # variable settings 
        self.current_width = self.resolution_list[0][0]
        self.current_height = self.resolution_list[0][1]
        self.current_rotation = None
        self.current_gain = None
        self.current_exposure = None

        # calibration
        self.intrinsic_matrix = None
        self.distortion_coef = None

        #opencv 
        self.cap = None

    def setIntrinsicMatrix(self, intrinsic_matrix):
        self.intrinsic_matrix = np.array(intrinsic_matrix)
    def getIntrinsicMatrix(self):
        return self.intrinsic_matrix
    
    def setDistortionCoef(self, distortion_coef):
        self.distortion_coef = np.array(distortion_coef)
    def getDistortionCoef(self):
        return self.distortion_coef
    
    def setRotation(self, rotation):
        self.current_rotation = rotation
        logger.debug("set rotation for camera", self.camera_system_name, rotation)
        return True
    def getRotation(self):
        return self.current_rotation
    
    def setExposure(self, exposure):
        self.current_exposure = exposure
        logger.debug("set exposure for camera", self.camera_system_name, exposure)
        if self.cap:
            self.cap.set(cv.CAP_PROP_AUTO_EXPOSURE, self.manual_mode)
            self.cap.set(cv.CAP_PROP_EXPOSURE, exposure)
            logger.debug("successfully set exposure for camera", self.camera_system_name)
            return True
    def getExposure(self):
        return self.current_exposure

    def setGain(self, gain):
        self.current_gain = gain
        logger.debug("set gain for camera", self.camera_system_name, gain)
        if self.cap:
            self.cap.set(cv.CAP_PROP_AUTO_EXPOSURE, self.manual_mode)
            self.cap.set(cv.CAP_PROP_GAIN, gain)
            return True
        
    def getGain(self):
        return self.current_gain

    def setResolution(self, resolution_index):
        if self.resolution_list is None: 
            return False
        
        self.current_width = self.resolution_list[resolution_index][0]
        self.current_height = self.resolution_list[resolution_index][1]

        if self.cap:
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, float(self.current_width))
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, float(self.current_height))

    def getWidth(self):
        return self.current_width
    
    def getHeight(self):
        return self.current_height
    
    def open_camera(self):
        camera_system_id = videoSubSystem.get_id_from_name(self.camera_system_name)
        # Use the CAP_V4L2 backend for better performance on Linux if available
        self.cap = cv.VideoCapture(camera_system_id, cv.CAP_V4L2)

        # Try to use multi-threaded capture if available (OpenCV 4.5+)
        if hasattr(cv, 'CAP_PROP_HW_ACCELERATION'):
            self.cap.set(cv.CAP_PROP_HW_ACCELERATION, cv.VIDEO_ACCELERATION_ANY)

        # Try to use OpenCV's CAP_PROP_THREAD for multi-threaded capture (if supported)
        if hasattr(cv, 'CAP_PROP_THREAD'):
            self.cap.set(cv.CAP_PROP_THREAD, 1)

        # Try to set a higher buffer size (may help with USB cameras)
        self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)

        # TODO have to find way to get settings from v4l2-ctl -d /dev/video4 --list-formats-ext and get them saved here v4l2-ctl -d /dev/video4 --all
        self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc("M", "J", "P", "G"))

        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, float(self.current_width))
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, float(self.current_height))
        logger.info("successfully opened camera: ", self.camera_system_name, self.current_width, self.current_height)

    def close_camera(self):
        self.cap.release()
    def get_frames(self):
        ret, frame  = self.cap.read()
        if (not ret):
            return None
        return frame
    #     frames.append(frame)
    #     # print( self.camera_params[i])
    # # for i in range(0, self.num_cameras):
