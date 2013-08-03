""" The UI widget that represents a single note """

from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QSizePolicy
from PyQt5.QtGui     import QFont, QFontMetrics
from PyQt5.QtCore    import QSize

from .note import Note

class AutoResizingTextEdit(QTextEdit):
    def line_count_to_widget_height(self, num_lines):
        # ASSUMPTION: The document uses only the default font

        assert num_lines >= 0

        widget_margins  = self.contentsMargins()
        document_margin = self.document().documentMargin()
        font_metrics    = QFontMetrics(self.document().defaultFont())

        # font_metrics.lineSpacing() is ignored because it seems to be already included in font_metrics.height()
        return (
            widget_margins.top()                      +
            document_margin                           +
            max(num_lines, 1) * font_metrics.height() +
            self.document().documentMargin()          +
            widget_margins.bottom()
        )

        return QSize(original_hint.width(), minimum_height_hint)

class NoteEdit(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._note_created_at  = datetime.utcnow()
        self._note_modified_at = datetime.utcnow()
        self._note_id          = None

        self._main_layout = QVBoxLayout(self)

        # Use Liberation Mono font if present. If not, TypeWriter hint
        # will make Qt select some other monospace font.
        monospace_font = QFont("Liberation Mono", 10, QFont.TypeWriter)

        timestamp_font = QFont()
        timestamp_font.setPointSize(7)

        self._tag_editor  = QLineEdit(self)
        self._body_editor = AutoResizingTextEdit(self)
        self._body_editor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        document = self._body_editor.document()
        document.setDefaultFont(monospace_font)

        self._main_layout.addWidget(self._body_editor)
        self._main_layout.addWidget(self._tag_editor)

        self._body_editor.textChanged.connect(self.touch)
        self._tag_editor.textChanged.connect(lambda text: self.touch())

    def load_note(self, note):
        self._body_editor.setPlainText(note.body)
        self._tag_editor.setText(Note.join_tags(note.tags))

        # NOTE: Set timestamps last because setText() calls trigger textChanged signals
        # that cause modified_at to be updated.
        self._note_created_at  = note.created_at
        self._note_modified_at = note.modified_at
        self._note_id          = note.id

    def dump_note(self):
        return Note(
            body        = self._body_editor.toPlainText(),
            tags        = Note.split_tags(self._tag_editor.text()),
            created_at  = self._note_created_at,
            modified_at = self._note_modified_at,
            id          = self._note_id
        )

    def touch(self):
        self._note_modified_at = datetime.utcnow()
