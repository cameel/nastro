import unittest
import sys
from datetime import datetime, timedelta

from PyQt5.QtTest    import QTest
from PyQt5.QtCore    import Qt, QRegExp, QAbstractItemModel, QItemSelection, QItemSelectionModel, QAbstractProxyModel
from PyQt5.QtGui     import QStandardItemModel, QStandardItem

from .dummy_application        import application
from ..tape_widget             import TapeWidget
from ..note                    import Note
from ..note_edit               import NoteEdit
from ..tape_filter_proxy_model import TapeFilterProxyModel
from ..note_model_helpers      import all_notes, assign_note_ids

class TapeWidgetTest(unittest.TestCase):
    def setUp(self):
        self.tape_widget = TapeWidget()

        self.notes = [
            Note(
                title      = "H+X",
                body       = "Y",
                tags       = ["Z"],
                created_at = datetime.utcnow()
            ),
            Note(
                title      = "A",
                body       = "B",
                tags       = ["C", "PPP RRR"],
                created_at = datetime.utcnow()
            ),
            Note(
                title      = "1",
                body       = "2",
                tags       = ["3", "PPP\tRRR"],
                created_at = datetime.utcnow()
            ),
            Note(
                title      = "I",
                body       = "b",
                tags       = ["VVV", "III"],
                created_at = datetime.utcnow()
            )
        ]

    def prepare_tape(self, index_sequence = None):
        if index_sequence == None:
            index_sequence = range(len(self.notes))

        for i in index_sequence:
            self.tape_widget.add_note(self.notes[i])

        assert self.tape_widget._tape_model.rowCount() == len(index_sequence)
        assert len(self.tape_widget._view.selectedIndexes()) == 0

    def test_set_model_replace_the_model_with_a_new_one(self):
        new_model = QStandardItemModel()
        item      = QStandardItem()
        item.setData(self.notes[0], Qt.EditRole)
        new_model.appendRow(item)

        assert self.tape_widget.model().rowCount() == 0

        self.tape_widget.set_model(new_model)

        self.assertEqual(self.tape_widget.model(), new_model)
        self.assertEqual(self.tape_widget.proxy_model().sourceModel(), new_model)
        self.assertEqual(self.tape_widget.model().rowCount(), 1)
        self.assertEqual(self.tape_widget.model().item(0, 0), item)

    def test_model_should_return_the_undelying_model(self):
        model = self.tape_widget.model()

        self.assertTrue(isinstance(model, QAbstractItemModel))

    def test_proxy_model_should_return_the_filtered_model_that_acts_as_a_proxy_for_the_actual_model(self):
        proxy_model = self.tape_widget.proxy_model()

        self.assertTrue(isinstance(proxy_model, QAbstractProxyModel))
        self.assertEqual(proxy_model.sourceModel(), self.tape_widget.model())

    def test_notes_should_enumerate_all_notes_in_the_same_order_as_note(self):
        with self.assertRaises(StopIteration):
            next(self.tape_widget.notes())

        self.prepare_tape()

        for (i, note) in enumerate(self.tape_widget.notes()):
            self.assertEqual(note, self.tape_widget.model().item(i).data(Qt.EditRole))

    def test_create_empty_note_should_not_assign_id(self):
        note = self.tape_widget.create_empty_note(666)

        self.assertEqual(note.id, None)

    def test_add_note_should_create_a_new_note(self):
        assert len(list(self.tape_widget.notes())) == 0

        self.tape_widget.add_note()

        self.assertEqual(len(list(self.tape_widget.notes())), 1)

        note = self.tape_widget.model().item(0).data(Qt.EditRole)
        assert isinstance(note, Note)

        self.assertEqual(note.title, 'Note 1')
        self.assertEqual(note.body,  '')
        self.assertEqual(note.tags,  [])

        # ASSUMPTION: This test executes in much less than 10 seconds.
        self.assertTrue(note.created_at > datetime.utcnow() - timedelta(0, 10))
        self.assertEqual(note.created_at, note.modified_at)

    def test_add_note_should_add_existing_note(self):
        assert len(list(self.tape_widget.notes())) == 0

        self.tape_widget.add_note(self.notes[0])

        self.assertEqual(len(list(self.tape_widget.notes())), 1)
        self.assertEqual(self.tape_widget.model().item(0).data(Qt.EditRole), self.notes[0])

    def test_add_note_should_append_notes_at_the_end_of_the_tape(self):
        assert len(list(self.tape_widget.notes())) == 0

        self.tape_widget.add_note(self.notes[0])
        self.tape_widget.add_note()
        self.tape_widget.add_note(self.notes[1])

        self.assertEqual(len(list(self.tape_widget.notes())), 3)
        self.assertEqual(self.tape_widget.model().item(0).data(Qt.EditRole), self.notes[0])
        self.assertEqual(self.tape_widget.model().item(2).data(Qt.EditRole), self.notes[1])

    def test_add_note_should_add_child_note(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        new_note = self.tape_widget.create_empty_note(777)
        self.tape_widget.add_note(new_note, self.tape_widget.model().item(2).index())

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 1)
        self.assertEqual(self.tape_widget.model().item(2).rowCount(), 1)
        self.assertEqual(self.tape_widget.model().item(2).child(0).data(Qt.EditRole), new_note)

    def test_add_note_should_append_child_at_the_end_of_parents_list(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        parent_note = self.tape_widget.create_empty_note(777)
        self.tape_widget.add_note(parent_note, self.tape_widget.model().item(2).index())
        assert self.tape_widget.model().item(2).child(0).data(Qt.EditRole) == parent_note
        assert self.tape_widget.model().item(2).rowCount() == 1

        child_note_1 = self.tape_widget.create_empty_note(888)
        self.tape_widget.add_note(child_note_1, self.tape_widget.model().item(2).child(0).index())
        child_note_2 = self.tape_widget.create_empty_note(999)
        self.tape_widget.add_note(child_note_2, self.tape_widget.model().item(2).child(0).index())

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 3)
        self.assertEqual(self.tape_widget.model().item(2).child(0).rowCount(), 2)
        self.assertEqual(self.tape_widget.model().item(2).child(0).child(0).data(Qt.EditRole), child_note_1)
        self.assertEqual(self.tape_widget.model().item(2).child(0).child(1).data(Qt.EditRole), child_note_2)

    def test_add_and_focus_note_should_create_a_note_and_focus_the_tape_on_it(self):
        assert len(self.notes) >= 2
        self.prepare_tape()

        index = self.tape_widget.proxy_model().index(1, 0)
        self.tape_widget.set_note_selection(index, True)
        assert self.tape_widget.selected_proxy_indexes() == [index]

        self.tape_widget.add_and_focus_note()

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 1)
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 1)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].row(), len(list(self.tape_widget.notes())) - 1)
        self.assertEqual(self.tape_widget.get_filter(), '')

    def test_add_and_focus_note_should_work_even_if_the_new_note_does_not_match_the_search_filter(self):
        assert len(self.notes) >= 2
        self.prepare_tape()

        keyword = "a filter not likely to match a new note"

        self.tape_widget.set_filter(keyword)
        assert not TapeFilterProxyModel.note_matches(QRegExp(keyword, False, QRegExp.FixedString), self.tape_widget.create_empty_note(0))

        self.tape_widget.add_and_focus_note()

        # This test is meant to detect a situation in which the search filter is cleared after (not before)
        # taking the index of a new note to select it. If the code is buggy Qt will probably just print something
        # to the console rather than cause an exception to be raised. If we're lucky, the note won't be selected
        # and the test will fail but I don't think we can count on that.
        self.assertEqual(self.tape_widget.get_filter(), '')
        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 1)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].row(), len(list(self.tape_widget.notes())) - 1)

    def test_add_and_focus_note_should_create_child_note(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        parent_proxy_index = self.tape_widget.proxy_model().mapFromSource(self.tape_widget.model().item(2).index())

        self.tape_widget.add_and_focus_note(parent_proxy_index)

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 1)
        self.assertEqual(self.tape_widget.model().item(2).rowCount(), 1)
        self.assertTrue(isinstance(self.tape_widget.model().item(2).child(0).data(Qt.EditRole), Note))
        self.assertTrue(not self.tape_widget.model().item(2).child(0).data(Qt.EditRole) in self.notes)
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 1)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].row(), 0)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].parent(), parent_proxy_index)

    def test_remove_notes_should_remove_multiple_notes_from_the_tape(self):
        self.prepare_tape(range(4))

        index_1 = self.tape_widget.model().index(1, 0)
        index_2 = self.tape_widget.model().index(2, 0)
        self.tape_widget.remove_notes([index_2, index_1])

        self.assertEqual(self.tape_widget.model().rowCount(), 2)
        self.assertEqual(self.tape_widget.model().item(0, 0).data(Qt.EditRole), self.notes[0])
        self.assertEqual(self.tape_widget.model().item(1, 0).data(Qt.EditRole), self.notes[3])

    def test_by_default_all_notes_should_be_visible(self):
        assert self.tape_widget.get_filter() == ''

        self.prepare_tape(range(3))

        self. assertEqual(len(list(self.tape_widget.notes())), 3)
        self.assertEqual(self.tape_widget._tape_filter_proxy_model.rowCount(), 3)
        for i in range(3):
            self.assertEqual(self.tape_widget._tape_filter_proxy_model.data(self.tape_widget._tape_filter_proxy_model.index(i, 0)).to_dict(), self.notes[i].to_dict())

    def test_get_filter_should_return_search_filter(self):
        keyword = "a keyword"
        self.tape_widget._search_box.setText(keyword)

        self.assertEqual(self.tape_widget.get_filter(), keyword)
        self.assertEqual(self.tape_widget.get_filter(), self.tape_widget._search_box.text())
        self.assertEqual(self.tape_widget._tape_filter_proxy_model.filterRegExp().patternSyntax(), QRegExp.FixedString)
        self.assertEqual(self.tape_widget._tape_filter_proxy_model.filterRegExp().pattern(), keyword)

    def test_set_filter_should_set_filter_string(self):
        keyword = 'B'
        assert self.tape_widget.get_filter() != keyword

        self.tape_widget.set_filter(keyword)

        self.assertEqual(self.tape_widget.get_filter(), keyword)

    def test_set_filter_should_hide_non_matching_notes(self):
        keyword = 'B'

        assert not TapeFilterProxyModel.note_matches(QRegExp(keyword, False, QRegExp.FixedString), self.notes[0])
        assert     TapeFilterProxyModel.note_matches(QRegExp(keyword, False, QRegExp.FixedString), self.notes[1])
        assert not TapeFilterProxyModel.note_matches(QRegExp(keyword, False, QRegExp.FixedString), self.notes[2])

        self.prepare_tape(range(3))

        self.tape_widget.set_filter(keyword)

        self.assertEqual(len(list(self.tape_widget.notes())), 3)
        self.assertEqual(self.tape_widget._tape_filter_proxy_model.rowCount(), 1)
        self.assertEqual(self.tape_widget._tape_filter_proxy_model.data(self.tape_widget._tape_filter_proxy_model.index(0, 0)).to_dict(), self.notes[1].to_dict())

    def test_selected_indexes_should_return_model_indexes_for_selected_items(self):
        self.prepare_tape()

        start_index = self.tape_widget.proxy_model().index(1, 0)
        end_index   = self.tape_widget.proxy_model().index(2, 0)

        self.tape_widget._view.selectionModel().select(
            QItemSelection(start_index, end_index),
            QItemSelectionModel.Select
        )

        result = self.tape_widget.selected_indexes()

        self.assertEqual(len(self.tape_widget._view.selectedIndexes()), 2)
        self.assertTrue(all(self.tape_widget.model().itemFromIndex(index) != None for index in result))
        self.assertTrue(any(index.row() == 1 for index in result))
        self.assertTrue(any(index.row() == 2 for index in result))

    def test_selected_proxy_indexes_should_return_proxy_model_indexes_for_selected_items(self):
        self.prepare_tape()

        start_index = self.tape_widget.proxy_model().index(1, 0)
        end_index   = self.tape_widget.proxy_model().index(2, 0)

        self.tape_widget._view.selectionModel().select(
            QItemSelection(start_index, end_index),
            QItemSelectionModel.Select
        )

        result = self.tape_widget.selected_proxy_indexes()

        self.assertEqual(len(self.tape_widget._view.selectedIndexes()), 2)
        self.assertTrue(all(self.tape_widget.proxy_model().mapToSource(index) != None for index in result))
        self.assertTrue(any(index.row() == 1 for index in result))
        self.assertTrue(any(index.row() == 2 for index in result))

    def test_by_default_no_note_should_be_selected(self):
        self.prepare_tape()

        self.assertEqual(self.tape_widget.selected_proxy_indexes(), [])

    def test_set_note_selection_should_select_a_note(self):
        assert len(self.notes) >= 2
        self.prepare_tape()

        index = self.tape_widget.proxy_model().index(1, 0)
        self.tape_widget.set_note_selection(index, True)

        self.assertEqual(self.tape_widget.selected_proxy_indexes(), [index])

    def test_set_note_selection_should_not_deselect_previously_selected_note(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        index_1 = self.tape_widget.proxy_model().index(1, 0)
        index_2 = self.tape_widget.proxy_model().index(2, 0)
        self.tape_widget.set_note_selection(index_1, True)
        self.tape_widget.set_note_selection(index_2, True)

        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 2)
        self.assertTrue(index_1 in self.tape_widget.selected_proxy_indexes())
        self.assertTrue(index_2 in self.tape_widget.selected_proxy_indexes())

    def test_set_note_selection_should_deselect_a_note(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        index_1 = self.tape_widget.proxy_model().index(1, 0)
        index_2 = self.tape_widget.proxy_model().index(2, 0)
        self.tape_widget.set_note_selection(index_1, True)
        self.tape_widget.set_note_selection(index_2, True)

        assert len(self.tape_widget.selected_proxy_indexes()), 2
        assert index_1 in self.tape_widget.selected_proxy_indexes()
        assert index_2 in self.tape_widget.selected_proxy_indexes()

        self.tape_widget.set_note_selection(index_2, False)

        self.assertEqual(self.tape_widget.selected_proxy_indexes(), [index_1])

    def test_clear_selection_should_make_all_notes_deselected(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        index_1 = self.tape_widget.proxy_model().index(1, 0)
        index_2 = self.tape_widget.proxy_model().index(2, 0)
        self.tape_widget.set_note_selection(index_1, True)
        self.tape_widget.set_note_selection(index_2, True)
        assert len(self.tape_widget.selected_proxy_indexes()), 2
        assert index_1 in self.tape_widget.selected_proxy_indexes()
        assert index_2 in self.tape_widget.selected_proxy_indexes()

        self.tape_widget.clear_selection()

        self.assertEqual(self.tape_widget.selected_proxy_indexes(), [])

    def test_delete_selected_notes_should_do_nothing_if_nothing_is_selected(self):
        self.prepare_tape()

        assert len(self.tape_widget.selected_proxy_indexes()) == 0

        self.tape_widget.delete_selected_notes()

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes))

    def test_delete_selected_notes_should_delete_selected_note(self):
        assert len(self.notes) >= 2
        self.prepare_tape()

        index = self.tape_widget.proxy_model().index(1, 0)
        self.tape_widget.set_note_selection(index, True)
        assert self.tape_widget.selected_proxy_indexes() == [index]

        self.tape_widget.delete_selected_notes()

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) - 1)

    def test_delete_selected_notes_should_handle_deleting_multiple_notes(self):
        assert len(self.notes) >= 2
        self.prepare_tape()
        assign_note_ids(self.tape_widget.model())

        index_1 = self.tape_widget.proxy_model().index(1, 0)
        index_2 = self.tape_widget.proxy_model().index(2, 0)
        self.tape_widget.set_note_selection(index_1, True)
        self.tape_widget.set_note_selection(index_2, True)
        assert len(self.tape_widget.selected_proxy_indexes()), 2
        assert index_1 in self.tape_widget.selected_proxy_indexes()
        assert index_2 in self.tape_widget.selected_proxy_indexes()

        self.tape_widget.delete_selected_notes()

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) - 2)

        note_ids = [note.id for note in all_notes(self.tape_widget.model())]
        assert all(id != None for id in note_ids)

        self.assertTrue(self.notes[1].id not in note_ids)
        self.assertTrue(self.notes[2].id not in note_ids)

    def test_new_sibling_handler_should_add_top_level_note_if_nothing_selected(self):
        assert len(self.notes) >= 2
        self.prepare_tape()

        self.tape_widget._new_sibling_handler()

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 1)
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 1)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].row(), len(self.notes))
        self.assertEqual(self.tape_widget.get_filter(), '')

    def test_new_sibling_handler_should_add_top_level_note_if_another_top_level_note_selected(self):
        assert len(self.notes) >= 2
        self.prepare_tape()

        index = self.tape_widget.proxy_model().index(1, 0)
        self.tape_widget.set_note_selection(index, True)
        assert self.tape_widget.selected_proxy_indexes() == [index]

        self.tape_widget._new_sibling_handler()

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 1)
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 1)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].row(), len(self.notes))
        self.assertEqual(self.tape_widget.get_filter(), '')

    def test_new_sibling_handler_should_add_top_level_note_if_more_than_one_note_selected(self):
        assert len(self.notes) >= 2
        self.prepare_tape()

        index_1 = self.tape_widget.proxy_model().index(1, 0)
        index_2 = self.tape_widget.proxy_model().index(2, 0)
        self.tape_widget.set_note_selection(index_1, True)
        self.tape_widget.set_note_selection(index_2, True)
        assert len(self.tape_widget.selected_proxy_indexes()) == 2
        assert index_1 in self.tape_widget.selected_proxy_indexes()
        assert index_2 in self.tape_widget.selected_proxy_indexes()

        self.tape_widget._new_sibling_handler()

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 1)
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 1)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].row(), len(self.notes))
        self.assertEqual(self.tape_widget.get_filter(), '')

    def test_new_sibling_handler_should_append_new_child_if_lower_level_note_selected(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        parent_note = self.tape_widget.create_empty_note(888)
        self.tape_widget.add_note(parent_note, self.tape_widget.model().item(2).index())

        parent_index = self.tape_widget.proxy_model().mapFromSource(self.tape_widget.model().item(2).child(0).index())
        self.tape_widget.set_note_selection(parent_index, True)
        assert self.tape_widget.selected_proxy_indexes() == [parent_index]

        self.tape_widget._new_sibling_handler()

        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 2)
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 1)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].parent(), parent_index.parent())
        self.assertNotEqual(self.tape_widget.selected_proxy_indexes()[0], parent_index)
        self.assertEqual(self.tape_widget.get_filter(), '')

    def test_add_child_to_selected_element_should_add_child_if_one_parent_selected(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        parent_note = self.tape_widget.create_empty_note(888)
        self.tape_widget.add_note(parent_note, self.tape_widget.model().item(2).index())

        parent_index = self.tape_widget.proxy_model().mapFromSource(self.tape_widget.model().item(2).child(0).index())
        self.tape_widget.set_note_selection(parent_index, True)
        assert self.tape_widget.selected_proxy_indexes() == [parent_index]

        added = self.tape_widget.add_child_to_selected_element()

        self.assertEqual(added, True)
        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes) + 2)
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 1)
        self.assertEqual(self.tape_widget.selected_proxy_indexes()[0].parent(), parent_index)
        self.assertEqual(self.tape_widget.get_filter(), '')

    def test_add_child_to_selected_element_should_not_add_anything_if_nothing_selected(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        added = self.tape_widget.add_child_to_selected_element()

        self.assertEqual(added, False)
        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes))
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 0)
        self.assertEqual(self.tape_widget.get_filter(), '')

    def test_add_child_to_selected_element_should_not_add_anything_and_leave_selection_intact_if_more_than_one_note_selected(self):
        assert len(self.notes) >= 3
        self.prepare_tape()

        index_1 = self.tape_widget.proxy_model().index(1, 0)
        index_2 = self.tape_widget.proxy_model().index(2, 0)
        self.tape_widget.set_note_selection(index_1, True)
        self.tape_widget.set_note_selection(index_2, True)
        assert len(self.tape_widget.selected_proxy_indexes()) == 2
        assert index_1 in self.tape_widget.selected_proxy_indexes()
        assert index_2 in self.tape_widget.selected_proxy_indexes()

        added = self.tape_widget.add_child_to_selected_element()

        self.assertEqual(added, False)
        self.assertEqual(len(list(self.tape_widget.notes())), len(self.notes))
        self.assertEqual(len(self.tape_widget.selected_proxy_indexes()), 2)
        self.assertEqual(self.tape_widget.get_filter(), '')
