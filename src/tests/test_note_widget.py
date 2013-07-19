import unittest
import sys
from datetime import datetime

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QApplication

from ..note        import Note
from ..note_widget import NoteWidget
from ..note_edit   import NoteEdit

class TestNoteWidget(unittest.TestCase):
    def setUp(self):
        self.application = QApplication(sys.argv)
        self.note_widget = NoteWidget()

        self.note = Note(
            title      = "A",
            body       = "B",
            tags       = ["C", "D"],
            created_at = datetime.utcnow()
        )

    def tearDown(self):
        self.application = None

    def test_load_note_should_load_note_data_into_editor_widgets(self):
        assert self.note_widget._title_label.text() != self.note.title
        assert self.note_widget._body_label.text()  != self.note.body
        assert self.note_widget._tag_label.text()   != Note.join_tags(self.note.tags)
        assert self.note_widget._created_at_label   != NoteEdit.format_timestamp(self.note.created_at)
        assert self.note_widget._modified_at_label  != NoteEdit.format_timestamp(self.note.modified_at)

        self.note_widget.load_note(self.note)

        self.assertEqual(self.note_widget._title_label.text(),       self.note.title)
        self.assertEqual(self.note_widget._body_label.text(),        self.note.body)
        self.assertEqual(self.note_widget._tag_label.text(),         Note.join_tags(self.note.tags))
        self.assertEqual(self.note_widget._created_at_label.text(),  NoteEdit.format_timestamp(self.note.created_at))
        self.assertEqual(self.note_widget._modified_at_label.text(), NoteEdit.format_timestamp(self.note.modified_at))
