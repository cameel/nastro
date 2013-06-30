""" The UI widget that represents a single note """

from PyQt4.QtGui  import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QPushButton, QSizePolicy, QFont
from PyQt4.QtCore import SIGNAL
from .utils       import utc_to_localtime

class NoteWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._note = None

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

        self.connect(self._delete_button, SIGNAL('clicked()'),     lambda : self.emit(SIGNAL('requestDelete()')))
        self.connect(self._body_editor,   SIGNAL('textChanged()'), lambda : self.update_note_body())
        self.connect(self._tag_editor,    SIGNAL('textChanged(const QString &)'), lambda text: self.update_note_tags(text))
        self.connect(self._title_editor,  SIGNAL('textChanged(const QString &)'), lambda text: self.update_note_title(text))

    def update_note_body(self):
        if self._note != None:
            self._note.body = self._body_editor.toPlainText()

    def update_note_title(self, text):
        if self._note != None:
            self._note.title = text

    def update_note_tags(self, text):
        if self._note != None:
            self._note.tags = [tag.strip() for tag in text.split(',')]

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, value):
        self._note = value
        self._title_editor.setText(value.title)
        self._tag_editor.setText(', '.join(value.tags))
        self._body_editor.setPlainText(value.body)
        # TODO: Use system settings for date format?
        self._created_at_label.setText(utc_to_localtime(value.created_at).strftime("%Y-%m-%d %H:%M"))
        self._modified_at_label.setText(utc_to_localtime(value.modified_at).strftime("%Y-%m-%d %H:%M"))

