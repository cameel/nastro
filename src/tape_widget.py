""" The UI widget that represents a scrollable tape composed of notes """

from PyQt4.QtGui  import QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QPushButton
from PyQt4.QtCore import SIGNAL

from datetime import datetime

from .note_widget import NoteWidget
from .note        import Note

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

        self._add_note_button = QPushButton(self)
        self._add_note_button.setText("New note")

        self._button_layout.addWidget(self._add_note_button)
        self._button_layout.addStretch()

        self._main_layout.addWidget(self._search_box)
        self._main_layout.addLayout(self._button_layout)
        self._main_layout.addWidget(self._scroll_area)

        self.connect(self._add_note_button, SIGNAL('clicked()'), lambda : self.add_note())

        # NOTE: There are some caveats regarding setWidget() and show()
        # See QScrollArea.setWidget() docs.
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._note_panel)

    def add_note(self, note = None):
        if note != None:
            assert note not in self._note_widgets
        else:
            note = Note(
                title     = "Note {}".format(len(self._note_widgets) + 1),
                body      = "",
                tags      = [],
                timestamp = datetime.now()
            )

        # TODO: Get layout directly from widget
        note_widget      = NoteWidget(self._note_panel)
        note_widget.note = note
        self._note_layout.addWidget(note_widget)
        self._note_widgets.append(note_widget)

        self.connect(note_widget, SIGNAL('requestDelete()'), lambda : self.remove_note(note))

    def remove_note(self, note):
        # TODO: Removal by index may be more efficient for large lists
        note_widget = next(widget for widget in self._note_widgets if widget.note == note)

        if note_widget != None:
            note_widget.setParent(None)
            self._note_widgets.remove(note_widget)

        assert note not in self._note_widgets

    def clear(self):
        for note_widget in self._note_widgets:
            note_widget.setParent(None)

        self._note_widgets = []

    def dump_notes(self):
        notes = []
        for note_widget in self._note_widgets:
            notes.append(note_widget.note.to_dict())

        return notes

    def load_notes(self, notes):
        self.clear()

        try:
            for note in notes:
                self.add_note(note)
        except:
            self.clear()
            raise