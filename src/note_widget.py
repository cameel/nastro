""" The UI widget that represents a single note """

from datetime import datetime

from PyQt4.QtGui  import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QFont, QPalette
from PyQt4.QtCore import SIGNAL, Qt

from .utils import utc_to_localtime
from .note  import Note

class NoteWidget(QFrame):
    def __init__(self, parent = None):
        super().__init__(parent)

        # Use Liberation Mono font if present. If not, TypeWriter hint
        # will make Qt select some other monospace font.
        monospace_font = QFont("Liberation Mono", 10, QFont.TypeWriter)

        bold_font = QFont()
        bold_font.setPointSize(14)
        bold_font.setWeight(QFont.Bold)

        tag_font = QFont()
        tag_font.setPointSize(8)

        timestamp_font = QFont()
        timestamp_font.setPointSize(7)

        self._main_layout  = QVBoxLayout(self)
        self._title_panel  = QWidget(self)
        self._title_layout = QHBoxLayout(self._title_panel)

        self._title_label       = QLabel(self._title_panel)
        self._tag_label         = QLabel(self)
        self._body_label        = QLabel(self)
        self._created_at_label  = QLabel(self._title_panel)
        self._modified_at_label = QLabel(self._title_panel)

        self._timestamp_layout = QVBoxLayout()
        self._timestamp_layout.addWidget(self._created_at_label)
        self._timestamp_layout.addWidget(self._modified_at_label)

        self._title_layout.addLayout(self._timestamp_layout)
        self._title_layout.addWidget(self._title_label)
        self._title_layout.addStretch()

        self._main_layout.addWidget(self._title_panel)
        self._main_layout.addWidget(self._body_label)
        self._main_layout.addWidget(self._tag_label)

        tag_palette = QPalette(self._tag_label.palette())
        tag_palette.setColor(self._tag_label.foregroundRole(), Qt.red)

        timestamp_palette = QPalette(self._created_at_label.palette())
        timestamp_palette.setColor(self._created_at_label.foregroundRole(), Qt.darkGray)

        self._title_label.setFont(bold_font)
        self._title_label.setTextFormat(Qt.PlainText)

        self._tag_label.setPalette(tag_palette)
        self._tag_label.setTextFormat(Qt.PlainText)
        self._tag_label.setFont(tag_font)

        self._body_label.setFont(monospace_font)
        self._body_label.setWordWrap(True)
        self._body_label.setTextFormat(Qt.PlainText)

        self._created_at_label.setFont(timestamp_font)
        self._created_at_label.setPalette(timestamp_palette)

        self._modified_at_label.setFont(timestamp_font)
        self._modified_at_label.setPalette(timestamp_palette)

        widget_palette = QPalette(self.palette())
        widget_palette.setColor(QPalette.Background, Qt.white)

        self.setAutoFillBackground(True)
        self.setPalette(widget_palette)
        self.setFrameStyle(QFrame.StyledPanel)

    def load_note(self, note):
        self._title_label.setText(note.title)
        self._body_label.setText(note.body)
        self._tag_label.setText(Note.join_tags(note.tags))
        self._created_at_label.setText(self.format_timestamp(note.created_at))
        self._modified_at_label.setText(self.format_timestamp(note.modified_at))

    @classmethod
    def format_timestamp(self, timestamp):
        assert timestamp != None

        # TODO: Use system settings for date format?
        return utc_to_localtime(timestamp).strftime("%Y-%m-%d %H:%M")
