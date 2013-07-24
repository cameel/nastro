import unittest
import sys
from datetime import datetime

from PyQt5.QtTest    import QTest
from PyQt5.QtCore    import Qt

from .dummy_application import application
from ..main_window      import MainWindow
from ..tape_widget      import TapeWidget
from ..note             import Note

class MainWindowTest(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    def test_replace_tape_widget_should_destroy_old_tape_and_put_a_new_one_on_the_panel(self):
        old_tape_widget = self.window.tape_widget

        assert isinstance(old_tape_widget, TapeWidget)
        assert self.window.centralWidget() == old_tape_widget

        old_tape_widget.add_note()
        old_tape_widget.add_note()
        old_note1 = old_tape_widget.model().item(0).data(Qt.EditRole)
        old_note2 = old_tape_widget.model().item(1).data(Qt.EditRole)

        new_note = Note(
            title      = "X",
            body       = "Y",
            tags       = ["Z"],
            created_at = datetime.utcnow()
        )

        self.window._replace_tape_widget([new_note])

        self.assertTrue(isinstance(self.window.tape_widget, TapeWidget))
        self.assertNotEqual(self.window.tape_widget, old_tape_widget)
        self.assertEqual(len(list(self.window.tape_widget.notes())), 1)
        self.assertEqual(self.window.tape_widget.model().item(0).data(Qt.EditRole), new_note)
        self.assertTrue(self.window.centralWidget() == self.window.tape_widget)

    def test_new_handler_should_create_new_empty_tape(self):
        note = Note(
            title      = "X",
            body       = "Y",
            tags       = ["Z"],
            created_at = datetime.utcnow()
        )

        self.window.tape_widget.add_note(note)
        assert len(list(self.window.tape_widget.notes())) == 1

        self.window.tape_widget.set_filter("test")

        self.window.new_handler()

        self.assertEqual(len(list(self.window.tape_widget.notes())), 0)
        self.assertEqual(self.window.tape_widget.get_filter(), '')
