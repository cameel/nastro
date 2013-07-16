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
        assert editor.note != self.note

        self.note_delegate.setEditorData(editor, self.item.index())

        self.assertEqual(editor.note, self.note)

    def test_updateEditorGeometry_should_change_editor_size_and_position(self):
        self.option.rect = QRect(11, 22, 33, 44)
        editor           = NoteWidget()

        self.note_delegate.updateEditorGeometry(editor, self.option, self.item.index())

        self.assertEqual(editor.geometry(), self.option.rect)

    def test_sizeHint_should_return_the_height_of_a_standard_note_widget(self):
        note_widget = NoteWidget()

        size_hint = self.note_delegate.sizeHint(self.option, self.item.index())

        # NOTE: Preferred height is be the same in an empty and non-empty widget.
        # Preferred width may change depending on the content.
        self.assertEqual(size_hint.height(), note_widget.sizeHint().height())
