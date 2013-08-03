""" The UI widget that represents a single note """

from datetime import datetime
from math     import ceil

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QSizePolicy
from PyQt5.QtGui     import QFont, QFontMetrics
from PyQt5.QtCore    import QSize

from .note import Note

class AutoResizingTextEdit(QTextEdit):
    MIN_LINES = 3

    def sizeHint(self):
        margins          = self.contentsMargins()
        document_height  = int(ceil(self.document().size().height()))
        preferred_height = margins.top() + document_height + margins.bottom()

        # We return current width because any width is acceptable. Different widths just yield
        # different heights. It's convenient because QTextDocument does not provide any method for
        # checking what the height would be at arbitrary width - it would be hard to find height
        # for width other than the current one.
        return QSize(self.width(), preferred_height)

    def minimumSizeHint(self):
        return QSize(
            super().minimumSizeHint().width(),
            int(ceil(self.line_count_to_widget_height(self.MIN_LINES)))
        )

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

        self.max_preferred_height = None

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
        self._body_editor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        document = self._body_editor.document()
        document.setDefaultFont(monospace_font)

        self._main_layout.addWidget(self._body_editor)
        self._main_layout.addWidget(self._tag_editor)

        self._body_editor.textChanged.connect(self._body_text_changed_handler)
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

    def _body_text_changed_handler(self):
        self.touch()

        self.adjustSize()

    def sizeHint(self):
        # NOTE: Reimplementing this method would not be necessary if the inherited sizeHint()
        # refreshed its value when sizeHint() of one of its children (managed by the layout) changed.
        # Instead it always returns the number based on minimumSizeHint()s of the children and
        # only checks the result of that method once so even if it changes, sizeHint() does not change.

        # SYNC: If you add more controls you need to update this assertion and include them in size calculations below
        assert self.layout().count() == 2

        original_hint  = super().sizeHint()
        layout         = self.layout()
        layout_margins = layout.contentsMargins()

        base_height = (
            layout_margins.top()                  +
            self._tag_editor.sizeHint().height()  +
            layout.spacing()                      +
            self._body_editor.sizeHint().height() +
            layout_margins.bottom()
        )

        preferred_height = min(self.max_preferred_height, base_height) if self.max_preferred_height != None else base_height

        # Even though we ignore self.minimumSize() here, QWidget won't let itself be resized below
        # that size no matter what sizeHint() says.
        return QSize(original_hint.width(), preferred_height)
