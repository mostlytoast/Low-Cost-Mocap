import unittest
from unittest import mock
import numpy as np
import sys
import CameraSetup
import json
import glob

# Patch sys.modules to mock cv2 and glob before importing the function
# sys.modules["cv2"] = mock.MagicMock()
import cv2

import unittest
import sys
from io import StringIO
from contextlib import redirect_stdout


class TestGenerateCalibrationData(unittest.TestCase):
    # @mock.patch("CameraSetup.glob.glob")
    # @mock.patch("CameraSetup.cv2")
    # def test_generate_calibration_data_success(self, mock_cv2, mock_glob):
    #     # Prepare mocks
    #     mock_glob.return_value = [f"img_{i}.jpg" for i in range(9)]
    #     dummy_img = np.ones((100, 100, 3), dtype=np.uint8)
    #     dummy_gray = np.ones((100, 100), dtype=np.uint8)
    #     mock_cv2.imread.return_value = dummy_img
    #     mock_cv2.cvtColor.return_value = dummy_gray
    #     # findChessboardCorners returns (True, corners)
    #     mock_cv2.findChessboardCorners.return_value = (
    #         True,
    #         np.zeros((30, 1, 2), dtype=np.float32),
    #     )
    #     mock_cv2.cornerSubPix.return_value = np.zeros((30, 1, 2), dtype=np.float32)
    #     mock_cv2.drawChessboardCorners.return_value = dummy_img
    #     mock_cv2.imshow.return_value = None
    #     # Simulate pressing ENTER (not ESC)
    #     mock_cv2.waitKey.side_effect = [13] * 9
    #     mock_cv2.imwrite.return_value = True
    #     # calibrateCamera returns dummy calibration data
    #     mtx = np.eye(3)
    #     dist = np.zeros((5, 1))
    #     mock_cv2.calibrateCamera.return_value = (True, mtx, dist, None, None)

    #     result = CameraSetup.generate_calibration_data(
    #         cam_images_folder_name="test_folder", checkerboard=(5, 6), dimension=30
    #     )
    #     self.assertIsInstance(result, tuple)
    #     self.assertEqual(result[0].shape, (3, 3))
    #     self.assertEqual(result[1].shape, (5, 1))

    # @mock.patch("CameraSetup.glob.glob")
    # def test_generate_calibration_data_not_enough_images(self, mock_glob):
    #     mock_glob.return_value = ["img_1.jpg"] * 3  # Less than 9 images
    #     with self.assertRaises(SystemExit):
    #         CameraSetup.generate_calibration_data(
    #             cam_images_folder_name="test_folder", checkerboard=(5, 6), dimension=30
    #         )

    def test_resolutions(self):
        with mock.patch("builtins.input", return_value="2"):
            print(CameraSetup.getResolution(4))
        # buffer = StringIO()
        # with redirect_stdout(buffer):
        #     print("Hello, stdout!")
        # self.assertEqual(buffer.getvalue(), "Hello, stdout!\n")

        # original_stdin = sys.stdin
        # sys.stdin = StringIO("test input\n")
        # try:
        #     input_value = input()
        #     self.assertEqual(input_value, "test input")
        # finally:
        #     sys.stdin = original_stdin

    def test_resolutions_work(self):
        # TODO for somereason when ran this pops up with a screen shot of the display?
        camera_name = "Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4):"
        camera_id = CameraSetup.get_id_from_name(camera_name)
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
        resolutions = CameraSetup.getResolution(camera_id)
        for res in resolutions:
            width, height = res
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            cap_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Resolution: {width} x {height}")
            assert (cap_width == width and cap_height == height)
            ret, img = cap.read()
            cv2.imshow("img", img)

    def test_generate_calibration_data_write_to_json(self):

        # cam_images_folder_name = 'cam_1'
        cam_images_folder_name_calibrated = f'{"calib_img"}_c'

        image_files = glob.glob(
            f'{"/home/tom/Projects/Low-Cost-Mocap/calib_img"}/*.jpg'
        )
        print(len(image_files))
        if len(image_files) < 9:
            print("Not enough images were found: at least 9 shall be provided!!!")
            exit(-1)
        images = []
        for fname in image_files:
            print(fname)
            img = cv2.imread(fname)
            images.append(img)

        mtx, dist = CameraSetup.generate_calibration_data(
            images, checkerboard=(5, 6), dimension=30
        )
        output = []
        data = {
            "intrinsic_matrix": mtx.tolist(),
            "distortion_coef": dist.tolist(),
            "rotation": 0,
            "id": 0,  # general id associated with camera for human use
            "name": "camera_name",
            "width": 0,
            "height": 0,
        }
        output.append(data)
        with open("computer_code/api/test.json", "w") as f:
            json.dump(output, f, indent=4)
        assert mtx is not None
        assert dist is not None

    @mock.patch("builtins.input", return_value="1")
    @mock.patch("subprocess.run")
    def test_getResolution_returns_correct_resolution(self, mock_run, mock_input):
        # Simulate v4l2-ctl output with three resolutions
        v4l2_output = (
            "Pixel Format: 'MJPG' (Motion-JPEG)\n"
            "\tSize: Discrete 640x480\n"
            "\tSize: Discrete 1280x720\n"
            "\tSize: Discrete 1920x1080\n"
        )
        mock_process = mock.Mock()
        mock_process.stdout = v4l2_output.encode("utf-8")
        mock_run.return_value = mock_process

        # User selects index 1 (1280x720)
        result = CameraSetup.getResolution(0)
        self.assertEqual(result[0], (640, 480))
        self.assertEqual(result[1], (1280, 720))
        self.assertEqual(result[2], (1920, 1080))

    @mock.patch("builtins.input", return_value="0")
    @mock.patch("subprocess.run")
    def test_getResolution_single_resolution(self, mock_run, mock_input):
        v4l2_output = (
            "Pixel Format: 'MJPG' (Motion-JPEG)\n" "\tSize: Discrete 800x600\n"
        )
        mock_process = mock.Mock()
        mock_process.stdout = v4l2_output.encode("utf-8")
        mock_run.return_value = mock_process

        result = CameraSetup.getResolution(1)[0]
        self.assertEqual(result, (800, 600))

    @mock.patch("builtins.input", return_value="0")
    @mock.patch("subprocess.run")
    def test_getResolution_no_discrete_sizes(self, mock_run, mock_input):
        v4l2_output = (
            "Pixel Format: 'MJPG' (Motion-JPEG)\n" "\tNo discrete sizes available\n"
        )
        mock_process = mock.Mock()
        mock_process.stdout = v4l2_output.encode("utf-8")
        mock_run.return_value = mock_process

        result = CameraSetup.getResolution(2)
        self.assertEqual(result, [])  # Should return [] if no resolutions found

    @mock.patch("builtins.input", return_value="0")
    @mock.patch("subprocess.run")
    def test_getResolution_handles_trailing_newline(self, mock_run, mock_input):
        v4l2_output = (
            "Pixel Format: 'MJPG' (Motion-JPEG)\n"
            "\tSize: Discrete 320x240\n"
            "\tSize: Discrete 640x480\n\n"
        )
        mock_process = mock.Mock()
        mock_process.stdout = v4l2_output.encode("utf-8")
        mock_run.return_value = mock_process

        result = CameraSetup.getResolution(3)

        self.assertEqual(result[0], (320, 240))
        self.assertEqual(result[1], (640, 480))


if __name__ == "__main__":
    unittest.main()
