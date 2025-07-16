import unittest
from unittest import mock
import numpy as np
import sys
import computer_code.gui.CameraSetup as CameraSetup
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

   


if __name__ == "__main__":
    unittest.main()
