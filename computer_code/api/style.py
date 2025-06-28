style = """
QMainWindow {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Segoe UI', 'Consolas', 'Courier New', monospace;
    font-size: 12pt;
}
QMenuBar {
    background-color: #2d2d2d;
    color: #d4d4d4;
}
QMenuBar::item:selected {
    background: #37373d;
}
QMenu {
    background-color: #2d2d2d;
    color: #d4d4d4;
}
QMenu::item:selected {
    background: #37373d;
}
QPushButton {
    background-color: #2d2d2d;
    color: #d4d4d4;
    border: 1px solid #3c3c3c;
    padding: 4px 8px;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #37373d;
}
QPushButton:disabled {
    background-color: #232323;
    color: #6a6a6a;
}
QListWidget, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #232323;
    color: #d4d4d4;
    border: 1px solid #3c3c3c;
    selection-background-color: #094771;
    selection-color: #ffffff;
}
QLabel {
    color: #d4d4d4;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #232323;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #444444;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line, QScrollBar::sub-line {
    background: none;
}
QStackedWidget {
    background-color: #1e1e1e;
}
"""