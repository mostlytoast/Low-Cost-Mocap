import json
import time
import computer_code.Ui.cameraCalibGui as cameraCalibGui
import sys
from PyQt5.QtWidgets import QApplication, QAction

from PyQt5.QtCore import Qt, QTimer, QObject, QEvent

from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QPoint
import json
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtTest import QTest
import json
import time


class PlaybackWorker(QObject):
    finished = pyqtSignal()
    play_event = pyqtSignal(dict)  # Emitted for each event to be played

    def __init__(self, filename="recorded_events.json"):
        super().__init__()
        self.filename = filename
        self._is_running = True

    def stop(self):
        self._is_running = False

    @pyqtSlot()
    def run(self):
        with open(self.filename, "r") as f:
            events = json.load(f)

        start_time = time.time()
        for event in events:
            if not self._is_running:
                break
            self.play_event.emit(event)
            time.sleep(0.2)  # mimic QTest.qWait(200)

        self.finished.emit()

class EventTypes:
    """Stores a string name for each event type.

    With PySide2 str() on the event type gives a nice string name,
    but with PyQt5 it does not. So this method works with both systems.
    https://stackoverflow.com/questions/62196835/how-to-get-string-name-for-qevent-in-pyqt5
    """

    def __init__(self):
        """Create mapping for all known event types."""
        self.string_name = {}
        for name in vars(QEvent):
            attribute = getattr(QEvent, name)
            if type(attribute) == QEvent.Type:
                self.string_name[attribute] = name

    def as_string(self, event: QEvent.Type) -> str:
        """Return the string name for this event."""
        try:
            return self.string_name[event]
        except KeyError:
            return f"UnknownEvent:{event}"


