import threading
import queue
import time
import computer_code.api.camera as Camera

import logging
logger = logging.getLogger(__name__)
import cv2
import numpy as np
from multiprocessing import Process, Queue
from collections import defaultdict

class CameraProcess:
    def __init__(self, camera_system_name, output_queue):
        self.camera = Camera.Camera(camera_system_name)
        self.frame_queue = queue.Queue(maxsize=10)
        self.running = False
        self.output_queue = output_queue
        self.captureThread = threading.Thread(target=self._captureLoop, name="CaptureThread")
        self.processThread = threading.Thread(target=self._processLoop, name="ProcessThread")

    def start(self):
        logging.debug("Starting CameraProcess...")
        self.running = True
        self.camera.setDistortionCoef( [
                [
                    0.07002292606292972,
                    -0.40894724240016145,
                    -0.020332839259062062,
                    0.00025543761137419597,
                    1.157665841456218
                ]
            ])
        self.camera.setIntrinsicMatrix ([
                    [
                        677.8118436477158,
                        0.0,
                        369.67423322200443
                    ],
                    [
                        0.0,
                        682.103355075851,
                        283.2898247123011
                    ],
                    [
                        0.0,
                        0.0,
                        1.0
                    ]
                ])
        self.camera.setRotation(0)
        self.camera.setResolution(0)
        # TODO refactor to be cleaner
        self.map1, self.map2 = cv2.initUndistortRectifyMap(
            self.camera.intrinsic_matrix,
            self.camera.distortion_coef,
            None,
            self.camera.intrinsic_matrix,
            (self.camera.getWidth(), self.camera.getHeight()),
            cv2.CV_16SC2
        )
        self.camera.open_camera()
        self.captureThread.start()
        self.processThread.start()

    def stop(self):
        logging.debug("Stopping CameraProcess...")
        self.running = False
        self.captureThread.join()
        self.processThread.join()
        logging.debug("CameraProcess stopped.")

    def _captureLoop(self):
        """Simulate capturing frames from a camera."""
        while self.running:
            # TODO figure out how to handle live camera setting changes? 
            if not self.frame_queue.full():
                frame = self.camera.get_frames()
                self.frame_queue.put(frame)
                logging.debug(f"[Capture] Captured frame")

    def _processLoop(self):
        """Simulate processing frames."""
        frame_id = 0
        while self.running or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=0.5)
                if frame.any():
                    frame = self._applyRotAndCorrection(frame)
                    frame, image_points = self._findDot(frame)
                    self.output_queue.put((self.camera.camera_system_name, frame_id, image_points))
                    # print(image_points)
                    frame_id += 1
                    
                # logging.debug(f"[Process] Processed frame {frame} -> result {frame}")
            except queue.Empty:
                continue
    
    def _applyRotAndCorrection(self, frame):
            # frames, _ = self.cameras[i].read()
        # TODO seams to be errors here when cameras disconnect 
        frame = np.rot90(frame, k=self.camera.getRotation())
        # TODO should we be squaring images? might be causing issues 
        frame = self._makeSquare(frame)
        frame = cv2.remap(frame, self.map1, self.map2, interpolation=cv2.INTER_LINEAR)
        # frame = cv2.undistort(frame, (self.camera.intrinsic_matrix), self.camera.distortion_coef)
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
        kernel = np.array([[-2,-1,-1,-1,-2],
                            [-1,1,3,1,-1],
                            [-1,3,4,3,-1],
                            [-1,1,3,1,-1],
                            [-2,-1,-1,-1,-2]])
        frame = cv2.filter2D(frame, -1, kernel)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def _findDot(self, frame):
        # frame = cv2.GaussianBlur(frame,(5,5),0)
        grey = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        grey = cv2.threshold(grey, 255*0.2, 255, cv2.THRESH_BINARY)[1]
        contours,_ = cv2.findContours(grey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        frame = cv2.drawContours(frame, contours, -1, (0,255,0), 1)
        #TODO separate into _drawDotsOnFrame for draw operations for speed toggle? 
        image_points = []
        for contour in contours:
            moments = cv2.moments(contour)
            if moments["m00"] != 0:
                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                cv2.putText(frame, f'({center_x}, {center_y})', (center_x,center_y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100,255,100), 1)
                cv2.circle(frame, (center_x,center_y), 1, (100,255,100), -1)
                image_points.append([center_x, center_y])

        if len(image_points) == 0:
            image_points = [[None, None]]

        return frame, image_points
    
    def _makeSquare(self, oldFrame):
        x, y, _ = oldFrame.shape
        size = max(x, y)
        newFrame = np.zeros((size, size, 3), dtype=np.uint8)
        ax,ay = (size - oldFrame.shape[1])//2,(size - oldFrame.shape[0])//2
        newFrame[ay:oldFrame.shape[0]+ay,ax:ax+oldFrame.shape[1]] = oldFrame

        # Pad the newFrame array with edge pixel values
        # Apply feathering effect
        feather_pixels = 8
        for i in range(feather_pixels):
            alpha = (i + 1) / feather_pixels
            newFrame[ay - i - 1, :] = oldFrame[0, :] * (1 - alpha)  # Top edge
            newFrame[ay + oldFrame.shape[0] + i, :] = oldFrame[-1, :] * (1 - alpha)  # Bottom edge
        return newFrame


def sync_loop(queues):
    buffer = defaultdict(dict)
    num_cams = len(queues)

    while True:
        start_time = time.time() # Record start of loop
        for cam_id, q in enumerate(queues):
            if not q.empty():
                cam_id, frame_id, result = q.get()
                buffer[frame_id][cam_id] = result

                if len(buffer[frame_id]) == num_cams:
                    synced = buffer.pop(frame_id)
                    # print(synced)
                    output = ""
                    for name in synced: 
                        output+= f"{name}, {synced[name][0]} "
                    # print(output)
                    # main_process(frame_id, synced)
                    fps = 1.0 / (time.time() - start_time)
                    print(f"FPS: {fps:.2f}")

def spawnCamera(cam_name, q):
    cam = CameraProcess(cam_name, q)
    cam.start()

    try:
        while True:
            time.sleep(1)
    finally:
        cam.stop()

if __name__ == "__main__":
    queues = []
    processes = []

    for cam_name in ["Arducam OV9281 USB Camera: Ardu (usb-0000:07:00.3-2.1.3):","Arducam OV9281 USB Camera: Ardu (usb-0000:07:00.3-2.1.4):","Arducam OV9281 USB Camera: Ardu (usb-0000:07:00.3-2.2):"]:
        q = Queue(maxsize=10)
        p = Process(target=spawnCamera, args=(cam_name, q))
        p.start()

        queues.append(q)
        processes.append(p)

    sync_loop(queues)
    # queues = []
    # cam = CameraProcess("Arducam OV9281 USB Camera: Ardu (usb-0000:07:00.3-2.1.3):",queues)
    

    # cam.start()

    try:
        time.sleep(10)  # let it run
    finally:
        for p in processes:
            p.terminate()
            p.join()
