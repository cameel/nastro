import unittest
from datetime    import datetime
from collections import deque

from PyQt5.QtTest import QTest
from PyQt5.QtGui  import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from ..note               import Note, WrongAttributeType
from ..model_helpers      import all_items
from ..note_model_helpers import item_to_note, item_to_id, all_notes, assign_note_ids, dump_notes, load_notes
from ..note_model_helpers import EmptyNoteId, MissingParentId, MissingPrevSiblingId, MissingNote, SiblingCycle, ParentCycle, InconsistentParentIds, ConflictingSiblingIds

class NoteModelHelpersTest(unittest.TestCase):
    def setUp(self):
        self.model = QStandardItemModel()

    def sample_note_dict(self, id, parent_id, prev_item_id):
        timestamp = Note.serialize_timestamp(datetime.utcnow())
        return {
            'title':           'Note {}'.format(id),
            'body':            'body\n\t\n',
            'tags':            ['a tag', 'another tag'],
            'created_at':      timestamp,
            'modified_at':     timestamp,
            'id':              id,
            'parent_id':       parent_id,
            'prev_sibling_id': prev_item_id
        }

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

    def test_assign_note_ids_should_put_unique_integer_id_in_each_note(self):
        self.prepare_tree()
        assert all(note.id == None for note in all_notes(self.model))

        assign_note_ids(self.model)

        ids = [note.id for note in all_notes(self.model)]
        self.assertEqual(len(set(ids)), len(ids))
        self.assertEqual(min(ids), 1)
        self.assertEqual(max(ids), len(ids))

    def test_assign_note_ids_should_not_crash_if_given_empty_model(self):
        empty_model = QStandardItemModel()

        assign_note_ids(empty_model)

        self.assertEqual(empty_model.rowCount(), 0)

    def test_assign_note_ids_should_not_modify_ids_in_model_that_already_has_ids(self):
        self.prepare_tree()
        assert all(note.id == None for note in all_notes(self.model))

        next_id = 1
        for note in all_notes(self.model):
            note.id = next_id
            next_id += 1

        ids_before = list(range(1, next_id))

        assign_note_ids(self.model)

        ids_after = [note.id for note in all_notes(self.model)]
        self.assertEqual(ids_after, ids_before)

    def test_assign_note_ids_should_assign_ids_only_to_notes_that_do_not_already_have_them(self):
        self.prepare_tree()
        assert all(note.id == None for note in all_notes(self.model))

        next_id = 0
        for note in all_notes(self.model):
            if next_id % 2 == 0:
                note.id = next_id
            next_id += 1

        ids_before = [note.id for note in all_notes(self.model)]
        assert all(id == None for id in ids_before[1::2])

        assign_note_ids(self.model)

        ids_after = [note.id for note in all_notes(self.model)]
        self.assertEqual(ids_after[::2], ids_before[::2])
        self.assertTrue(all(id != None for id in ids_after[1::2]))

    def test_assign_note_ids_should_assign_ids_not_colliding_with_already_assigned_ones(self):
        self.prepare_tree()
        assert all(note.id == None for note in all_notes(self.model))

        next_id = 0
        for note in all_notes(self.model):
            if next_id % 2 == 0:
                note.id = next_id
            next_id += 1

        ids_before = [note.id for note in all_notes(self.model)]
        assert all(id == None for id in ids_before[1::2])

        assign_note_ids(self.model)

        ids_after = [note.id for note in all_notes(self.model)]
        self.assertEqual(set(ids_after) & set(ids_before[1::2]), set())

    def test_dump_notes_should_serialize_note_tree_into_a_list_of_dicts_of_primitives(self):
        self.prepare_tree()
        notes = list(all_notes(self.model))
        assign_note_ids(self.model)
        assert all(note.id != None for note in notes)

        serialized_notes = dump_notes(self.model)

        self.assertEqual(len(serialized_notes), len(notes))
        for key in ['title', 'body', 'tags', 'created_at', 'modified_at', 'id', 'parent_id', 'prev_sibling_id']:
            self.assertTrue(all(key in note_dict for note_dict in serialized_notes))

        for key in ['title', 'body', 'created_at', 'modified_at']:
            self.assertTrue(all(isinstance(note_dict[key], str) for note_dict in serialized_notes))

        for key in ['id', 'parent_id', 'prev_sibling_id']:
            self.assertTrue((note_dict[key] == None or all(isinstance(note_dict[key], int)) for note_dict in serialized_notes))

        self.assertTrue(all(all(isinstance(tag, str) for tag in note_dict['tags']) for note_dict in serialized_notes))

    def test_dump_notes_should_serialize_tree_structure_correctly(self):
        self.prepare_tree()
        assign_note_ids(self.model)

        items = list(all_items(self.model))
        assert all(item_to_id(item) != None for item in items)

        expected_tree = {
            item_to_id(self.item_0):         (None,              None),
            item_to_id(self.item_0_0):       (self.item_0,       None),
            item_to_id(self.item_0_0_0):     (self.item_0_0,     None),
            item_to_id(self.item_0_0_0_0):   (self.item_0_0_0,   None),
            item_to_id(self.item_1):         (None,              self.item_0),
            item_to_id(self.item_1_0):       (self.item_1,       None),
            item_to_id(self.item_1_0_0):     (self.item_1_0,     None),
            item_to_id(self.item_1_0_1):     (self.item_1_0,     self.item_1_0_0),
            item_to_id(self.item_1_0_2):     (self.item_1_0,     self.item_1_0_1),
            item_to_id(self.item_1_0_2_0):   (self.item_1_0_2,   None),
            item_to_id(self.item_1_0_2_0_0): (self.item_1_0_2_0, None),
            item_to_id(self.item_1_0_3):     (self.item_1_0,     self.item_1_0_2),
            item_to_id(self.item_1_1):       (self.item_1,       self.item_1_0),
            item_to_id(self.item_1_1_0):     (self.item_1_1,     None),
            item_to_id(self.item_2):         (None,              self.item_1),
            item_to_id(self.item_2_0):       (self.item_2,       None),
            item_to_id(self.item_3):         (None,              self.item_2)
        }

        serialized_notes = dump_notes(self.model)

        serialized_id_set = set(note_dict['id']  for note_dict in serialized_notes)
        note_id_set       = set(item_to_id(item) for item      in items)

        self.assertEqual(serialized_id_set, note_id_set)

        for note_dict in serialized_notes:
            expected_node            = expected_tree[note_dict['id']]
            expected_parent_id       = item_to_id(expected_node[0]) if expected_node[0] != None else None
            expected_prev_sibling_id = item_to_id(expected_node[1]) if expected_node[1] != None else None

            self.assertEqual(note_dict['parent_id'],       expected_parent_id)
            self.assertEqual(note_dict['prev_sibling_id'], expected_prev_sibling_id)

    def test_dump_notes_should_handle_empty_model(self):
        empty_model = QStandardItemModel()

        serialized_notes = dump_notes(empty_model)

        self.assertEqual(serialized_notes, [])

    def test_load_notes_should_deserialize_tree_structure_correctly(self):
        self.prepare_tree()
        assign_note_ids(self.model)
        serialized_notes_before = dump_notes(self.model)
        assert all(note_dict['id'] != None for note_dict in serialized_notes_before)

        new_model = load_notes(serialized_notes_before)

        serialized_notes_after = dump_notes(new_model)

        note_id = lambda note_dict: note_dict['id']
        self.assertEqual(sorted(serialized_notes_after, key = note_id), sorted(serialized_notes_before, key = note_id))

    def test_load_notes_should_raise_error_if_tree_contains_sibling_cycle(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    4),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 1,    3)
        ]

        with self.assertRaises(SiblingCycle):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_contains_sibling_cycle_that_does_not_include_all_siblings(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(5, 1,    None),
            self.sample_note_dict(6, 1,    5),
            self.sample_note_dict(7, 1,    6),
            self.sample_note_dict(2, 1,    4),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 1,    3)
        ]

        with self.assertRaises(SiblingCycle):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_contains_an_element_which_is_its_own_prev_sibling(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 1,    4)
        ]

        with self.assertRaises(SiblingCycle):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_contains_parent_cycle(self):
        serialized_notes = [
            self.sample_note_dict(1, 4, None),
            self.sample_note_dict(2, 1, None),
            self.sample_note_dict(3, 2, None),
            self.sample_note_dict(4, 3, None)
        ]

        with self.assertRaises(ParentCycle):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_contains_parent_cycle_that_does_not_reach_top_level(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 2,    None),
            self.sample_note_dict(4, 3,    None),
            self.sample_note_dict(5, 8,    None),
            self.sample_note_dict(6, 5,    None),
            self.sample_note_dict(7, 6,    None),
            self.sample_note_dict(8, 7,    None),
            self.sample_note_dict(9, 8,    5)
        ]

        with self.assertRaises(ParentCycle):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_contains_an_element_which_is_its_own_parent(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 2,    None),
            self.sample_note_dict(4, 4,    None)
        ]

        with self.assertRaises(ParentCycle):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_siblings_with_the_same_prev_sibling_id(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 1,    2),
            self.sample_note_dict(5, 1,    4)
        ]

        with self.assertRaises(ConflictingSiblingIds):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_siblings_with_the_same_prev_sibling_id_being_none(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 1,    None),
            self.sample_note_dict(4, 1,    2),
            self.sample_note_dict(5, 1,    4)
        ]

        with self.assertRaises(ConflictingSiblingIds):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_contains_note_with_empty_id(self):
        serialized_notes = [
            self.sample_note_dict(1,    None, None),
            self.sample_note_dict(2,    1,    None),
            self.sample_note_dict(3,    1,    2),
            self.sample_note_dict(4,    1,    3),
            self.sample_note_dict(None, 1,    4)
        ]

        with self.assertRaises(EmptyNoteId):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_contains_note_without_parent_id_attribute(self):
        # NOTE: It's about the attribute missing from the dict, not being None
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 1,    3),
            self.sample_note_dict(5, 1,    4)
        ]

        del serialized_notes[-1]['parent_id']

        with self.assertRaises(MissingParentId):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_tree_contains_note_without_prev_sibling_id_attribute(self):
        # NOTE: It's about the attribute missing from the dict, not being None
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 1,    3),
            self.sample_note_dict(5, 1,    4)
        ]

        del serialized_notes[-1]['prev_sibling_id']

        with self.assertRaises(MissingPrevSiblingId):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_prev_sibling_id_does_not_exist_in_tree(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 1,    666),
            self.sample_note_dict(5, 1,    4)
        ]

        with self.assertRaises(MissingNote):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_parent_id_does_not_exist_in_tree(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 666,  3),
            self.sample_note_dict(5, 1,    4)
        ]

        with self.assertRaises(MissingNote):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_prev_sibling_has_different_parent(self):
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 1,    2),
            self.sample_note_dict(4, 5,    3),
            self.sample_note_dict(5, None, 4)
        ]

        with self.assertRaises(InconsistentParentIds):
            load_notes(serialized_notes)

    def test_load_notes_should_raise_error_if_prev_sibling_at_a_different_level(self):
        # This can also be classified as siblings having different parents but
        # the structure here is a bit different so the example is included for completeness.
        serialized_notes = [
            self.sample_note_dict(1, None, None),
            self.sample_note_dict(2, 1,    None),
            self.sample_note_dict(3, 2,    None),
            self.sample_note_dict(4, 2,    3),
            self.sample_note_dict(5, 1,    4)
        ]

        with self.assertRaises(InconsistentParentIds):
            load_notes(serialized_notes)

    def test_load_notes_should_correctly_handle_notes_not_in_the_final_order(self):
        # This means note's prev sibling and/or parent coming after the note
        serialized_notes_before = [
            self.sample_note_dict(15, 7,    14),
            self.sample_note_dict(7,  5,    6),
            self.sample_note_dict(2,  1,    None),
            self.sample_note_dict(14, 7,    10),
            self.sample_note_dict(4,  1,    3),
            self.sample_note_dict(17, 5,    7),
            self.sample_note_dict(18, 5,    17),
            self.sample_note_dict(10, 7,    9),
            self.sample_note_dict(11, 10,   None),
            self.sample_note_dict(3,  1,    2),
            self.sample_note_dict(12, 10,   11),
            self.sample_note_dict(9,  7,    8),
            self.sample_note_dict(8,  7,    None),
            self.sample_note_dict(16, 15,   None),
            self.sample_note_dict(13, 10,   12),
            self.sample_note_dict(6,  5,    None),
            self.sample_note_dict(20, 19,   None),
            self.sample_note_dict(19, None, 5),
            self.sample_note_dict(5,  None, 1),
            self.sample_note_dict(1,  None, None)
        ]

        new_model = load_notes(serialized_notes_before)

        serialized_notes_after = dump_notes(new_model)

        note_id = lambda note_dict: note_dict['id']
        self.assertEqual(sorted(serialized_notes_after, key = note_id), sorted(serialized_notes_before, key = note_id))

    def test_load_notes_should_detect_wrong_attribute_types(self):
        note_dict = {
            'title':           "X",
            'body':            "Y",
            'tags':            ["a", "b", "c"],
            'created_at':      "2013-06-16T00:00:00.000000",
            'modified_at':     "2013-07-16T00:00:00.000000",
            'id':              1,
            'parent_id':       None,
            'prev_sibling_id': None
        }

        # ASSUMPTION: This does not raise exceptions
        load_notes([note_dict])

        wrong_type_samples = [
            ('title',           1),
            ('body',            1),
            ('tags',            ("a", "b", "c")),
            ('tags',            ()),
            ('tags',            {}),
            ('tags',            set()),
            ('tags',            deque(["a", "b", "c"])),
            ('tags',            [1, 2, 3]),
            ('created_at',      1234567890),
            ('created_at',      datetime(2013, 1, 1)),
            ('modified_at',     1234567890),
            ('modified_at',     datetime(2013, 1, 1)),
            ('id',              "10"),
            ('id',              []),
            ('parent_id',       "10"),
            ('parent_id',       []),
            ('prev_sibling_id', "10"),
            ('prev_sibling_id', [])
        ]

        for tested_attribute, wrong_value in wrong_type_samples:
            filtered_note_dict = {attribute: note_dict[attribute] if attribute != tested_attribute else wrong_value for attribute in note_dict}

            with self.assertRaises(WrongAttributeType):
                load_notes([filtered_note_dict])