class MyEventFilter(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.events = []
        self.view = cameraCalibGui
        self.window = None
        # self.tracked_events=[10,5,11,127,129,128,2,3]
        self.tracked_events = [2, 3]

        self.start_time = time.time()

    def set_window(self, window):
        self.window = window

    def get_variable_name(self, obj):
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

    # def eventFilter(self, watched, event):
    #     var_name = self.get_variable_name(watched)
    #     event_str = EventTypes().as_string(event.type())
    #     # self.print_child_widgets(self.view.MainWindow)
    #     # if event.type() not in self.events:
    #     #     self.events.append(event.type())

    #     #     print(event)
    #     # print(event)

    #     if event.type() == QEvent.Type.KeyPress:
    #         print(f"Key press event on {watched.objectName()}: {event.key()}")
    #     # You can add more event types to log
    #     if event.type() == QEvent.Type.MouseButtonPress:
    #         if (watched.objectName() == "QMenuClassWindow"):
    #             print()
    #             # to cause crash put breakpoint on above line then run this script in debug mode, and click on file menu this causes system to hang
    #         else:
    #             print(f"Key press event on {watched.objectName()}")
    #     if var_name != None:

    #         print(var_name,watched.objectName(),event_str,event.type())

    #     return super().eventFilter(watched, event)

    def eventFilter(self, watched, event):
        if event.type() in self.tracked_events:
            event_data = {
                "timestamp": time.time() - self.start_time,
                "event_type": EventTypes().as_string(event.type()),
                "type_code": int(event.type()),
                "object_name": watched.objectName(),
                "variable_name": self.get_variable_name(watched),
            }

            if event.type() == QEvent.KeyPress:
                event_data.update(
                    {"key": event.key(), "modifiers": int(event.modifiers())}
                )

            elif event.type() == QEvent.MouseButtonPress:
                event_data.update(
                    {
                        "button": int(event.button()),
                        "x": event.pos().x(),
                        "y": event.pos().y(),
                    }
                )

            self.events.append(event_data)
            print("Recorded:", event_data)

        return super().eventFilter(watched, event)

    def save_events_to_file(self, filename="recorded_events.json"):
        with open(filename, "w") as f:
            json.dump(self.events, f, indent=2)

    def load_and_play_events(self, window, filename="recorded_events.json"):
        with open(filename, "r") as f:
            events = json.load(f)

        var_map = {
            self.get_variable_name(child): child
            for child in window.findChildren(QObject)
            if self.get_variable_name(child)
        }
        object_map = {
            child.objectName(): child
            for child in window.findChildren(QObject)
            if child.objectName()
        }
        for event in events:
            obj = var_map.get(event["variable_name"])
            if not obj:
                obj = object_map.get(event["object_name"])
                if not obj:
                    print(f"Skipped event, no object named '{event['variable_name']}'")

                    print(f"Skipped event, no object named '{event['object_name']}'")
                    continue

            # ✅ Skip QAction objects
            if isinstance(obj, QAction):
                print(f"Skipped QAction object: {obj.objectName()}")
                continue

            # if event['type_code'] == QEvent.KeyPress:
            #     QTest.keyClick(obj, Qt.Key(event['key']), Qt.KeyboardModifiers(event['modifiers']))

            if event["type_code"] == QEvent.MouseButtonPress:
                pos = QPoint(event["x"], event["y"])
                QTest.mouseClick(
                    obj, Qt.MouseButton(event["button"]), Qt.NoModifier, pos
                )

            QTest.qWait(200)  # Simulate slight delay between events
    def connect_playback(self, window):
        self.thread = QThread()
        self.worker = PlaybackWorker("recorded_events.json")
        self.worker.moveToThread(self.thread)

        self.worker.play_event.connect(lambda evt: self.handle_event(window, evt))
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()
    def handle_event(self, window, event):
        var_map = {
            self.get_variable_name(child): child
            for child in window.findChildren(QObject)
            if self.get_variable_name(child)
        }
        object_map = {
            child.objectName(): child
            for child in window.findChildren(QObject)
            if child.objectName()
        }

        obj = var_map.get(event["variable_name"]) or object_map.get(event["object_name"])
        if not obj or isinstance(obj, QAction):
            print(f"Skipped event: {event}")
            return

        if event["type_code"] == QEvent.MouseButtonPress:
            pos = QPoint(event["x"], event["y"])
            QTest.mouseClick(
                obj, Qt.MouseButton(event["button"]), Qt.NoModifier, pos
            )


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     # global event_filter
#     filt = MyEventFilter
#     # event_filter = filt()
#     # app.installEventFilter(event_filter)  # Install the filter on the application


#     window =  cameraCalibGcomputer_code.Ui.MainWindow()
#     # event_filter.set_window(window)
#     window.show()
#     QTimer.singleShot(1000, lambda: MyEventFilter.load_and_play_events(window, 'recorded_events.json'))
#     # try:
#     sys.exit(app.exec())
#     # finally:
#     #     event_filter.save_events_to_file()
def record():
    app = QApplication(sys.argv)

    # ✅ Instantiate the event filter
    event_filter = MyEventFilter()
    app.installEventFilter(event_filter)

    # ✅ Create and set the window
    window = cameraCalibGcomputer_code.Ui.MainWindow()
    event_filter.set_window(window)
    window.show()

    # ✅ Use the instance method, not the class method
    # QTimer.singleShot(1000, lambda: event_filter.load_and_play_events(window, 'recorded_events.json'))

    try:
        sys.exit(app.exec())
    finally:
        event_filter.save_events_to_file()

# def play():
#     app = QApplication(sys.argv)
#     event_filter = MyEventFilter()
#     window = cameraCalibGcomputer_code.Ui.MainWindow()
#     event_filter.set_window(window)
#     window.show()

#     QTimer.singleShot(1000, lambda: event_filter.connect_playback(window))

#     sys.exit(app.exec())
def play():
    app = QApplication(sys.argv)

    # ✅ Instantiate the event filter
    event_filter = MyEventFilter()
    # app.installEventFilter(event_filter)

    # ✅ Create and set the window
    window = cameraCalibGcomputer_code.Ui.MainWindow()
    event_filter.set_window(window)
    window.show()

    # ✅ Use the instance method, not the class method
    QTimer.singleShot(
        1000, lambda: event_filter.load_and_play_events(window, "recorded_events.json")
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    # play()
    record()
