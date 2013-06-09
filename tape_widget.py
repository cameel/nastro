""" The UI widget that represents a scrollable tape composed of notes """

from PyQt4.QtGui  import QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget
from PyQt4.QtCore import SIGNAL

from datetime import datetime

from note_widget import NoteWidget
from note        import Note

class TapeWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._note_widgets = []

        self._main_layout   = QVBoxLayout(self)
        self._search_box    = QLineEdit(self)
        self._scroll_area   = QScrollArea(self)
        self._note_panel    = QWidget()
        self._note_layout   = QVBoxLayout(self._note_panel)

        self._main_layout.addWidget(self._search_box)
        self._main_layout.addWidget(self._scroll_area)

        # NOTE: There are some caveats regarding setWidget() and show()
        # See QScrollArea.setWidget() docs.
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._note_panel)
