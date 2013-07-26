import unittest

from PyQt5.QtTest import QTest
from PyQt5.QtGui  import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from ..note               import Note
from ..note_model_helpers import item_to_note, item_to_id, all_notes

class NoteModelHelpersTest(unittest.TestCase):
    def setUp(self):
        self.model = QStandardItemModel()

    def create_note_and_append(self, parent_item, title):
        note = Note(title = title)
        item = QStandardItem()
        item.setData(note, Qt.EditRole)
        parent_item.appendRow(item)
        return item

    def prepare_tree(self):
        root_item = self.model.invisibleRootItem()

        self.item_0         = self.create_note_and_append(root_item,         "Note 0")
        self.item_0_0       = self.create_note_and_append(self.item_0,       "Note 0_0")
        self.item_0_0_0     = self.create_note_and_append(self.item_0_0,     "Note 0_0_0")
        self.item_0_0_0_0   = self.create_note_and_append(self.item_0_0_0,   "Note 0_0_0_0")
        self.item_1         = self.create_note_and_append(root_item,         "Note 1")
        self.item_1_0       = self.create_note_and_append(self.item_1,       "Note 1_0")
        self.item_1_0_0     = self.create_note_and_append(self.item_1_0,     "Note 1_0_0")
        self.item_1_0_1     = self.create_note_and_append(self.item_1_0,     "Note 1_0_1")
        self.item_1_0_2     = self.create_note_and_append(self.item_1_0,     "Note 1_0_2")
        self.item_1_0_2_0   = self.create_note_and_append(self.item_1_0_2,   "Note 1_0_2_0")
        self.item_1_0_2_0_0 = self.create_note_and_append(self.item_1_0_2_0, "Note 1_0_2_0_0")
        self.item_1_0_3     = self.create_note_and_append(self.item_1_0,     "Note 1_0_3")
        self.item_1_1       = self.create_note_and_append(self.item_1,       "Note 1_1")
        self.item_1_1_0     = self.create_note_and_append(self.item_1_1,     "Note 1_1_0")
        self.item_2         = self.create_note_and_append(root_item,         "Note 2")
        self.item_2_0       = self.create_note_and_append(self.item_2,       "Note 2_0")
        self.item_3         = self.create_note_and_append(root_item,         "Note 3")

    def test_all_items_should_iterate_over_all_model_items_inorder(self):
        self.prepare_tree()

        expected_order = [
            item_to_note(self.item_0),
            item_to_note(self.item_0_0),
            item_to_note(self.item_0_0_0),
            item_to_note(self.item_0_0_0_0),
            item_to_note(self.item_1),
            item_to_note(self.item_1_0),
            item_to_note(self.item_1_0_0),
            item_to_note(self.item_1_0_1),
            item_to_note(self.item_1_0_2),
            item_to_note(self.item_1_0_2_0),
            item_to_note(self.item_1_0_2_0_0),
            item_to_note(self.item_1_0_3),
            item_to_note(self.item_1_1),
            item_to_note(self.item_1_1_0),
            item_to_note(self.item_2),
            item_to_note(self.item_2_0),
            item_to_note(self.item_3)
        ]

        result = []
        for note in all_notes(self.model):
            result.append(note)

        self.assertEqual(result, expected_order)
