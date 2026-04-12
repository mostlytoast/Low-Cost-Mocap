import unittest
from unittest import mock
from unittest.mock import patch
import computer_code.api.videoSubSystem as videoSubSystem
import cv2

class TestVideoSubSystem(unittest.TestCase):
    def test_find_camera_detects_difference(self):
        # Simulate listWebcams output before and after camera is connected
        result_no_cam = [
            ["Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)", 0]
        ]
        result_with_cam = [
            ["Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)", 0],
            ["Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)", 4],
        ]

        # Patch input to skip user interaction, and patch listWebcams to return our simulated results\
        mock_output = (
            b"Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)\n"
            b"\t/dev/video0\n"
            b"Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)\n"
            b"\t/dev/video4\n"
            b"\n"
        )
        mock_completed_process = mock.Mock()
        mock_completed_process.stdout = mock_output

        with patch("computer_code.api.videoSubSystem.input", side_effect=["", ""]), patch(
            "computer_code.api.videoSubSystem.listWebcams", side_effect=[result_no_cam, result_with_cam]
        ):
            output = videoSubSystem.find_camera()
            assert output == [
                ["Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)", 4]
            ]

    def test_find_camera_no_difference(self):
        # Simulate no camera change
        result_no_cam = [
            ["Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)", 0]
        ]
        result_with_cam = [
            ["Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)", 0],
        ]
        with patch("computer_code.api.videoSubSystem.input", side_effect=["", ""]), patch(
            "computer_code.api.videoSubSystem.listWebcams", side_effect=[result_no_cam, result_with_cam]
        ):
            output = videoSubSystem.find_camera()
            assert output == []

    def test_find_camera_multiple_new_devices(self):
        # Simulate two new cameras connected
        result_no_cam = [
            ["Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)",0]
        ]
        result_with_cam = [
            ["Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)",0],
            
            ["Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)", 4],
            ["Logitech C920 HD Pro Webcam (usb-0000:00:14.0-6)",5]
        ]

        

        # use the patch function from Python’s unittest.mock module to temporarily replace
        #  videoSubSystem.input and videoSubSystem.listWebcams.
        with patch("computer_code.api.videoSubSystem.input", side_effect=["", ""]), patch(
            "computer_code.api.videoSubSystem.listWebcams", side_effect=[result_no_cam, result_with_cam]
        ):
            output = videoSubSystem.find_camera()
            assert output == [
                ["Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)", 4],
                ["Logitech C920 HD Pro Webcam (usb-0000:00:14.0-6)", 5],
            ]

    """_summary_ uses real camera setup to test find_camera 
    """

    def test_get_id_from_name(self):
        mock_output = (
            b"Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)\n"
            b"\t/dev/video0\n"
            b"Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)\n"
            b"\t/dev/video4\n"
            b"\n"
        )
        mock_completed_process = mock.Mock()
        mock_completed_process.stdout = mock_output

        with patch("subprocess.run", return_value=mock_completed_process), patch(
            "platform.system", return_value="linux"
        ):
            output = videoSubSystem.get_id_from_name(
                "Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)"
            )
            print(output)
            assert output == 4

    """_summary_ test listWebcams for linux in normal conditions 
    _expected_ return list of webcam names with unique usb id's and their ids
    """

    def test_listWebcams_returns_expected_output_linux(self):
        # Simulate subprocess.run returning a specific output
        mock_output = (
            b"Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)\n"
            b"\t/dev/video0\n"
            b"Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)\n"
            b"\t/dev/video4\n"
            b"\n"
        )
        mock_completed_process = mock.Mock()
        mock_completed_process.stdout = mock_output

        with patch("subprocess.run", return_value=mock_completed_process), patch(
            "platform.system", return_value="linux"
        ):
            result = videoSubSystem.listWebcams()
            expected = [
                ["Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)", 0],
                ["Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4)", 4],
            ]
            self.assertEqual(result, expected)

    def test_listWebcams_handles_no_devices(self):
        # Simulate subprocess.run returning only a newline (no devices)
        mock_output = b"\n"
        mock_completed_process = mock.Mock()
        mock_completed_process.stdout = mock_output

        with patch("subprocess.run", return_value=mock_completed_process), patch(
            "platform.system", return_value="linux"
        ):
            result = videoSubSystem.listWebcams()
            self.assertEqual(result, [])

    def test_listWebcams_handles_single_device(self):
        mock_output = (
            b"Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)\n"
            b"\t/dev/video0\n"
            b"\n"
        )
        mock_completed_process = mock.Mock()
        mock_completed_process.stdout = mock_output

        with patch("subprocess.run", return_value=mock_completed_process), patch(
            "platform.system", return_value="linux"
        ):
            result = videoSubSystem.listWebcams()
            expected = [
                ["Integrated Webcam: Integrated_Webcam_HD (usb-0000:00:14.0-5)", 0]
            ]
            self.assertEqual(result, expected)
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
        result = videoSubSystem.getResolution(0)
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

        result = videoSubSystem.getResolution(1)[0]
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

        result = videoSubSystem.getResolution(2)
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

        result = videoSubSystem.getResolution(3)

        self.assertEqual(result[0], (320, 240))
        self.assertEqual(result[1], (640, 480))

    """_summary_ test that resolutions actually work and can be applied to a real webcam attached to system
        """
    def test_resolutions_work(self):
        # TODO for somereason when ran this pops up with a screen shot of the display?
        camera_name = "Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.4):"
        camera_id = videoSubSystem.get_id_from_name(camera_name)
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
        resolutions = videoSubSystem.getResolution(camera_id)
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