""" The UI widget that represents a scrollable tape composed of notes """

from PyQt4.QtGui  import QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QPushButton, QStandardItem, QStandardItemModel, QListView
from PyQt4.QtCore import SIGNAL, Qt

from datetime import datetime

from .note_delegate import NoteDelegate
from .note          import Note

class TapeWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._note_widgets = []

        self._main_layout   = QVBoxLayout(self)
        self._search_box    = QLineEdit(self)
        self._scroll_area   = QScrollArea(self)
        self._note_panel    = QWidget()
        self._note_layout   = QVBoxLayout(self._note_panel)
        self._button_layout = QHBoxLayout()
        self._note_list_view = QListView()

        self._add_note_button = QPushButton(self)
        self._add_note_button.setText("New note")

        self._button_layout.addWidget(self._add_note_button)
        self._button_layout.addStretch()

        self._main_layout.addWidget(self._search_box)
        self._main_layout.addLayout(self._button_layout)
        self._main_layout.addWidget(self._scroll_area)
        self._main_layout.addWidget(self._note_list_view)

        self._tape_model    = QStandardItemModel()
        self._note_delegate = NoteDelegate()

        self._note_list_view.setItemDelegate(self._note_delegate)
        self._note_list_view.setModel(self._tape_model)

        self.connect(self._add_note_button, SIGNAL('clicked()'),                   self.add_note)
        """
        self.connect(self._search_box,      SIGNAL('textEdited(const QString &)'), self.search_handler)
        """

        # NOTE: There are some caveats regarding setWidget() and show()
        # See QScrollArea.setWidget() docs.
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._note_panel)

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

        # TODO: Get layout directly from widget
        note_widget      = NoteWidget(self._note_panel)
        note_widget.note = note
        self._note_layout.addWidget(note_widget)
        self._note_widgets.append(note_widget)

        self.connect(note_widget, SIGNAL('requestDelete()'), lambda : self.remove_note(note))
        root_item = self._tape_model.invisibleRootItem()
        item = QStandardItem()
        item.setData(note, Qt.EditRole)
        root_item.appendRow(item)

    def remove_note(self, note):
        # TODO: Removal by index may be more efficient for large lists
        try:
            note_widget = next(widget for widget in self._note_widgets if widget.note == note)
            note_widget.setParent(None)
            self._note_widgets.remove(note_widget)
        except StopIteration:
            pass

        assert note not in self._note_widgets
        note_position = self._find_note(note)
        if note_position != None:
            self._tape_model.takeRow(note_position)

    def _find_note(self, note_to_find):
        try:
            return next(i for (i, note) in enumerate(self.notes()) if note == note_to_find)
        except StopIteration:
            return None

    def search(self, text):
        def note_matches(lowercase_text, note):
            for text_component in [note.title] + note.tags + [note.body]:
                if text_component.lower().find(lowercase_text) != -1:
                    return True

            return False

        return [note_matches(text.lower(), note) for note in self.notes()]

    """
    def search_handler(self, text):
        mask = self.search(text)
        for i, note_matches in enumerate(mask):
            self._note_widgets[i].setVisible(note_matches)
    """

    def clear(self):
        for note_widget in self._note_widgets:
            note_widget.setParent(None)

        self._note_widgets = []
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
