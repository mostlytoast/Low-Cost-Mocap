import os

import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import unittest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
import sys
import pyfakewebcam
# Import your code (adjust import based on your structure)
from cameraCalibGui import MainWindow
import pyvirtualcam
import colorsys
class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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


        with pyvirtualcam.Camera(width=1280, height=720, fps=20) as cam:
            print(f'Using virtual camera: {cam.device}')
            frame = np.zeros((cam.height, cam.width, 3), np.uint8)  # RGB
            h, s, v = (cam.frames_sent % 100) / 100, 1.0, 1.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            frame[:] = (r * 255, g * 255, b * 255)
            cam.send(frame)
            window = MainWindow()
            window.setup_widget.reload_button.click()
            self.assertTrue(window.setup_widget.non_added_webcam_list.count() > 0)
            print(window.setup_widget.non_added_webcam_list.count())
                # mock_alert_instance.exec.assert_called_once()

    def tearDown(self):
        # Avoid hanging widgets between tests
        for widget in QApplication.topLevelWidgets():
            widget.close()


if __name__ == "__main__":
    unittest.main()
