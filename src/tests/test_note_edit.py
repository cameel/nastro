import unittest
import sys
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout

from .dummy_application import application
from ..note             import Note
from ..note_edit        import NoteEdit

class NoteEditTest(unittest.TestCase):
    def setUp(self):
        self.note_edit = NoteEdit()

        self.note = Note(
            body       = "B",
            tags       = ["C", "D"],
            created_at = datetime.utcnow(),
            id         = 666
        )

    def test_load_note_should_load_note_data_into_editor_widgets(self):
        assert self.note_edit._body_editor.toPlainText() != self.note.body
        assert self.note_edit._tag_editor.text()         != Note.join_tags(self.note.tags)
        assert self.note_edit._note_created_at           != self.note.created_at
        assert self.note_edit._note_modified_at          != self.note.modified_at
        assert self.note_edit._note_id                   != self.note.id

        self.note_edit.load_note(self.note)

        self.assertEqual(self.note_edit._body_editor.toPlainText(), self.note.body)
        self.assertEqual(self.note_edit._tag_editor.text(),         Note.join_tags(self.note.tags))
        self.assertEqual(self.note_edit._note_created_at,           self.note.created_at)
        self.assertEqual(self.note_edit._note_modified_at,          self.note.modified_at)
        self.assertEqual(self.note_edit._note_id,                   self.note.id)

    def test_loading_and_dumping_a_note_should_not_modify_it(self):
        dict_before = self.note.to_dict()
        assert Note.from_dict(dict_before).to_dict() == dict_before

        self.note_edit.load_note(self.note)
        note_after = self.note_edit.dump_note()

        self.assertNotEqual(note_after, self.note)
        self.assertEqual(note_after.to_dict(), dict_before)

    def test_load_note_should_not_store_reference_to_note_and_let_widget_modify_it_later(self):
        new_body  = "new body"
        new_tags  = ["new", "tag"]
        assert new_body  != self.note.body
        assert new_tags  != self.note.tags

        dict_before = self.note.to_dict()
        assert Note.from_dict(dict_before).to_dict() == dict_before

        self.note_edit.load_note(self.note)

        self.note_edit._body_editor.setPlainText(new_body)
        self.note_edit._tag_editor.setText(Note.join_tags(new_tags))

        note_after = self.note_edit.dump_note()

        self.assertEqual(self.note.to_dict(), dict_before)
        self.assertNotEqual(note_after.to_dict(), dict_before)

    def test_dump_note_should_create_a_note_with_data_from_editor_widgets(self):
        self.note_edit.load_note(self.note)
        dumped_note = self.note_edit.dump_note()

        self.assertEqual(dumped_note.to_dict(), self.note.to_dict())

    def test_writing_in_body_editor_should_update_note_body(self):
        new_text = "new text"
        self.note_edit.load_note(self.note)

        assert self.note.body != new_text
        assert self.note_edit._body_editor.toPlainText() == self.note.body

        self.note_edit._body_editor.setText(new_text)
        note_after = self.note_edit.dump_note()

        assert self.note_edit._body_editor.toPlainText() == new_text
        self.assertEqual(note_after.body, new_text)

    def test_writing_in_body_editor_should_update_modified_at_timestamp(self):
        new_text = "new text"
        self.note_edit.load_note(self.note)

        assert self.note.body != new_text
        assert self.note_edit._body_editor.toPlainText() == self.note.body

        self.note_edit._body_editor.setText(new_text)
        note_after = self.note_edit.dump_note()

        assert self.note_edit._body_editor.toPlainText() == new_text
        self.assertTrue(note_after.modified_at > self.note.modified_at)

    def test_writing_in_tag_editor_should_update_note_tags(self):
        new_tags = ["A", "B"]
        new_text = Note.join_tags(new_tags)
        self.note_edit.load_note(self.note)

        assert self.note.tags != new_tags
        assert self.note_edit._tag_editor.text() == Note.join_tags(self.note.tags)

        self.note_edit._tag_editor.setText(new_text)
        note_after = self.note_edit.dump_note()

        assert self.note_edit._tag_editor.text() == new_text
        self.assertEqual(note_after.tags, new_tags)

    def test_writing_in_tag_editor_should_update_modified_at_timestamp(self):
        new_tags = ["A", "B"]
        new_text = Note.join_tags(new_tags)
        self.note_edit.load_note(self.note)

        assert self.note.tags != new_tags
        assert self.note_edit._tag_editor.text() == Note.join_tags(self.note.tags)

        self.note_edit._tag_editor.setText(new_text)
        note_after = self.note_edit.dump_note()

        assert self.note_edit._tag_editor.text() == new_text
        self.assertTrue(note_after.modified_at > self.note.modified_at)

    def test_touch_should_update_modified_at_timestamp(self):
        self.note_edit.load_note(self.note)
        self.note_edit.touch()
        note_after = self.note_edit.dump_note()

        assert note_after != self.note
        self.assertTrue(note_after.modified_at > self.note.modified_at)
