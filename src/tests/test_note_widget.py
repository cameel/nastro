import unittest
import sys
from datetime import datetime

from PyQt5.QtTest    import QTest

from .dummy_application import application
from ..utils            import localtime_to_utc
from ..note             import Note
from ..note_widget      import NoteWidget

class TestNoteWidget(unittest.TestCase):
    def setUp(self):
        self.note_widget = NoteWidget()

        self.note = Note(
            body       = "B",
            tags       = ["C", "D"],
            created_at = datetime.utcnow()
        )

    def test_load_note_should_load_note_data_into_editor_widgets(self):
        assert self.note_widget._body_label.text()        != self.note.body
        assert self.note_widget._tag_label.text()         != Note.join_tags(self.note.tags)
        assert self.note_widget._created_at_label.text()  != NoteWidget.format_timestamp(self.note.created_at)
        assert self.note_widget._modified_at_label.text() != NoteWidget.format_timestamp(self.note.modified_at)

        self.note_widget.load_note(self.note)

        self.assertEqual(self.note_widget._body_label.text(),        self.note.body)
        self.assertEqual(self.note_widget._tag_label.text(),         Note.join_tags(self.note.tags))
        self.assertEqual(self.note_widget._created_at_label.text(),  NoteWidget.format_timestamp(self.note.created_at))
        self.assertEqual(self.note_widget._modified_at_label.text(), NoteWidget.format_timestamp(self.note.modified_at))

    def test_format_timestamp_should_convert_a_timestamp_into_a_readable_string_repesentation(self):
        timestamp = datetime(2000, 12, 31)

        self.assertEqual(NoteWidget.format_timestamp(localtime_to_utc(timestamp)), "2000-12-31 00:00")
