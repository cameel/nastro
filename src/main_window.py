""" The main UI component of the application. Controls the whole window """

from PyKDE4.kdeui import KMainWindow, KDatePicker
from PyQt4.QtGui  import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
from PyQt4.QtCore import SIGNAL

import simplejson

from .tape_widget            import TapeWidget
from .note                   import Note
from .opera.hotlist.importer import import_opera_notes

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
        open_action    = file_menu.addAction("&Open...")
        save_as_action = file_menu.addAction("&Save as...")
        file_menu.addSeparator()
        import_menu    = file_menu.addMenu("&Import")
        file_menu.addSeparator()
        exit_action    = file_menu.addAction("&Exit")

        import_opera_notes_action = import_menu.addAction("&Opera Notes...")

        self.connect(exit_action,    SIGNAL('triggered()'), self.close)
        self.connect(open_action,    SIGNAL('triggered()'), self.load_file)
        self.connect(save_as_action, SIGNAL('triggered()'), self.save_file)

        self.connect(import_opera_notes_action, SIGNAL('triggered()'), self.import_opera_notes)

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

    def load_file(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open...",
            None,
            "JSON files (*.json)"
        )

        if file_name != '':
            with open(file_name, 'r') as json_file:
                try:
                    raw_notes = simplejson.loads(json_file.read())
                except simplejson.scanner.JSONDecodeError:
                    QMessageBox.warning(self, "File error", "Failed to decode JSON data. The file has different format or is damaged.")
                    return

            notes = []
            for note_dict in raw_notes:
                notes.append(Note.from_dict(note_dict))

            self.tape_widget.load_notes(notes)

    def import_opera_notes(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open Opera Notes...",
            '~/.opera',
            "Opera Hotlist (*.adr)"
        )

        if file_name != '':
            with open(file_name, 'r') as note_file:
                notes = import_opera_notes(note_file)
            self.tape_widget.load_notes(notes)
            QMessageBox.information(self, "Success", "Successfully imported {} notes".format(len(notes)))
