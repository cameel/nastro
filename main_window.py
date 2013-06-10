""" The main UI component of the application. Controls the whole window """

from PyKDE4.kdeui import KMainWindow, KDatePicker
from PyQt4.QtGui  import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt4.QtCore import SIGNAL

import simplejson

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

        file_menu      = self.menuBar().addMenu("File")
        save_as_action = file_menu.addAction("&Save as...")
        file_menu.addSeparator()
        exit_action    = file_menu.addAction("&Exit")

        self.connect(exit_action,    SIGNAL('triggered()'), self.close)
        self.connect(save_as_action, SIGNAL('triggered()'), self.save_file)

        self.resize(1200, 800)
        self.setCentralWidget(self.main_panel)

    def save_file(self):
        file_name = QFileDialog.getSaveFileName(
            self,
            "Save as...",
            None,
            "JSON files (*.json)"
        )

        if file_name != '':
            notes = self.tape_widget.dump_notes()

            with open(file_name, 'w') as json_file:
                if __debug__:
                    json_file.write(simplejson.dumps(notes, indent = 4, sort_keys = True))
                else:
                    json_file.write(simplejson.dumps(notes))
