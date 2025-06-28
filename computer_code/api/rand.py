# import os

# import numpy as np
# os.environ["QT_QPA_PLATFORM"] = "offscreen"

# import unittest
# from unittest.mock import patch, MagicMock
# from PyQt5.QtWidgets import QApplication,QAction
# import sys
# import pyfakewebcam
# # Import your code (adjust import based on your structure)
# from cameraCalibGui import MainWindow
# import pyvirtualcam
# import cv2
# import colorsys
# from PyQt5.QtTest import QTest
# from cameraThread import MyThread


# file = os.path.dirname(__file__) + "/calibImg/image_0.jpg"
# print(file)
# fnames = []
# # get image files 
# for i in range(12):
#     fnames.append(f"{os.path.dirname(__file__)}/calibImg/image_{i}.jpg")
#     print(fnames[i])

# with pyvirtualcam.Camera(width=1280, height=800, fps=20) as cam:
#     for name in fnames:
#         img = cv2.imread(name)
#         print(name)
#         cam.send(img)
#         input() 
#         print("next")
# # import colorsys
# # import numpy as np
# # import pyvirtualcam

# # with pyvirtualcam.Camera(width=1280, height=720, fps=20) as cam:
# #     print(f'Using virtual camera: {cam.device}')
# #     frame = np.zeros((cam.height, cam.width, 3), np.uint8)  # RGB
# #     while True:
# #         h, s, v = (cam.frames_sent % 100) / 100, 1.0, 1.0
# #         r, g, b = colorsys.hsv_to_rgb(h, s, v)
# #         frame[:] = (r * 255, g * 255, b * 255)
# #         cam.send(frame)
# #         cam.sleep_until_next_frame()