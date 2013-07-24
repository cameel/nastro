import unittest
import sys
from datetime import datetime

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QApplication

from ..main_window import MainWindow
from ..tape_widget import TapeWidget
from ..note        import Note

class TapeWidgetTest(unittest.TestCase):
    def setUp(self):
        self.application = QApplication(sys.argv)
        self.window      = MainWindow()

    def tearDown(self):
        # FIXME: Python crashes without this. Probably unittest does not destroy the old instance of the
        # class before creating a new one and PyQt does not like having two instances of QApplication?
        self.application = None

    def test_replace_tape_widget_should_destroy_old_tape_and_put_a_new_one_on_the_panel(self):
        old_tape_widget = self.window.tape_widget

        assert isinstance(old_tape_widget, TapeWidget)
        assert self.window.centralWidget() == old_tape_widget

        old_tape_widget.add_note()
        old_tape_widget.add_note()
        old_note1 = old_tape_widget.note(0)
        old_note2 = old_tape_widget.note(1)

        new_note = Note(
            title      = "X",
            body       = "Y",
            tags       = ["Z"],
            created_at = datetime.utcnow()
        )

        self.window._replace_tape_widget([new_note])

        self.assertTrue(isinstance(self.window.tape_widget, TapeWidget))
        self.assertNotEqual(self.window.tape_widget, old_tape_widget)
        self.assertEqual(self.window.tape_widget.note_count(), 1)
        self.assertEqual(self.window.tape_widget.note(0), new_note)
        self.assertTrue(self.window.centralWidget() == self.window.tape_widget)
