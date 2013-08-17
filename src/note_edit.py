""" The UI widget that represents a single note """

from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QSizePolicy
from PyQt5.QtGui     import QFont

from .note import Note

class NoteEdit(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._note_created_at  = datetime.utcnow()
        self._note_modified_at = datetime.utcnow()

        self._main_layout = QVBoxLayout(self)

        # Use Liberation Mono font if present. If not, TypeWriter hint
        # will make Qt select some other monospace font.
        monospace_font = QFont("Liberation Mono", 10, QFont.TypeWriter)

        timestamp_font = QFont()
        timestamp_font.setPointSize(7)

        self._title_editor = QLineEdit(self)
        self._tag_editor   = QLineEdit(self)
        self._body_editor  = QTextEdit(self)
        self._body_editor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self._body_editor.setCurrentFont(monospace_font)

        self._main_layout.addWidget(self._title_editor)
        self._main_layout.addWidget(self._body_editor)
        self._main_layout.addWidget(self._tag_editor)

        self._body_editor.textChanged.connect(self.touch)
        self._tag_editor.textChanged.connect(lambda text: self.touch())
        self._title_editor.textChanged.connect(lambda text: self.touch())

    def load_note(self, note):
        self._title_editor.setText(note.title)
        self._body_editor.setPlainText(note.body)
        self._tag_editor.setText(Note.join_tags(note.tags))

        # NOTE: Set timestamps last because setText() calls trigger textChanged signals
        # that cause modified_at to be updated.
        self._note_created_at  = note.created_at
        self._note_modified_at = note.modified_at

    def dump_note(self):
        return Note(
            title       = self._title_editor.text(),
            body        = self._body_editor.toPlainText(),
            tags        = Note.split_tags(self._tag_editor.text()),
            created_at  = self._note_created_at,
            modified_at = self._note_modified_at
        )

    def touch(self):
        self._note_modified_at = datetime.utcnow()
