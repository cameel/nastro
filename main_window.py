""" The main UI component of the application. Controls the whole window """

from PyKDE4.kdeui import KMainWindow, KDatePicker
from PyQt4.QtGui  import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QScrollArea, QTextEdit

class MainWindow(KMainWindow):
    def __init__(self):
        super().__init__()

        self.main_panel        = QWidget()
        self.left_panel        = QWidget(self.main_panel)
        self.date_picker       = KDatePicker(self.left_panel)
        self.left_panel_layout = QVBoxLayout(self.left_panel)
        self.left_panel_layout.addWidget(self.date_picker)
        self.left_panel_layout.addStretch()

        self.right_panel   = QWidget(self.main_panel)
        self.search_box    = QLineEdit(self.right_panel)
        self.note_area     = QScrollArea(self.right_panel)

        right_panel_layout = QVBoxLayout(self.right_panel)
        right_panel_layout.addWidget(self.search_box)
        right_panel_layout.addWidget(self.note_area)

        note_area_layout = QVBoxLayout(self.note_area)

        self.main_panel_layout = QHBoxLayout(self.main_panel)
        self.main_panel_layout.addWidget(self.left_panel)
        self.main_panel_layout.addWidget(self.right_panel)

        self.setCentralWidget(self.main_panel)
