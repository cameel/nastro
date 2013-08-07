import unittest
import sys
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem
from PyQt5.QtGui     import QStandardItemModel, QStandardItem, QPixmap, QPainter
from PyQt5.QtCore    import Qt, QRect

from .dummy_application   import application
from ..note               import Note
from ..note_edit          import NoteEdit
from ..note_widget        import NoteWidget
from ..note_delegate      import NoteDelegate
from ..note_model_helpers import item_to_note, set_item_note

class NoteDelegateTest(unittest.TestCase):
    def setUp(self):
        self.note_delegate = NoteDelegate()
        self.model         = QStandardItemModel()

        self.note = Note(
            body       = "B",
            tags       = ["C", "D"],
            created_at = datetime.utcnow()
        )

        root_item = self.model.invisibleRootItem()
        self.item = QStandardItem()
        set_item_note(self.item, self.note)
        root_item.appendRow(self.item)

        self.parent      = QWidget()
        self.option      = QStyleOptionViewItem()
        self.option.rect = self.parent.geometry()

    def test_createEditor_should_create_note_edit(self):
        editor_container = self.note_delegate.createEditor(None, self.option, self.item.index())

        self.assertIsInstance(editor_container,          NoteDelegate.NoteEditContainer)
        self.assertIsInstance(editor_container.editor(), NoteEdit)

    def test_setEditorData_should_copy_data_from_note_to_editor(self):
        editor_container = self.note_delegate.createEditor(self.parent, self.option, self.item.index())
        assert editor_container.editor().dump_note().to_dict() != self.note.to_dict()

        self.note_delegate.setEditorData(editor_container, self.item.index())

        self.assertEqual(editor_container.editor().dump_note().to_dict(), self.note.to_dict())

    def test_setModelData_should_copy_data_from_editor_to_note(self):
        assert isinstance(item_to_note(self.item), Note)
        assert item_to_note(self.item).to_dict() == self.note.to_dict()

        new_note = Note(
            body       = "Y",
            tags       = ["W", "Z"],
            created_at = datetime.utcnow()
        )
        assert new_note.to_dict() != self.note.to_dict()

        editor_container = self.note_delegate.createEditor(self.parent, self.option, self.item.index())
        editor_container.editor().load_note(new_note)

        self.note_delegate.setModelData(editor_container, self.model, self.item.index())
        new_item_value = item_to_note(self.item)

        self.assertTrue(isinstance(new_item_value, Note))
        self.assertNotEqual(new_item_value, self.note)
        self.assertNotEqual(new_item_value, new_note)
        self.assertEqual(new_item_value.to_dict(), new_note.to_dict())

    def test_updateEditorGeometry_should_change_editor_size_and_position(self):
        self.option.rect = QRect(11, 22, 33, 44)
        expected_rect    = QRect(11, 22, 33, self.parent.height() - 22)
        editor_container = self.note_delegate.createEditor(self.parent, self.option, self.item.index())
        editor_container.editor().load_note(self.note)

        self.note_delegate.updateEditorGeometry(editor_container, self.option, self.item.index())

        self.assertEqual(editor_container.geometry(), expected_rect)

    def test_sizeHint_should_return_the_height_of_a_standard_note_widget(self):
        note_widget = NoteWidget()
        note_widget.load_note(self.note)

        size_hint = self.note_delegate.sizeHint(self.option, self.item.index())

        # NOTE: Preferred height is be the same in an empty and non-empty widget.
        # Preferred width may change depending on the content.
        self.assertEqual(size_hint.height(), note_widget.sizeHint().height())
