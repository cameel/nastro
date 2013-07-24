""" The main UI component of the application. Controls the whole window """

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QSplitter

import simplejson

from .tape_widget            import TapeWidget
from .note                   import Note
from .opera.hotlist.importer import import_opera_notes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tape_widget = TapeWidget(self)

        file_menu      = self.menuBar().addMenu("File")
        new_action     = file_menu.addAction("&New")
        open_action    = file_menu.addAction("&Open...")
        save_as_action = file_menu.addAction("&Save as...")
        file_menu.addSeparator()
        import_menu    = file_menu.addMenu("&Import")
        file_menu.addSeparator()
        exit_action    = file_menu.addAction("&Exit")

        import_opera_notes_action = import_menu.addAction("&Opera Notes...")

        new_action.triggered.connect(self.new_handler)
        open_action.triggered.connect(self.open_handler)
        save_as_action.triggered.connect(self.save_as_handler)
        exit_action.triggered.connect(self.close)

        import_opera_notes_action.triggered.connect(self.import_opera_notes_handler)

        self.resize(800, 800)
        self.setCentralWidget(self.tape_widget)

    def new_handler(self):
        self._replace_tape_widget([])

    def save_as_handler(self):
        file_name = QFileDialog.getSaveFileName(
            self,
            "Save as...",
            None,
            "JSON files (*.json)"
        )

        if file_name[0] != '':
            self.save_note_file_as(file_name[0])

    def open_handler(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open...",
            None,
            "JSON files (*.json)"
        )

        if file_name[0] != '':
            self.open_note_file(file_name[0])

    def import_opera_notes_handler(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open Opera Notes...",
            '~/.opera',
            "Opera Hotlist (*.adr)"
        )

        if file_name[0] != '':
            num_notes = self.import_opera_notes(file_name[0])
            QMessageBox.information(self, "Success", "Successfully imported {} notes".format(num_notes))

    def save_note_file_as(self, file_name):
        notes = self.tape_widget.dump_notes()

        with open(file_name, 'w') as json_file:
            if __debug__:
                json_file.write(simplejson.dumps(notes, indent = 4, sort_keys = True))
            else:
                json_file.write(simplejson.dumps(notes))

    def open_note_file(self, file_name):
        with open(file_name, 'r') as json_file:
            try:
                raw_notes = simplejson.loads(json_file.read())
            except simplejson.scanner.JSONDecodeError:
                QMessageBox.warning(self, "File error", "Failed to decode JSON data. The file has different format or is damaged.")
                return

        notes = []
        for note_dict in raw_notes:
            notes.append(Note.from_dict(note_dict))

        self._replace_tape_widget(notes)

    def import_opera_notes(self, file_name):
        with open(file_name, 'r') as note_file:
            notes = import_opera_notes(note_file)
        self._replace_tape_widget(notes)

        return len(notes)

    def _replace_tape_widget(self, notes):
        new_tape_widget = TapeWidget()
        new_tape_widget.load_notes(notes)

        self.tape_widget.setParent(None)

        self.tape_widget = new_tape_widget
        self.setCentralWidget(new_tape_widget)
