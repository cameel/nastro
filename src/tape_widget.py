""" The UI widget that represents a scrollable tape composed of notes """

from PyQt4.QtGui  import QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QPushButton, QStandardItem, QStandardItemModel, QListView
from PyQt4.QtCore import SIGNAL, Qt

from datetime import datetime

from .note_delegate import NoteDelegate
from .note          import Note

class TapeWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._main_layout    = QVBoxLayout(self)
        self._search_box     = QLineEdit(self)
        self._button_layout  = QHBoxLayout()
        self._note_list_view = QListView()

        self._add_note_button = QPushButton(self)
        self._add_note_button.setText("New note")

        self._button_layout.addWidget(self._add_note_button)
        self._button_layout.addStretch()

        self._main_layout.addWidget(self._search_box)
        self._main_layout.addLayout(self._button_layout)
        self._main_layout.addWidget(self._note_list_view)

        self._tape_model    = QStandardItemModel()
        self._note_delegate = NoteDelegate()

        self._note_list_view.setItemDelegate(self._note_delegate)
        self._note_list_view.setModel(self._tape_model)

        self.connect(self._add_note_button, SIGNAL('clicked()'),                   self.add_note)
        """
        self.connect(self._search_box,      SIGNAL('textEdited(const QString &)'), self.search_handler)
        """

    def note(self, index):
        assert 0 <= index < self._tape_model.rowCount()

        note = self._tape_model.item(index).data(Qt.EditRole)
        assert isinstance(note, Note)

        return note

    def note_count(self):
        return self._tape_model.rowCount()

    def notes(self):
        for i in range(self._tape_model.rowCount()):
            note = self._tape_model.item(i).data(Qt.EditRole)
            assert isinstance(note, Note)

            yield note

    def add_note(self, note = None):
        if note != None:
            assert self._find_note(note) == None
        else:
            note = Note(
                title       = "Note {}".format(self._tape_model.rowCount() + 1),
                body        = "",
                tags        = [],
                created_at  = datetime.utcnow()
            )

        root_item = self._tape_model.invisibleRootItem()
        item = QStandardItem()
        item.setData(note, Qt.EditRole)
        root_item.appendRow(item)

    def remove_note(self, note):
        # TODO: Removal by index may be more efficient for large lists
        note_position = self._find_note(note)
        if note_position != None:
            self._tape_model.takeRow(note_position)

    def _find_note(self, note_to_find):
        try:
            return next(i for (i, note) in enumerate(self.notes()) if note == note_to_find)
        except StopIteration:
            return None

    """
    def search_handler(self, text):
        mask = self.search(text)
        for i, note_matches in enumerate(mask):
            self._note_widgets[i].setVisible(note_matches)
    """

    def clear(self):
        self._tape_model.clear()

    def dump_notes(self):
        notes = []
        for note in self.notes():
            notes.append(note.to_dict())

        return notes

    def load_notes(self, notes):
        self.clear()

        try:
            for note in notes:
                self.add_note(note)
        except:
            self.clear()
            raise
