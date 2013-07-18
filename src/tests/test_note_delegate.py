import unittest
import sys
from datetime import datetime

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QApplication, QStandardItemModel, QStyleOptionViewItem, QStandardItem, QPainter, QPixmap
from PyQt4.QtCore import Qt, QRect

from ..note          import Note
from ..note_widget   import NoteWidget
from ..note_delegate import NoteDelegate

class NoteDelegateTest(unittest.TestCase):
    def setUp(self):
        self.application   = QApplication(sys.argv)
        self.note_delegate = NoteDelegate()
        self.model         = QStandardItemModel()

        self.note = Note(
            title      = "A",
            body       = "B",
            tags       = ["C", "D"],
            created_at = datetime.utcnow()
        )

        root_item = self.model.invisibleRootItem()
        self.item = QStandardItem()
        self.item.setData(self.note, Qt.EditRole)
        root_item.appendRow(self.item)

        self.option = QStyleOptionViewItem()

    def tearDown(self):
        self.application = None

    def test_createEditor_should_create_note_widget(self):
        editor = self.note_delegate.createEditor(None, self.option, self.item.index())

        self.assertTrue(isinstance(editor, NoteWidget))

    def test_setEditorData_should_copy_data_from_note_to_editor(self):
        editor = NoteWidget()
        assert editor.dump_note().to_dict() != self.note.to_dict()

        self.note_delegate.setEditorData(editor, self.item.index())

        self.assertEqual(editor.dump_note().to_dict(), self.note.to_dict())

    def test_setModelData_should_copy_data_from_editor_to_note(self):
        assert isinstance(self.item.data(Qt.EditRole), Note)
        assert self.item.data(Qt.EditRole).to_dict() == self.note.to_dict()

        new_note = Note(
            title      = "X",
            body       = "Y",
            tags       = ["W", "Z"],
            created_at = datetime.utcnow()
        )
        assert new_note.to_dict() != self.note.to_dict()

        editor = NoteWidget()
        editor.load_note(new_note)

        self.note_delegate.setModelData(editor, self.model, self.item.index())
        new_item_value = self.item.data(Qt.EditRole)

        self.assertTrue(isinstance(new_item_value, Note))
        self.assertNotEqual(new_item_value, self.note)
        self.assertNotEqual(new_item_value, new_note)
        self.assertEqual(new_item_value.to_dict(), new_note.to_dict())

    def test_updateEditorGeometry_should_change_editor_size_and_position(self):
        self.option.rect = QRect(11, 22, 33, 44)
        expected_rect    = QRect(11 + 3, 22 + 3, 33 - 6, 44 - 6)
        editor           = NoteWidget()
        editor.load_note(self.note)

        self.note_delegate.updateEditorGeometry(editor, self.option, self.item.index())

        self.assertEqual(editor.geometry(), expected_rect)

    def test_sizeHint_should_return_the_height_of_a_standard_note_widget(self):
        note_widget = NoteWidget()

        size_hint = self.note_delegate.sizeHint(self.option, self.item.index())

        # NOTE: Preferred height is be the same in an empty and non-empty widget.
        # Preferred width may change depending on the content.
        self.assertEqual(size_hint.height(), note_widget.sizeHint().height())
