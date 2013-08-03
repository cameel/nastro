""" The UI widget that represents a single note """

from datetime import datetime
from math     import ceil

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QSizePolicy
from PyQt5.QtGui     import QFont, QFontMetrics
from PyQt5.QtCore    import QSize

from .note import Note

class AutoResizingTextEdit(QTextEdit):
    MIN_LINES = 3

    def __init__(self, parent = None):
        super().__init__(parent)

        # This seems to have no effect. I have expected that it will cause self.hasHeightForWidth()
        # to start returning True, but it hasn't - that's why I hardcoded it to True there anyway.
        # I still set it to True in size policy just in case - for consistency.
        size_policy = self.sizePolicy()
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        margins = self.contentsMargins()

        if width >= margins.left() + margins.right():
            document_width = width - margins.left() - margins.right()
        else:
            # If specified width can't even fit the margin, there's no space left for the document
            document_width = 0

        # Cloning the whole document only to check its size at different width seems wasteful
        # but apparently it's the only and preferred way to do this in Qt >= 4. QTextDocument does not
        # provide any means to get height for specified width (as some QWidget subclasses do).
        # Neither does QTextEdit. In Qt3 Q3TextEdit had working implementation of heightForWidth()
        # but it was allegedly just a hack and was removed.
        #
        # The performance probably won't be a problem here because the application is meant to
        # work with a lot of small notes rather than few big ones. And there's usually only one
        # editor that needs to be dynamically resized - the one having focus.
        document = self.document().clone()
        document.setTextWidth(document_width)

        return margins.top() + document.size().height() + margins.bottom()

    def sizeHint(self):
        original_hint = super().sizeHint()
        return QSize(original_hint.width(), self.heightForWidth(original_hint.width()))

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
