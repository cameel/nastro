""" The UI widget that represents a single note """

from PyQt4.QtGui  import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QPushButton, QSizePolicy
from PyQt4.QtCore import SIGNAL

class NoteWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._note = None

        self._main_layout = QVBoxLayout(self)

        self._title_panel  = QWidget(self)
        self._title_layout = QHBoxLayout(self._title_panel)
        self._body_editor  = QTextEdit(self)
        self._body_editor.setMinimumSize(0, 250)
        self._body_editor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        self._main_layout.addWidget(self._title_panel)
        self._main_layout.addWidget(self._body_editor)

        self._timestamp_label = QLabel(self._title_panel)
        self._title_editor    = QLineEdit(self._title_panel)
        self._delete_button   = QPushButton(self._title_panel)
        self._title_layout.addWidget(self._timestamp_label)
        self._title_layout.addWidget(self._title_editor)
        self._title_layout.addWidget(self._delete_button)

        self._delete_button.setText('delete')

        self.connect(self._delete_button, SIGNAL('clicked()'), lambda : self.emit(SIGNAL('requestDelete()')))

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, value):
        self._note = value
        self._title_editor.setText(value.title)
        self._body_editor.setPlainText(value.body)
        # TODO: Use system settings for date format?
        self._timestamp_label.setText(value.timestamp.strftime("%Y-%m-%d %H:%M"))

