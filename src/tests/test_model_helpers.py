import unittest

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QStandardItemModel, QStandardItem

from ..model_helpers import level, tree_path

class ModelHelpersTest(unittest.TestCase):
    def setUp(self):
        self.model = QStandardItemModel()

        root_item = self.model.invisibleRootItem()
        self.item_0 = QStandardItem()
        root_item.appendRow(self.item_0)
        self.item_1 = QStandardItem()
        root_item.appendRow(self.item_1)
        self.item_2 = QStandardItem()
        root_item.appendRow(self.item_2)
        self.item_3 = QStandardItem()
        root_item.appendRow(self.item_3)

        self.item_0_0 = QStandardItem()
        self.item_0.appendRow(self.item_0_0)

        self.item_0_0_0 = QStandardItem()
        self.item_0_0.appendRow(self.item_0_0_0)

        self.item_0_0_0_0 = QStandardItem()
        self.item_0_0_0.appendRow(self.item_0_0_0_0)

        self.item_1_0 = QStandardItem()
        self.item_1.appendRow(self.item_1_0)
        self.item_1_1 = QStandardItem()
        self.item_1.appendRow(self.item_1_1)

        self.item_1_0_0 = QStandardItem()
        self.item_1_0.appendRow(self.item_1_0_0)
        self.item_1_0_1 = QStandardItem()
        self.item_1_0.appendRow(self.item_1_0_1)
        self.item_1_0_2 = QStandardItem()
        self.item_1_0.appendRow(self.item_1_0_2)
        self.item_1_0_3 = QStandardItem()
        self.item_1_0.appendRow(self.item_1_0_3)

        self.item_1_0_2_0 = QStandardItem()
        self.item_1_0_2.appendRow(self.item_1_0_2_0)

        self.item_1_0_2_0_0 = QStandardItem()
        self.item_1_0_2_0.appendRow(self.item_1_0_2_0_0)

        self.item_1_1_0 = QStandardItem()
        self.item_1_1.appendRow(self.item_1_1_0)

        self.item_2_0 = QStandardItem()
        self.item_2.appendRow(self.item_2_0)

    def test_level_should_return_the_level_at_which_an_item_pointed_at_by_index_is_nested_in_the_model(self):
        self.assertEqual(level(self.item_0), 0)
        self.assertEqual(level(self.item_1), 0)
        self.assertEqual(level(self.item_1_0), 1)
        self.assertEqual(level(self.item_1_0_0), 2)
        self.assertEqual(level(self.item_1_0_1), 2)
        self.assertEqual(level(self.item_1_0_2), 2)
        self.assertEqual(level(self.item_1_0_2_0), 3)
        self.assertEqual(level(self.item_1_0_2_0_0), 4)
        self.assertEqual(level(self.item_1_0_3), 2)
        self.assertEqual(level(self.item_1_1), 1)
        self.assertEqual(level(self.item_1_1_0), 2)
        self.assertEqual(level(self.item_2), 0)
        self.assertEqual(level(self.item_2_0), 1)
        self.assertEqual(level(self.item_3), 0)

    def test_level_should_work_with_model_indexes(self):
        self.assertEqual(level(self.item_0.index()), 0)
        self.assertEqual(level(self.item_1.index()), 0)
        self.assertEqual(level(self.item_1_0.index()), 1)
        self.assertEqual(level(self.item_1_0_0.index()), 2)
        self.assertEqual(level(self.item_1_0_1.index()), 2)
        self.assertEqual(level(self.item_1_0_2.index()), 2)
        self.assertEqual(level(self.item_1_0_2_0.index()), 3)
        self.assertEqual(level(self.item_1_0_2_0_0.index()), 4)
        self.assertEqual(level(self.item_1_0_3.index()), 2)
        self.assertEqual(level(self.item_1_1.index()), 1)
        self.assertEqual(level(self.item_1_1_0.index()), 2)
        self.assertEqual(level(self.item_2.index()), 0)
        self.assertEqual(level(self.item_2_0.index()), 1)
        self.assertEqual(level(self.item_3.index()), 0)

    def test_item_level_should_return_0_for_invisible_root_item(self):
        root_item = self.model.invisibleRootItem()
        self.assertEqual(level(root_item), 0)

    def test_tree_path_should_return_the_row_numbers_of_the_item_and_all_ancestors(self):
        self.assertEqual(tree_path(self.item_0),                     [0])
        self.assertEqual(tree_path(self.item_0_0),                [0, 0])
        self.assertEqual(tree_path(self.item_0_0_0),           [0, 0, 0])
        self.assertEqual(tree_path(self.item_0_0_0_0),      [0, 0, 0, 0])
        self.assertEqual(tree_path(self.item_1),                     [1])
        self.assertEqual(tree_path(self.item_1_0),                [0, 1])
        self.assertEqual(tree_path(self.item_1_0_0),           [0, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_1),           [1, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_2),           [2, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_2_0),      [0, 2, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_2_0_0), [0, 0, 2, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_3),           [3, 0, 1])
        self.assertEqual(tree_path(self.item_1_1),                [1, 1])
        self.assertEqual(tree_path(self.item_1_1_0),           [0, 1, 1])
        self.assertEqual(tree_path(self.item_2),                     [2])
        self.assertEqual(tree_path(self.item_2_0),                [0, 2])
        self.assertEqual(tree_path(self.item_3),                     [3])

    def test_tree_path_should_work_with_model_indexes(self):
        self.assertEqual(tree_path(self.item_0.index()),                     [0])
        self.assertEqual(tree_path(self.item_0_0.index()),                [0, 0])
        self.assertEqual(tree_path(self.item_0_0_0.index()),           [0, 0, 0])
        self.assertEqual(tree_path(self.item_0_0_0_0.index()),      [0, 0, 0, 0])
        self.assertEqual(tree_path(self.item_1.index()),                     [1])
        self.assertEqual(tree_path(self.item_1_0.index()),                [0, 1])
        self.assertEqual(tree_path(self.item_1_0_0.index()),           [0, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_1.index()),           [1, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_2.index()),           [2, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_2_0.index()),      [0, 2, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_2_0_0.index()), [0, 0, 2, 0, 1])
        self.assertEqual(tree_path(self.item_1_0_3.index()),           [3, 0, 1])
        self.assertEqual(tree_path(self.item_1_1.index()),                [1, 1])
        self.assertEqual(tree_path(self.item_1_1_0.index()),           [0, 1, 1])
        self.assertEqual(tree_path(self.item_2.index()),                     [2])
        self.assertEqual(tree_path(self.item_2_0.index()),                [0, 2])
        self.assertEqual(tree_path(self.item_3.index()),                     [3])
