""" The UI widget that represents a single note """

from datetime import datetime

from PyQt4.QtGui  import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QPushButton, QSizePolicy, QFont
from PyQt4.QtCore import SIGNAL

from .utils import utc_to_localtime
from .note  import Note

class NoteWidget(QWidget):
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

        self._title_panel  = QWidget(self)
        self._title_layout = QHBoxLayout(self._title_panel)
        self._tag_editor   = QLineEdit(self)
        self._body_editor  = QTextEdit(self)
        self._body_editor.setMinimumSize(0, 250)
        self._body_editor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self._body_editor.setCurrentFont(monospace_font)

        self._main_layout.addWidget(self._title_panel)
        self._main_layout.addWidget(self._tag_editor)
        self._main_layout.addWidget(self._body_editor)
        self._main_layout.addWidget(self._tag_editor)

        self._created_at_label  = QLabel(self._title_panel)
        self._modified_at_label = QLabel(self._title_panel)
        self._created_at_label.setFont(timestamp_font)
        self._modified_at_label.setFont(timestamp_font)

        self._timestamp_layout = QVBoxLayout()
        self._timestamp_layout.addWidget(self._created_at_label)
        self._timestamp_layout.addWidget(self._modified_at_label)

        self._title_editor     = QLineEdit(self._title_panel)
        self._delete_button    = QPushButton(self._title_panel)
        self._title_layout.addLayout(self._timestamp_layout)
        self._title_layout.addWidget(self._title_editor)
        self._title_layout.addWidget(self._delete_button)

        self._delete_button.setText('delete')

        self.connect(self._delete_button, SIGNAL('clicked()'),                    lambda:      self.emit(SIGNAL('requestDelete()')))
        self.connect(self._body_editor,   SIGNAL('textChanged()'),                lambda:      self.touch())
        self.connect(self._tag_editor,    SIGNAL('textChanged(const QString &)'), lambda text: self.touch())
        self.connect(self._title_editor,  SIGNAL('textChanged(const QString &)'), lambda text: self.touch())

    def load_note(self, note):
        self._title_editor.setText(note.title)
        self._body_editor.setPlainText(note.body)
        self._tag_editor.setText(Note.join_tags(note.tags))
        self._note_created_at  = note.created_at
        self._note_modified_at = note.modified_at

        # NOTE: Set timestamps last because setText() calls trigger textChanged signals
        # that cause modified_at to be updated.
        self.refresh_timestamps()

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

    def _format_timestamp(self, timestamp):
        assert timestamp != None

        # TODO: Use system settings for date format?
        return utc_to_localtime(timestamp).strftime("%Y-%m-%d %H:%M")

    def refresh_timestamps(self):
        self._created_at_label.setText(self._format_timestamp(self._note_created_at))
        self._modified_at_label.setText(self._format_timestamp(self._note_modified_at))
