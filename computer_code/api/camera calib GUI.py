from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    # QListWidgetItem,
    QShortcut,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QAction,
    QPushButton,
    QLabel,
    QComboBox
)
from PyQt5.QtGui import QKeySequence, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import  pyqtSlot as Slot
# import sys
import cameraThread
import videoSubSystem
from PyQt5.QtWidgets import QSplitter



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Setup")
        self.camera_thread = cameraThread.MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
        self.initUI()

    def initUI(self):
        # TODO need new data structure that better supports edits 
        self.data = [ {
                    "intrinsic_matrix": [
                        [677.8118436477158, 0.0, 369.67423322200443],
                        [0.0, 682.103355075851, 283.2898247123011],
                        [0.0, 0.0, 1.0],
                    ],
                    "distortion_coef": [
                        [
                            0.07002292606292972,
                            -0.40894724240016145,
                            -0.020332839259062062,
                            0.00025543761137419597,
                            1.157665841456218,
                        ]
                    ],
                    "rotation": 0,
                    "id": 3,
                    "name": "Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-1.4):",
                    "width": 800,
                    "height": 600,
                    "connected": False,
                        "calibrated": False,

                    "added": False

                },
                {
                    
                        "intrinsic_matrix": [
                            [679.654681050567, 0.0, 404.0916055013056],
                            [0.0, 678.2903122373327, 280.39271414461007],
                            [0.0, 0.0, 1.0],
                        ],
                        "distortion_coef": [
                            [
                                0.04194078685957363,
                                -0.007168281261102275,
                                -0.009100180545490017,
                                0.004533057678646769,
                                -0.17059294063428096,
                            ]
                        ],
                        "rotation": 0,
                        "id": 2,
                        "name": "Arducam OV9281 USB Camera: Ardu (usb-0000:08:00.3-2.1.1):",
                        "width": 800,
                        "height": 600,
                        "connected": False,
                        "calibrated": False,

                        "added": True

                    
                }
                ]
            
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        save_action = QAction("save", self)
        #   save_action.triggered.connect()
        file_menu.addAction(save_action)

        open_action = QAction("open", self)
        #   open_action.triggered.connect()
        file_menu.addAction(open_action)

        self.setWindowTitle("QMenuBar Example")
        self.setGeometry(300, 300, 400, 300)
        self.main_layout = QVBoxLayout()
        self.webcam_settings_layout = QVBoxLayout()
        self.webcam_preview_layout = QHBoxLayout()
        self.webcam_list_layout = QHBoxLayout()
        self.move_buttons_layout = QVBoxLayout()

        # added webcams
        self.added_webcam_list = QListWidget()
        # self.added_webcam_list.addItem("0")
        # self.added_webcam_list.addItem("3")
        # self.added_webcam_list.addItem("2")
        self.webcam_list_layout.addWidget(self.added_webcam_list)
        # Create a vertical layout for the edit button and label
        self.edit_layout = QVBoxLayout()
        self.edit_button = QPushButton("edit")
        self.edit_button.setEnabled(False)  # Initially greyed out
        self.edit_button.clicked.connect(self.add_webcam)

        self.edit_layout.addWidget(self.edit_button)
        self.move_buttons_layout.addLayout(self.edit_layout)

        
        self.reload_button = QPushButton("reload")
        self.reload_button.clicked.connect(self.reload_cameras)
        self.move_buttons_layout.addWidget(self.reload_button)
        self.add_button = QPushButton("<")
        self.add_button.clicked.connect(self.add_webcam)
        self.move_buttons_layout.addWidget(self.add_button)
        self.setup_button = QPushButton(">")
        self.setup_button.clicked.connect(self.remove_webcam)
        self.move_buttons_layout.addWidget(self.setup_button)
        self.webcam_list_layout.addLayout(self.move_buttons_layout)

        # webcams not added
        self.non_added_webcam_list = QListWidget()
        # self.non_added_webcam_list.addItem("webcam 4")
        # self.non_added_webcam_list.addItem("webcam 2")
        self.webcam_list_layout.addWidget(self.non_added_webcam_list)
        
        # Enable the discover button only when an item is selected in either list
        self.added_webcam_list.itemSelectionChanged.connect(
            lambda: self.edit_button.setEnabled(
                bool(self.added_webcam_list.selectedItems()) or bool(self.non_added_webcam_list.selectedItems())
            )
        )
        self.non_added_webcam_list.itemSelectionChanged.connect(
            lambda: self.edit_button.setEnabled(
                bool(self.added_webcam_list.selectedItems()) or bool(self.non_added_webcam_list.selectedItems())
            )
        )
        

        self.main_layout.addLayout(self.webcam_list_layout)
        # Shortcuts for deleting items in each list
        self.update_list()

        self.delete_shortcut1 = QShortcut(
            QKeySequence(Qt.Key_Right), self.added_webcam_list
        )
        self.delete_shortcut1.setContext(Qt.WidgetShortcut)
        self.delete_shortcut1.activated.connect(self.remove_webcam)

        self.delete_shortcut2 = QShortcut(
            QKeySequence(Qt.Key_Left), self.non_added_webcam_list
        )
        self.delete_shortcut2.setContext(Qt.WidgetShortcut)
        self.delete_shortcut2.activated.connect(self.add_webcam)

        self.open_btn = QPushButton("Open The Camera", clicked=self.open_camera)
        self.webcam_settings_layout.addWidget(self.open_btn)
        # Create a vertical layout for editable items based on self.data[0]
        self.editable_fields_layout = QVBoxLayout()
        self.editable_labels = {}
        index = 0
        
        # Connect selection changes to update_editable_fields
        # self.added_webcam_list.itemSelectionChanged.connect(self.update_editable_fields)
        # self.non_added_webcam_list.itemSelectionChanged.connect(self.update_editable_fields)

        # # Initial population
        # self.update_editable_fields()
        # # Dropdown to edit a variable (e.g., "rotation" of the first webcam)
        # combobox = QComboBox(self)
        # combobox.setEditable(True)
        # combobox.addItem("0")
        # combobox.addItem("90")
        # combobox.addItem("180")
        # combobox.addItem("270")
        # combobox.setCurrentText(str(self.data[0]["rotation"]))

        

        # combobox.currentTextChanged.connect(self.on_combobox_changed)
        
        # self.editable_fields_layout.addWidget(combobox)

        self.webcam_settings_layout.addLayout(self.editable_fields_layout)
        
        # Use a QSplitter to allow resizing between settings and preview

        self.webcam_settings_widget = QWidget()
        self.webcam_settings_widget.setLayout(self.webcam_settings_layout)
        self.webcam_settings_widget.setMinimumWidth(200)  # Minimum width
        self.webcam_settings_widget.setMaximumWidth(400)  # Optional: Maximum width

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignRight)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.webcam_settings_widget)
        splitter.addWidget(self.label)
        splitter.setSizes([200, 400])  # Initial sizes

        self.webcam_preview_layout.addWidget(splitter)

        self.camera_thread = cameraThread.MyThread(0)
        self.camera_thread.frame_signal.connect(self.setImage)
        self.main_layout.addLayout(self.webcam_preview_layout)
        # Set main_layout on a QWidget and set as central widget
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
    # Function to update editable fields when selection changes
    # def update_editable_fields(self):
    #     # Remove all widgets from the layout
    #     while self.editable_fields_layout.count():
    #         item = self.editable_fields_layout.takeAt(0)
    #         widget = item.widget()
    #         if widget is not None:
    #             widget.deleteLater()
    #     self.editable_labels.clear()

    #     # Determine which list and item is selected
    #     selected_item = None
    #     if self.added_webcam_list.selectedItems():
    #         selected_item = self.added_webcam_list.selectedItems()[0]
    #     elif self.non_added_webcam_list.selectedItems():
    #         selected_item = self.non_added_webcam_list.selectedItems()[0]
    #     idx = 0
    #     if selected_item:
    #         idx = selected_item.data(Qt.UserRole)
    #     for key, value in self.data[idx].items():
    #         label = QLabel(f"{key}: {value}")
    #         label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    #         self.editable_fields_layout.addWidget(label)
    #         self.editable_labels[key] = label

    # def on_combobox_changed(self,value):
    #     try:
    #         self.data[0]["rotation"] = int(value)
    #         self.editable_labels["rotation"].setText(f"rotation: {value}")
    #     except ValueError:
    #         pass  # Ignore invalid input
    def remove_webcam(self):
        selected_items = self.added_webcam_list.selectedItems()
        for item in selected_items:
            self.added_webcam_list.takeItem(self.added_webcam_list.row(item))
            self.non_added_webcam_list.addItem(item)
            self.data[item.data(Qt.UserRole)]["added"] = False
  

    def add_webcam(self):
        selected_items = self.non_added_webcam_list.selectedItems()
        for item in selected_items:
            self.non_added_webcam_list.takeItem(self.non_added_webcam_list.row(item))
            self.added_webcam_list.addItem(item)
            self.data[item.data(Qt.UserRole)]["added"] = True
       
                

    def save(self):
        RuntimeWarning("not implemented yet")

    def open(self):
        RuntimeWarning("not implemented yet")

    def update_list(self):
        self.added_webcam_list.clear()
        self.non_added_webcam_list.clear()
        for index, webcam in enumerate(self.data):
            item = None
            # get targeted list 
            target_list = self.added_webcam_list if webcam["added"] else self.non_added_webcam_list
            target_list.addItem(webcam["name"])
            item = target_list.item(target_list.count() - 1)
            if not webcam["calibrated"]:
                item.setForeground(Qt.gray)
                item.setToolTip("not calibrated")
            if not webcam["connected"]:
                item.setForeground(Qt.red)
                item.setToolTip("not connected")
            item.setData(Qt.UserRole, index)


    def test(self):
        print("test")
    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def open_camera(self):
        item = self.added_webcam_list.currentItem()
        if not item:
            return
      
        name = self.data[item.data(Qt.UserRole)]["name"] 
        if not name:
            return
        camera_id = videoSubSystem.get_id_from_name(name)
        print(camera_id)
        self.camera_thread.set_camera_id(camera_id)

        self.camera_thread.start()
    """_summary_ reloads the list of cameras connected to the system
    """
    def reload_cameras(self):
        # TODO have to find way of adding newly added cameras in system to list 

        attached_webcams = videoSubSystem.listWebcams()
            # TODO find better way of doing this 
        for current_webcams in self.data:
            for attached_webcam in attached_webcams:
                if not any(cam["name"] == attached_webcam[0] for cam in self.data):
                    self.data.append({
                        "intrinsic_matrix": [],
                        "distortion_coef": [],
                        "rotation": 0,
                        "id": attached_webcam[1] if len(attached_webcam) > 1 else -1,
                        "name": attached_webcam[0],
                        "width": 0,
                        "height": 0,
                        "connected": True,
                        "calibrated": False,
                        "added": False
                    })
            
            # assume its false
                current_webcams["connected"] = False

                if current_webcams["name"] == attached_webcam[0]:
                    current_webcams["connected"] = True
                    break
    

        self.update_list()
          
    # def search_data(self,search_attribute,value):
    #         # TODO make this support multiple matching felids 
    #         """_summary_ finds dictionary in data structure with same attribute as value 
    #         ex finds where data[search_attribute] == value

    #         Args:
    #             search_attribute (_type_): the key of dictionary to be searched  
    #             value (int):  index where search matches 
    #         """



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
