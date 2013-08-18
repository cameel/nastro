import unittest

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from ..model_helpers import level, tree_path, subtree_items, all_items, remove_items

class ModelHelpersTest(unittest.TestCase):
    def create_item_and_append(self, parent_item):
        item = QStandardItem()
        parent_item.appendRow(item)
        return item

    def setUp(self):
        self.model = QStandardItemModel()

        root_item = self.model.invisibleRootItem()

        self.item_0         = self.create_item_and_append(root_item)
        self.item_0_0       = self.create_item_and_append(self.item_0)
        self.item_0_0_0     = self.create_item_and_append(self.item_0_0)
        self.item_0_0_0_0   = self.create_item_and_append(self.item_0_0_0)
        self.item_1         = self.create_item_and_append(root_item)
        self.item_1_0       = self.create_item_and_append(self.item_1)
        self.item_1_0_0     = self.create_item_and_append(self.item_1_0)
        self.item_1_0_1     = self.create_item_and_append(self.item_1_0)
        self.item_1_0_2     = self.create_item_and_append(self.item_1_0)
        self.item_1_0_2_0   = self.create_item_and_append(self.item_1_0_2)
        self.item_1_0_2_0_0 = self.create_item_and_append(self.item_1_0_2_0)
        self.item_1_0_3     = self.create_item_and_append(self.item_1_0)
        self.item_1_1       = self.create_item_and_append(self.item_1)
        self.item_1_1_0     = self.create_item_and_append(self.item_1_1)
        self.item_2         = self.create_item_and_append(root_item)
        self.item_2_0       = self.create_item_and_append(self.item_2)
        self.item_3         = self.create_item_and_append(root_item)

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

    def test_subtree_items_should_iterate_over_all_subtree_items_inorder(self):
        expected_order = [
            self.item_1,
            self.item_1_0,
            self.item_1_0_0,
            self.item_1_0_1,
            self.item_1_0_2,
            self.item_1_0_2_0,
            self.item_1_0_2_0_0,
            self.item_1_0_3,
            self.item_1_1,
            self.item_1_1_0
        ]

        result = []
        for item in subtree_items(self.item_1):
            result.append(item)

        self.assertEqual(result, expected_order)

    def test_all_items_should_iterate_over_all_model_items_inorder(self):
        expected_order = [
            self.item_0,
            self.item_0_0,
            self.item_0_0_0,
            self.item_0_0_0_0,
            self.item_1,
            self.item_1_0,
            self.item_1_0_0,
            self.item_1_0_1,
            self.item_1_0_2,
            self.item_1_0_2_0,
            self.item_1_0_2_0_0,
            self.item_1_0_3,
            self.item_1_1,
            self.item_1_1_0,
            self.item_2,
            self.item_2_0,
            self.item_3
        ]

        result = []
        for item in all_items(self.model):
            result.append(item)

        self.assertEqual(result, expected_order)

    def test_remove_items_should_work_with_empty_list(self):
        row_count_before = self.model.rowCount()

        remove_items(self.model, [])

        self.assertEqual(self.model.rowCount(), row_count_before)

    def test_remove_items_should_remove_a_single_top_level_childless_item(self):
        assert self.item_3.parent() == None
        assert self.item_3.rowCount() == 0
        assert self.item_3 in [self.model.item(i) for i in range(self.model.rowCount())]

        row_count_before = self.model.rowCount()

        remove_items(self.model, [self.item_3.index()])

        self.assertEqual(self.model.rowCount(), row_count_before - 1)
        self.assertTrue(self.item_3 not in [self.model.item(i) for i in range(self.model.rowCount())])

    def test_remove_items_should_remove_a_childless_nested_item(self):
        assert self.item_1_1_0.parent() == self.item_1_1
        assert self.item_1_1_0.rowCount() == 0
        assert self.item_1_1_0 in [self.item_1_1.child(i) for i in range(self.item_1_1.rowCount())]

        row_count_before = self.item_1_1.rowCount()

        remove_items(self.model, [self.item_1_1_0.index()])

        self.assertEqual(self.item_1_1.rowCount(), row_count_before - 1)
        self.assertTrue(self.item_1 not in [self.item_1_1.child(i) for i in range(self.item_1_1.rowCount())])

    def test_remove_items_should_remove_an_item_and_all_its_children(self):
        assert self.item_1_1_0.parent() == self.item_1_1
        assert self.item_1_1_0.rowCount() == 0
        assert self.item_1_1_0 in [self.item_1_1.child(i) for i in range(self.item_1_1.rowCount())]

        row_count_before = self.item_1.rowCount()
        num_items_before = len(list(all_items(self.model)))
        items_to_remove  = list(subtree_items(self.item_1_0))

        remove_items(self.model, [self.item_1_0.index()])

        items_after = all_items(self.model)
        self.assertEqual(self.item_1.rowCount(), row_count_before - 1)
        self.assertEqual(len(list(items_after)), num_items_before - len(items_to_remove))

        # NOTE: This would cause problems if remove_items() was using removeRow() instead of takeRow().
        # We need the model not to delete the items if we want to access them after removal.
        for item in items_to_remove:
            self.assertTrue(item not in items_after)

    def test_remove_items_should_remove_multiple_items_none_of_which_is_a_parent_of_another(self):
        items_to_remove = [
            self.item_3,
            self.item_2_0,
            self.item_1_0_2_0_0
        ]
        indexes_to_remove = [item.index() for item in items_to_remove]

        items_before = list(all_items(self.model))

        remove_items(self.model, indexes_to_remove)

        items_after = list(all_items(self.model))
        self.assertEqual(len(items_after), len(items_before) - len(items_to_remove))
        for item in items_to_remove:
            self.assertTrue(item not in items_after)

    def test_remove_items_should_remove_multiple_items_from_a_single_subtree(self):
        items_to_remove = [
            self.item_0_0,
            self.item_0_0_0,
            self.item_0_0_0_0
        ]
        indexes_to_remove = [item.index() for item in items_to_remove]

        # All items to be removed have row() == 0 so that if sorting in the tested code is buggy
        # and ignores nesting level, their deletion order depends on the order on the list.
        # For this test they are ordered such that a buggy code would still delete children before parents.
        assert (
            sorted(indexes_to_remove, key = lambda index: index.row()) ==
            sorted(indexes_to_remove, key = lambda index: (level(index), index.row()))
        )

        items_before = list(all_items(self.model))

        remove_items(self.model, indexes_to_remove)

        items_after = list(all_items(self.model))
        self.assertEqual(len(items_after), len(items_before) - len(items_to_remove))
        for item in items_to_remove:
            self.assertTrue(item not in items_after)

    def test_remove_items_should_remove_multiple_items_from_a_single_subtree_and_not_crash_if_they_are_in_wrong_order(self):
        items_to_remove = [
            self.item_0_0_0_0,
            self.item_0_0_0,
            self.item_0_0
        ]
        indexes_to_remove = [item.index() for item in items_to_remove]

        # All items to be removed have row() == 0 so that if sorting in the tested code is buggy
        # and ignores nesting level, their deletion order depends on the order on the list.
        # This test ensures that the tested code takes nesting level into account. If not, Python
        # may even crash (if the code is using removeRow() which releases items).
        assert (
            sorted(indexes_to_remove, key = lambda index: index.row()) !=
            sorted(indexes_to_remove, key = lambda index: (level(index), index.row()))
        )

        items_before = list(all_items(self.model))

        remove_items(self.model, indexes_to_remove)

        items_after = list(all_items(self.model))
        self.assertEqual(len(items_after), len(items_before) - len(items_to_remove))
        for item in items_to_remove:
            self.assertTrue(item not in items_after)
