""" The UI widget that represents a single note """

from PyQt4.QtGui  import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit
from PyQt4.QtCore import SIGNAL

class NoteWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._note = None

        self._main_layout = QVBoxLayout(self)

        self._body_editor  = QTextEdit(self)

        self._main_layout.addWidget(self._title_panel)
        self._main_layout.addWidget(self._body_editor)

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, value):
        self._note = value
        self._body_editor.setPlainText(value.body)
