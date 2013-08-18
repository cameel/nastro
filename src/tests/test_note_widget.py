import unittest
import sys
from datetime import datetime

from .dummy_application import application
from ..utils            import localtime_to_utc
from ..note             import Note
from ..note_widget      import NoteWidget

class TestNoteWidget(unittest.TestCase):
    def setUp(self):
        self.note_widget = NoteWidget()

        self.note = Note(
            body        = "B",
            tags        = ["C", "D"],
            created_at  = datetime(2013, 7, 31, 12, 24, 15, 123456),
            modified_at = datetime(2012, 6, 30,  2, 25, 16, 654321)
        )

    def test_load_note_should_load_note_data_into_editor_widgets(self):
        assert self.note_widget._body_label.text() != self.note.body
        assert self.note_widget._tag_label.text()  != Note.join_tags(self.note.tags)
        assert NoteWidget.format_timestamp(self.note.created_at)  not in self.note_widget._timestamp_label.text()
        assert NoteWidget.format_timestamp(self.note.modified_at) not in self.note_widget._timestamp_label.text()

        self.note_widget.load_note(self.note)

        self.assertEqual(self.note_widget._body_label.text(), self.note.body)
        self.assertEqual(self.note_widget._tag_label.text(),  Note.join_tags(self.note.tags))
        self.assertIn(NoteWidget.format_timestamp(self.note.created_at),  self.note_widget._timestamp_label.text())
        self.assertIn(NoteWidget.format_timestamp(self.note.modified_at), self.note_widget._timestamp_label.text())

    def test_load_note_should_make_timestamp_label_show_only_one_timestamp_if_they_are_the_same(self):
        self.note.created_at == self.note.modified_at

        self.note_widget.load_note(self.note)

        self.assertEqual(self.note_widget._timestamp_label.text().count(NoteWidget.format_timestamp(self.note.created_at)), 1)

    def test_format_timestamp_should_convert_a_timestamp_into_a_readable_string_repesentation(self):
        timestamp = datetime(2000, 12, 31)

        self.assertEqual(NoteWidget.format_timestamp(localtime_to_utc(timestamp)), "2000-12-31 00:00")
