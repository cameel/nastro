""" The main UI component of the application. Controls the whole window """

from PyKDE4.kdeui import KMainWindow, KDatePicker
from PyQt4.QtGui  import QWidget, QVBoxLayout, QHBoxLayout

from tape_widget import TapeWidget

class MainWindow(KMainWindow):
    def __init__(self):
        super().__init__()

        self.main_panel        = QWidget()
        self.left_panel        = QWidget(self.main_panel)
        self.date_picker       = KDatePicker(self.left_panel)
        self.left_panel_layout = QVBoxLayout(self.left_panel)
        self.left_panel_layout.addWidget(self.date_picker)
        self.left_panel_layout.addStretch()

        self.tape_widget = TapeWidget(self.main_panel)

        self.main_panel_layout = QHBoxLayout(self.main_panel)
        self.main_panel_layout.addWidget(self.left_panel)
        self.main_panel_layout.addWidget(self.tape_widget)

        self.resize(1200, 800)
        self.setCentralWidget(self.main_panel)
