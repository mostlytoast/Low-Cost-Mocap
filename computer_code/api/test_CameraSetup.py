import unittest
from unittest import mock
import numpy as np
import sys
import CameraSetup

# Patch sys.modules to mock cv2 and glob before importing the function
sys.modules["cv2"] = mock.MagicMock()
sys.modules["glob"] = mock.MagicMock()


class TestGenerateCalibrationData(unittest.TestCase):
    @mock.patch("CameraSetup.glob.glob")
    @mock.patch("CameraSetup.cv2")
    def test_generate_calibration_data_success(self, mock_cv2, mock_glob):
        # Prepare mocks
        mock_glob.return_value = [f"img_{i}.jpg" for i in range(9)]
        dummy_img = np.ones((100, 100, 3), dtype=np.uint8)
        dummy_gray = np.ones((100, 100), dtype=np.uint8)
        mock_cv2.imread.return_value = dummy_img
        mock_cv2.cvtColor.return_value = dummy_gray
        # findChessboardCorners returns (True, corners)
        mock_cv2.findChessboardCorners.return_value = (
            True,
            np.zeros((30, 1, 2), dtype=np.float32),
        )
        mock_cv2.cornerSubPix.return_value = np.zeros((30, 1, 2), dtype=np.float32)
        mock_cv2.drawChessboardCorners.return_value = dummy_img
        mock_cv2.imshow.return_value = None
        # Simulate pressing ENTER (not ESC)
        mock_cv2.waitKey.side_effect = [13] * 9
        mock_cv2.imwrite.return_value = True
        # calibrateCamera returns dummy calibration data
        mtx = np.eye(3)
        dist = np.zeros((5, 1))
        mock_cv2.calibrateCamera.return_value = (True, mtx, dist, None, None)

        result = CameraSetup.generate_calibration_data(
            cam_images_folder_name="test_folder", checkerboard=(5, 6), dimension=30
        )
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0].shape, (3, 3))
        self.assertEqual(result[1].shape, (5, 1))

    @mock.patch("CameraSetup.glob.glob")
    def test_generate_calibration_data_not_enough_images(self, mock_glob):
        mock_glob.return_value = ["img_1.jpg"] * 3  # Less than 9 images
        with self.assertRaises(SystemExit):
            CameraSetup.generate_calibration_data(
                cam_images_folder_name="test_folder", checkerboard=(5, 6), dimension=30
            )


if __name__ == "__main__":
    unittest.main()
