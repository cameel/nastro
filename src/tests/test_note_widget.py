import unittest
import sys
from datetime import datetime

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QApplication

from ..utils       import localtime_to_utc
from ..note        import Note
from ..note_widget import NoteWidget

class NoteWidgetTest(unittest.TestCase):
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
        assert self.note_widget._title_editor.text()       != self.note.title
        assert self.note_widget._body_editor.toPlainText() != self.note.body
        assert self.note_widget._tag_editor.text()         != Note.join_tags(self.note.tags)
        assert self.note_widget._note_created_at           != self.note.created_at
        assert self.note_widget._note_modified_at          != self.note.modified_at

        self.note_widget.load_note(self.note)

        self.assertEqual(self.note_widget._title_editor.text(),       self.note.title)
        self.assertEqual(self.note_widget._body_editor.toPlainText(), self.note.body)
        self.assertEqual(self.note_widget._tag_editor.text(),         Note.join_tags(self.note.tags))
        self.assertEqual(self.note_widget._note_created_at,           self.note.created_at)
        self.assertEqual(self.note_widget._note_modified_at,          self.note.modified_at)

    def test_loading_and_dumping_a_note_should_not_modify_it(self):
        dict_before = self.note.to_dict()
        assert Note.from_dict(dict_before).to_dict() == dict_before

        self.note_widget.load_note(self.note)
        note_after = self.note_widget.dump_note()

        self.assertNotEqual(note_after, self.note)
        self.assertEqual(note_after.to_dict(), dict_before)

    def test_load_note_should_not_store_reference_to_note_and_let_widget_modify_it_later(self):
        new_body  = "new body"
        new_title = "new title"
        new_tags  = ["new", "tag"]
        assert new_body  != self.note.body
        assert new_title != self.note.title
        assert new_tags  != self.note.tags

        dict_before = self.note.to_dict()
        assert Note.from_dict(dict_before).to_dict() == dict_before

        self.note_widget.load_note(self.note)

        self.note_widget._body_editor.setPlainText(new_body)
        self.note_widget._title_editor.setText(new_title)
        self.note_widget._tag_editor.setText(Note.join_tags(new_tags))

        note_after = self.note_widget.dump_note()

        self.assertEqual(self.note.to_dict(), dict_before)
        self.assertNotEqual(note_after.to_dict(), dict_before)

    def test_dump_note_should_create_a_note_with_data_from_editor_widgets(self):
        self.note_widget.load_note(self.note)
        dumped_note = self.note_widget.dump_note()

        self.assertEqual(dumped_note.to_dict(), self.note.to_dict())

    def test_writing_in_body_editor_should_update_note_body(self):
        new_text = "new text"
        self.note_widget.load_note(self.note)

        assert self.note.body != new_text
        assert self.note_widget._body_editor.toPlainText() == self.note.body

        self.note_widget._body_editor.setText(new_text)
        note_after = self.note_widget.dump_note()

        assert self.note_widget._body_editor.toPlainText() == new_text
        self.assertEqual(note_after.body, new_text)

    def test_writing_in_body_editor_should_update_modified_at_timestamp(self):
        new_text = "new text"
        self.note_widget.load_note(self.note)

        assert self.note.body != new_text
        assert self.note_widget._body_editor.toPlainText() == self.note.body

        self.note_widget._body_editor.setText(new_text)
        note_after = self.note_widget.dump_note()

        assert self.note_widget._body_editor.toPlainText() == new_text
        self.assertTrue(note_after.modified_at > self.note.modified_at)

    def test_writing_in_title_editor_should_update_note_title(self):
        new_text = "new text"
        self.note_widget.load_note(self.note)

        assert self.note.title != new_text
        assert self.note_widget._title_editor.text() == self.note.title

        self.note_widget._title_editor.setText(new_text)
        note_after = self.note_widget.dump_note()

        assert self.note_widget._title_editor.text() == new_text
        self.assertEqual(note_after.title, new_text)

    def test_writing_in_title_editor_should_update_modified_at_timestamp(self):
        new_text = "new text"
        self.note_widget.load_note(self.note)

        assert self.note.title != new_text
        assert self.note_widget._title_editor.text() == self.note.title

        self.note_widget._title_editor.setText(new_text)
        note_after = self.note_widget.dump_note()

        assert self.note_widget._title_editor.text() == new_text
        self.assertTrue(note_after.modified_at > self.note.modified_at)

    def test_writing_in_tag_editor_should_update_note_tags(self):
        new_tags = ["A", "B"]
        new_text = Note.join_tags(new_tags)
        self.note_widget.load_note(self.note)

        assert self.note.tags != new_tags
        assert self.note_widget._tag_editor.text() == Note.join_tags(self.note.tags)

        self.note_widget._tag_editor.setText(new_text)
        note_after = self.note_widget.dump_note()

        assert self.note_widget._tag_editor.text() == new_text
        self.assertEqual(note_after.tags, new_tags)

    def test_writing_in_tag_editor_should_update_modified_at_timestamp(self):
        new_tags = ["A", "B"]
        new_text = Note.join_tags(new_tags)
        self.note_widget.load_note(self.note)

        assert self.note.tags != new_tags
        assert self.note_widget._tag_editor.text() == Note.join_tags(self.note.tags)

        self.note_widget._tag_editor.setText(new_text)
        note_after = self.note_widget.dump_note()

        assert self.note_widget._tag_editor.text() == new_text
        self.assertTrue(note_after.modified_at > self.note.modified_at)

    def test_touch_should_update_modified_at_timestamp(self):
        self.note_widget.load_note(self.note)
        self.note_widget.touch()
        note_after = self.note_widget.dump_note()

        assert note_after != self.note
        self.assertTrue(note_after.modified_at > self.note.modified_at)

    def test_format_timestamp_should_convert_a_timestamp_into_a_readable_string_repesentation(self):
        timestamp = datetime(2000, 12, 31)

        self.assertEqual(self.note_widget.format_timestamp(localtime_to_utc(timestamp)), "2000-12-31 00:00")

    def test_refresh_timestamps_should_update_timestamp_labels(self):
        self.note_widget._note_created_at  = datetime(2000, 12, 31)
        self.note_widget._note_modified_at = datetime(2000, 12, 31)
        assert self.note_widget._created_at_label.text()  != self.note_widget.format_timestamp(self.note_widget._note_created_at)
        assert self.note_widget._modified_at_label.text() != self.note_widget.format_timestamp(self.note_widget._note_modified_at)

        self.note_widget.refresh_timestamps()

        self.assertEqual(self.note_widget._created_at_label.text(),  self.note_widget.format_timestamp(self.note_widget._note_created_at))
        self.assertEqual(self.note_widget._modified_at_label.text(), self.note_widget.format_timestamp(self.note_widget._note_modified_at))
