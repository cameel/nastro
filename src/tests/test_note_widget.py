import unittest
import sys
from datetime import datetime

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QApplication

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

    def test_inserting_a_note_should_not_modify_it(self):
        dict_before = self.note.to_dict()
        assert Note.from_dict(dict_before).to_dict() == dict_before

        self.note_widget.note = self.note

        self.assertEqual(self.note_widget.note.to_dict(), dict_before)

    def test_writing_in_body_editor_should_update_note_body(self):
        new_text              = "new text"
        self.note_widget.note = self.note

        assert self.note.body != new_text
        assert self.note_widget._body_editor.toPlainText() == self.note.body

        self.note_widget._body_editor.setText(new_text)

        assert self.note_widget._body_editor.toPlainText() == new_text
        self.assertEqual(self.note_widget.note.body, new_text)

    def test_writing_in_body_editor_should_update_modified_at_timestamp(self):
        # NOTE: Insert note first save values later - we're only interested in changes made after the note is inserted.
        self.note_widget.note = self.note

        new_text           = "new text"
        modified_at_before = self.note.modified_at

        assert self.note.body != new_text
        assert self.note_widget._body_editor.toPlainText() == self.note.body

        self.note_widget._body_editor.setText(new_text)

        assert self.note_widget._body_editor.toPlainText() == new_text
        self.assertTrue(self.note_widget.note.modified_at > modified_at_before)

    def test_writing_in_body_editor_should_not_update_modified_at_timestamp_if_new_content_is_identical(self):
        # NOTE: Insert note first save values later - we're only interested in changes made after the note is inserted.
        self.note_widget.note = self.note

        body_before        = self.note.body
        modified_at_before = self.note.modified_at

        assert self.note_widget._body_editor.toPlainText() == self.note.body

        self.note_widget._body_editor.setText(body_before)

        assert self.note_widget._body_editor.toPlainText() == body_before
        self.assertTrue(self.note_widget.note.modified_at == modified_at_before)

    def test_writing_in_title_editor_should_update_note_title(self):
        new_text              = "new text"
        self.note_widget.note = self.note

        assert self.note.title != new_text
        assert self.note_widget._title_editor.text() == self.note.title

        self.note_widget._title_editor.setText(new_text)

        assert self.note_widget._title_editor.text() == new_text
        self.assertEqual(self.note_widget.note.title, new_text)

    def test_writing_in_title_editor_should_update_modified_at_timestamp(self):
        # NOTE: Insert note first save values later - we're only interested in changes made after the note is inserted.
        self.note_widget.note = self.note

        new_text           = "new text"
        modified_at_before = self.note.modified_at

        assert self.note.title != new_text
        assert self.note_widget._title_editor.text() == self.note.title

        self.note_widget._title_editor.setText(new_text)

        assert self.note_widget._title_editor.text() == new_text
        self.assertTrue(self.note_widget.note.modified_at > modified_at_before)

    def test_writing_in_title_editor_should_not_update_modified_at_timestamp_if_new_content_is_identical(self):
        # NOTE: Insert note first save values later - we're only interested in changes made after the note is inserted.
        self.note_widget.note = self.note

        title_before       = self.note.title
        modified_at_before = self.note.modified_at

        assert self.note_widget._title_editor.text() == self.note.title

        self.note_widget._title_editor.setText(title_before)

        assert self.note_widget._title_editor.text() == title_before
        self.assertTrue(self.note_widget.note.modified_at == modified_at_before)

    def test_writing_in_tag_editor_should_update_note_tags(self):
        new_tags              = ["A", "B"]
        new_text              = ', '.join(new_tags)
        self.note_widget.note = self.note

        assert self.note.tags != new_tags
        assert self.note_widget._tag_editor.text() == ', '.join(self.note.tags)

        self.note_widget._tag_editor.setText(new_text)

        assert self.note_widget._tag_editor.text() == new_text
        self.assertEqual(self.note_widget.note.tags, new_tags)

    def test_writing_in_tag_editor_should_update_modified_at_timestamp(self):
        # NOTE: Insert note first save values later - we're only interested in changes made after the note is inserted.
        self.note_widget.note = self.note

        new_tags           = ["A", "B"]
        new_text           = ', '.join(new_tags)
        modified_at_before = self.note.modified_at

        assert self.note.tags != new_tags
        assert self.note_widget._tag_editor.text() == ', '.join(self.note.tags)

        self.note_widget._tag_editor.setText(new_text)

        assert self.note_widget._tag_editor.text() == new_text
        self.assertTrue(self.note_widget.note.modified_at > modified_at_before)

    def test_writing_in_tag_editor_should_not_update_modified_at_timestamp_if_new_content_is_identical(self):
        # NOTE: Insert note first save values later - we're only interested in changes made after the note is inserted.
        self.note_widget.note = self.note

        tags_before        = self.note.tags
        text_before        = ', '.join(tags_before)
        modified_at_before = self.note.modified_at

        assert self.note_widget._tag_editor.text() == text_before

        self.note_widget._tag_editor.setText(text_before)

        assert self.note_widget._tag_editor.text() == text_before
        self.assertTrue(self.note_widget.note.modified_at == modified_at_before)
