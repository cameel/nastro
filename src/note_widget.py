""" The UI widget that represents a single note """

from datetime import datetime

from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui     import QFont, QPalette
from PyQt5.QtCore    import Qt

from .utils import utc_to_localtime
from .note  import Note

class NoteWidget(QFrame):
    def __init__(self, parent = None):
        super().__init__(parent)

        # Use Liberation Mono font if present. If not, TypeWriter hint
        # will make Qt select some other monospace font.
        monospace_font = QFont("Liberation Mono", 10, QFont.TypeWriter)

        tag_font = QFont()
        tag_font.setPointSize(8)

        timestamp_font = QFont()
        timestamp_font.setPointSize(7)

        self._main_layout = QVBoxLayout(self)
        self._tag_panel   = QWidget(self)
        self._tag_layout  = QHBoxLayout(self._tag_panel)

        self._tag_label         = QLabel(self)
        self._body_label        = QLabel(self)
        self._timestamp_label   = QLabel(self._tag_panel)

        self._tag_layout.addWidget(self._tag_label)
        self._tag_layout.addStretch()
        self._tag_layout.addWidget(self._timestamp_label)

        self._main_layout.addWidget(self._body_label)
        self._main_layout.addWidget(self._tag_panel)

        tag_palette = QPalette(self._tag_label.palette())
        tag_palette.setColor(self._tag_label.foregroundRole(), Qt.red)

        timestamp_palette = QPalette(self._timestamp_label.palette())
        timestamp_palette.setColor(self._timestamp_label.foregroundRole(), Qt.darkGray)

        self._tag_label.setPalette(tag_palette)
        self._tag_label.setTextFormat(Qt.PlainText)
        self._tag_label.setFont(tag_font)

        self._body_label.setFont(monospace_font)
        self._body_label.setWordWrap(True)
        self._body_label.setTextFormat(Qt.PlainText)

        self._timestamp_label.setFont(timestamp_font)
        self._timestamp_label.setPalette(timestamp_palette)

        widget_palette = QPalette(self.palette())
        widget_palette.setColor(QPalette.Background, Qt.white)

        self.setAutoFillBackground(True)
        self.setPalette(widget_palette)
        self.setFrameStyle(QFrame.StyledPanel)

    def load_note(self, note):
        self._body_label.setText(note.body)
        self._tag_label.setText(Note.join_tags(note.tags))

        if note.created_at != note.modified_at:
            self._timestamp_label.setText("{} (Modified: {})".format(
                self.format_timestamp(note.created_at),
                self.format_timestamp(note.modified_at)
            ))
        else:
            self._timestamp_label.setText(self.format_timestamp(note.created_at))

    @classmethod
    def format_timestamp(self, timestamp):
        assert timestamp != None

        # TODO: Use system settings for date format?
        return utc_to_localtime(timestamp).strftime("%Y-%m-%d %H:%M")
