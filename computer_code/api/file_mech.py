from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QGridLayout,
    QFileDialog,
    QMessageBox
)
from helpers import camera_pose_to_serializable, camera_pose_from_serializable, Cameras
import json
class file_dialog(QFileDialog):
    """provides a uniform way for both the camera calibration and normal app to access saved data 

    Args:
        QFileDialog (_type_): _description_
    """
    def __init__(self, parent=None):
        super(file_dialog, self).__init__(parent)
        self.save_path = ""
        self.parent = parent
        self.cameras = Cameras.instance()

        

    def saveFile(self):
            if self.save_path == "":

                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save File", "", "Json Files (*.json);;All Files (*.*)"
                )
                if file_path and not file_path.lower().endswith(".json"):
                    file_path += ".json"
                if file_path:
                    print(f"Selected file: {file_path}")
                    self.save_path = file_path
            # double check
            if self.save_path != "":
                try:
                    self.save_config_params()
                except Exception as e:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText(f"Can't save file: {e}")

                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    self.save_path = ""  # delete path so can save new files in future

    def save_as(self):
        self.save_path = ""
        self.saveFile()

    def openFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Configuration Files (*.json);;All Files (*.*)"
        )
        if file_path:
            print(f"Selected file: {file_path}")
            self.save_path = file_path
        # double check
        if self.save_path != "":
            try:
                self.load_config_params()
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Can't read file: {e}")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        self.save_path = ""  # delete path so can open new files in future
    def load_config_params(self):
        with open(self.save_path,"r") as f:
            data = json.load(f)
        self.cameras.camera_params = data["camera_params"]

        # cameras.configure()
        
        self.cameras.to_world_coords_matrix = data["to_world_coords_matrix"]
        self.cameras.camera_poses = camera_pose_from_serializable(data["camera_poses"])
        # if hasattr(self.parent, "load_config()"):
        self.parent.updates_config(data["camera_params"], data["camera_poses"], data["to_world_coords_matrix"])
        # return data["camera_params"], data["camera_poses"], data["to_world_coords_matrix"]
        # TODO how do we do camera poses 
    def save_config_params(self):
        data = {}
        data["camera_params"] = self.cameras.camera_params
        try:
            data["to_world_coords_matrix"] = self.cameras.to_world_coords_matrix.tolist()
        except:
            data["to_world_coords_matrix"]= []
        if (self.cameras.camera_poses != None):
            data["camera_poses"] = camera_pose_to_serializable(self.cameras.camera_poses)
        else: 
            data["camera_poses"] = []

        with open(self.save_path,"w") as f:
            json.dump(data,f)
    # TODO clean up by moving into app.py and camera calib GUI.py
