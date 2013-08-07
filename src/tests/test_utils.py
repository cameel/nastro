import unittest
from datetime import datetime

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPalette
from PyQt5.QtCore    import Qt

from .dummy_application import application
from ..utils            import set_widget_background_color

class UtilsTest(unittest.TestCase):
    def test_set_widget_background_color_should_change_background_color(self):
        widget = QWidget()
        assert widget.palette().color(widget.backgroundRole()) != Qt.red

        set_widget_background_color(widget, Qt.red)

        self.assertEqual(widget.palette().color(widget.backgroundRole()), Qt.red)
