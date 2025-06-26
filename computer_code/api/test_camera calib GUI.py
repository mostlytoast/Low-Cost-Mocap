import sys
import types
import pytest
from unittest.mock import MagicMock, patch

import PyQt5.QtWidgets as QtWidgets


# Patch all external dependencies before importing the MainWindow
@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Patch file_mech.file_dialog
    file_dialog_mock = MagicMock()
    file_dialog_mock.save_as = MagicMock()
    file_dialog_mock.saveFile = MagicMock()
    file_dialog_mock.openFile = MagicMock()
    monkeypatch.setattr("file_mech.file_dialog", lambda self: file_dialog_mock)

    # Patch helpers.Cameras.instance
    Cameras_mock = MagicMock()
    Cameras_mock.camera_params = []
    Cameras_mock.camera_poses = []
    Cameras_mock.to_world_coords_matrix = []
    monkeypatch.setattr("helpers.Cameras.instance", lambda: Cameras_mock)

    # Patch calibrationWidget.CalibrateWidget
    CalibrateWidget_mock = MagicMock()
    monkeypatch.setattr(
        "calibrationWidget.CalibrateWidget", lambda self: CalibrateWidget_mock
    )

    # Patch setupWidget.setup_window
    setup_window_mock = MagicMock()
    setup_window_mock.update_list = MagicMock()
    setup_window_mock.camera_thread = MagicMock()
    setup_window_mock.camera_thread.stop = MagicMock()
    monkeypatch.setattr("setupWidget.setup_window", lambda self: setup_window_mock)

    # Patch open for style.css
    monkeypatch.setattr(
        "builtins.open",
        lambda *a, **k: types.SimpleNamespace(
            __enter__=lambda s: s,
            __exit__=lambda s, exc_type, exc_val, exc_tb: None,
            read=lambda: "",
        ),
    )

    yield


@pytest.fixture
def app(qtbot):
    """Provide a QApplication instance."""
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def main_window(app):
    from cameraCalibGui import MainWindow

    window = MainWindow()
    return window


def test_mainwindow_initializes(main_window):
    # Test that the main window initializes and has expected attributes
    assert hasattr(main_window, "file")
    assert hasattr(main_window, "cameras")
    assert hasattr(main_window, "stacked_widget")
    assert hasattr(main_window, "calibrate_widget_instance")
    assert hasattr(main_window, "setup_widget")
    assert main_window.windowTitle() == "Camera calibration"


def test_calib_scratch_switches_stack(main_window):
    main_window.stacked_widget.setCurrentIndex = MagicMock()
    main_window.setup_widget.camera_thread.stop = MagicMock()
    main_window.calib_scratch()
    main_window.stacked_widget.setCurrentIndex.assert_called_with(0)
    main_window.setup_widget.camera_thread.stop.assert_called_once()


def test_calib_single_prints(monkeypatch, main_window, capsys):
    main_window.calib_single()
    captured = capsys.readouterr()
    assert captured.out == "\n"


def test_calib_copy_prints(monkeypatch, main_window, capsys):
    main_window.calib_copy()
    captured = capsys.readouterr()
    assert captured.out == "\n"


def test_show_setup_switches_stack(main_window):
    main_window.calibrate_widget_instance.camera_thread.stop = MagicMock()
    main_window.stacked_widget.setCurrentIndex = MagicMock()
    main_window.show_setup()
    main_window.calibrate_widget_instance.camera_thread.stop.assert_called_once()
    main_window.stacked_widget.setCurrentIndex.assert_called_with(1)


def test_updates_config_updates_cameras_and_list(main_window):
    camera_params = [1, 2, 3]
    camera_poses = [4, 5, 6]
    to_world_coords_matrix = [7, 8, 9]
    main_window.setup_widget.update_list = MagicMock()
    main_window.cameras.camera_params = None
    main_window.cameras.camera_poses = None
    main_window.cameras.to_world_coords_matrix = None
    main_window.updates_config(camera_params, camera_poses, to_world_coords_matrix)
    assert main_window.cameras.camera_params == camera_params
    assert main_window.cameras.camera_poses == camera_poses
    assert main_window.cameras.to_world_coords_matrix == to_world_coords_matrix
    main_window.setup_widget.update_list.assert_called_once()
