import os

import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import unittest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication,QAction
import sys
import pyfakewebcam
# Import your code (adjust import based on your structure)
from cameraCalibGui import MainWindow
import pyvirtualcam
import cv2
import colorsys
from PyQt5.QtTest import QTest
from cameraThread import MyThread

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
         # Only use offscreen in CI or headless environments
        if os.environ.get("SHOW_QT_GUI", "0") != "1":
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
        cls.app = QApplication.instance() or QApplication(sys.argv)

    # @patch("file_mech.file_dialog")
    # @patch("helpers.Cameras")
    # @patch("calibrationWidget.CalibrateWidget")
    # @patch("setupWidget.setup_window")
    def test_mainwindow_initialization(
        self
    ):
        # Mocks
        # mock_file_dialog.return_value = MagicMock()
        # mock_cameras.instance.return_value = MagicMock()
        # mock_calibrate_widget.return_value = MagicMock()
        # mock_setup_window.return_value = MagicMock()

        # Instantiate MainWindow
        window = MainWindow()

        # Basic assertions
        self.assertEqual(window.windowTitle(), "Camera calibration")
        self.assertGreaterEqual(window.stacked_widget.count(), 2)
        self.assertEqual(window.stacked_widget.currentWidget(), window.setup_widget)

    # @patch("main_window.Cameras")
    def test_check_for_webcams_false(self):
        # mock_camera_instance = MagicMock()
        # mock_camera_instance.added_cameras = []
        # mock_cameras.instance.return_value = mock_camera_instance

        with patch("alertWidget.alert_widget") as mock_alert:
            mock_alert_instance = MagicMock()
            mock_alert.return_value = mock_alert_instance

            window = MainWindow()
            result = window.check_for_webcams()

            self.assertFalse(result)
            mock_alert_instance.exec.assert_called_once()
    def test_check_for_webcams_true(self):
        # requires virtual camera to be loaded 
        # https://github.com/letmaik/pyvirtualcam
        file = os.path.dirname(__file__) + "/calibImg/image_0.jpg"
        print(file)
        fnames = []
        # get image files 
        for i in range(12):
            fnames.append(f"{os.path.dirname(__file__)}/calibImg/image_{i}.jpg")
            print(fnames[i])
            self.assertTrue(os.path.exists(fnames[i]))
        with pyvirtualcam.Camera(width=640, height=480, fps=20) as cam:
            img = cv2.imread(fnames[0])
            cam.send(img)
            window = MainWindow()

            window.setup_widget.reload_button.click()
            num_cams = window.setup_widget.non_added_webcam_list.count()
            self.assertTrue(num_cams > 0)
            print(num_cams)
            cam_index = 0 
            for i in range(num_cams):
                print(window.setup_widget.non_added_webcam_list.item(i).text(),flush=True)
                if window.setup_widget.non_added_webcam_list.item(i).text() == "Dummy video device (0x0000) (platform:v4l2loopback-000):":
                    window.setup_widget.non_added_webcam_list.item(i).setSelected(True)
                    cam_index = i
            
            window.setup_widget.add_button.click()  

            self.assertTrue(window.setup_widget.added_webcam_list.count() > 0)

            # self.find_action("calibrate from scratch").trigger()
            window.calib_scratch()
            # file_menu = window.menubar.actions()[1].menu()  # assuming "File" is the first
            # target_action = None
            
            # for action in file_menu.actions():
            #     if action.text() == "calibrate from scratch":
            #         action.trigger()
            #         break

            # print(window.stacked_widget.currentIndex())
            thread = MyThread.instance()
            window.calibrate_widget_instance.cameras.camera_params[cam_index]["exposure"]=12
            window.calibrate_widget_instance.cameras.camera_params[cam_index]["gain"]=39

            self.assertTrue(window.stacked_widget.currentIndex() == 0)
            for i,frames in enumerate(fnames):
                
                print(f"frame {frames}")
                img = cv2.imread(frames)
                cam.send(img)
                window.calibrate_widget_instance.capture_btn.click()
                print("img",thread.imgpoints)
                while(True):
                    if len( window.calibrate_widget_instance.camera_thread.imgpoints) >i:
                        break

            window.calibrate_widget_instance.next_finish_btn.click()
            output = window.calibrate_widget_instance.cameras.camera_params[window.camera_thread.camera_id].get("intrinsic_matrix")
            
            assert(output != [])
            
                # mock_alert_instance.exec.assert_called_once()

    # def find_action(window,title)->QAction:
        
    
    def tearDown(self):
        # Avoid hanging widgets between tests
        for widget in QApplication.topLevelWidgets():
            widget.close()


if __name__ == "__main__":
    unittest.main()
