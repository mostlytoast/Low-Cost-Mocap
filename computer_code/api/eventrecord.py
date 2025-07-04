# # Example of using an event filter (conceptual)
# import sys
import viewapp 
# from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
# from PyQt6.QtCore import QObject, QEvent
# import math
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QGridLayout,
    QAction,
)
import inspect 
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import Qt,QTimer,QObject,QEvent
from PyQt5.QtGui import QPixmap, QImage
import index
from viewer3d import QGLControllerWidget
import time
from PyQt5 import QtWidgets, QtCore
import numpy as np
import file_mech

# import openmesh as om
import style

from helpers import Cameras
# class MainWindow(QtWidgets.QMainWindow):

#     def __init__(self, parent=None):
#         super(MainWindow, self).__init__(parent)
#         self.setWindowTitle("Low-Cost Mocap PyQt")
#         # print("parent",parent)
#         self.parent = parent
#         self.cameras = Cameras.instance()
#         self.camera_stream_running = False
#         self.camera_stream_thread = None
#         self.has_world_calibration = False
#         self.has_collected_points = False
#         self.collecting_points = False
#         self.is_triangulating_points = False
#         self.is_locating_objects = False
#         self.is_acquiring_floor = False
#         self.is_acquiring_origin = False
#         self.is_acquiring_scale= False
#         self.has_origin = False
#         self.has_scale = False
#         # data variables
#         self.captured_points_for_pose = []
#         self.object_points = []

#         self.last_time = 0
#         # self.cameras.to_world_coords_matrix = [[0.9941338485260931,0.0986512964608827,-0.04433748889242502,0.9938296704767513],[-0.0986512964608827,0.659022672138982,-0.7456252673517598,2.593331619023365],[0.04433748889242498,-0.7456252673517594,-0.6648888236128887,2.9576262456228286],[0,0,0,1]]
#         # self.cameras.to_world_coords_matrix = np.eye(4)
#         # self.cameras.camera_poses = ([{"R":[[1,0,0],[0,1,0],[0,0,1]],"t":[0,0,0]},{"R":[[-0.13639683654819235,0.5218092394166619,-0.8420872998917929],[-0.4139150519535063,0.7422608899144861,0.5269944032621987],[0.9000390173464546,0.42043297796766566,0.11474266116518528]],"t":[0.26932272217012254,-0.5101944343371594,0.89286825065571]}])

#         self.camera_thread = index.MyThread()
#         # self.camera_thread.frame_signal.connect(self.setImage)
#         # self.camera_thread.data_signal.connect(self.setData)
#         self.file = file_mech.file_dialog(self)
#         self.central_widget = QWidget()
#         self.layout = QVBoxLayout()
#         self.central_widget.setLayout(self.layout)
#         self.setCentralWidget(self.central_widget)

#         # self.resize(640, 480)
#         # TODO probs just include in this file and not as separate css
#         self.setStyleSheet(style.style)


class MyEventFilter(QObject):
    
    def __init__(self,parent = None):
        super().__init__(parent)
        self.events = [] 
        self.view = viewapp
        self.window = None
    def set_window(self,window):
        self.window = window
    def get_variable_name(self,obj):
        """Returns the name of the variable pointing to the given object in the caller's scope."""
        cls = self.window
        if cls == None:
            return None
        # caller_frame = inspect.currentframe().f_back
        # caller_frame.f_code
        # if caller_frame:
        #     for name, value in caller_frame.f_locals.items():
        #         if value is obj:
        #             return name
        
        for attr_name in dir(cls):
            # Skip built-in/private attributes
            # if attr_name.startswith('__'):
            #     continue
            try:
                if getattr(cls, attr_name) is obj:
                    return attr_name
            except AttributeError:
                continue
        return None
    # def print_child_widgets(self,parent):
    #     for child in parent.findChildren(QWidget):
    #         print(f"Class: {type(child).__name__}, ObjectName: {child.objectName()}")
    def eventFilter(self, watched, event):
        # self.print_child_widgets(self.view.MainWindow)
        if event.type() not in self.events:
            self.events.append(event.type())
            
            print(event)
        # print(event)
        if event.type() == QEvent.Type.KeyPress:
            print(f"Key press event on {watched.objectName()}: {event.key()}")
        # You can add more event types to log
        if event.type() == QEvent.Type.MouseButtonPress:
            if (watched.objectName() == "QMenuClassWindow"):
                # watched.actions()
                print()
                # to cause crash put breakpoint on above line then run this script in debug mode, and click on file menu this causes system to hang 
            else:
                print(f"Key press event on {watched.objectName()}")
            print(self.get_variable_name(watched))

            

        return super().eventFilter(watched, event)

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Event Filter Example")
#         self.label = QLabel("Click or press a key")
#         self.setCentralWidget(self.label)
#         self.label.setObjectName("MyLabel")  # Set an object name to identify the widget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    event_filter = MyEventFilter()
    app.installEventFilter(event_filter)  # Install the filter on the application

    
    window =  viewapp.MainWindow()
    event_filter.set_window(window)
    window.show()

    sys.exit(app.exec())
# ```

# **Important Considerations:**

# *   **Performance:**  Logging every event can impact performance, so consider what level of detail is necessary.
# *   **Purpose of recording:**  The best approach depends on why you need to record user actions (e.g., testing, debugging, user analysis).

# By using one of these techniques, you can effectively record user actions in your PyQt application.
