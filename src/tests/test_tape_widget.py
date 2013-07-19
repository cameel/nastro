import unittest
import sys
from datetime import datetime, timedelta

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QApplication, QItemSelection, QItemSelectionModel
from PyQt4.QtCore import QRegExp

from ..tape_widget             import TapeWidget
from ..note                    import Note
from ..note_edit               import NoteEdit
from ..tape_filter_proxy_model import TapeFilterProxyModel

class TapeWidgetTest(unittest.TestCase):
    def setUp(self):
        self.application = QApplication(sys.argv)
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

    def tearDown(self):
        # FIXME: Python crashes without this. Probably unittest does not destroy the old instance of the
        # class before creating a new one and PyQt does not like having two instances of QApplication?
        self.application = None

    def prepare_tape(self, index_sequence = None):
        if index_sequence == None:
            index_sequence = range(len(self.notes))

        for i in index_sequence:
            self.tape_widget.add_note(self.notes[i])

        assert self.tape_widget.note_count() == len(index_sequence)

    def test_note_should_return_note_at_specified_index(self):
        self.prepare_tape()

        for (i, note) in enumerate(self.notes):
            self.assertEqual(self.tape_widget.note(i), note)

    def test_note_count_should_return_the_number_of_notes(self):
        self.assertEqual(self.tape_widget.note_count(), 0)

        self.prepare_tape()

        self.assertEqual(self.tape_widget.note_count(), len(self.notes))

    def test_notes_should_enumerate_all_notes_in_the_same_order_as_note(self):
        with self.assertRaises(StopIteration):
            next(self.tape_widget.notes())

        self.prepare_tape()

        for (i, note) in enumerate(self.tape_widget.notes()):
            self.assertEqual(note, self.tape_widget.note(i))

    def test_add_note_should_create_a_new_note(self):
        assert self.tape_widget.note_count() == 0

        self.tape_widget.add_note()

        self.assertEqual(self.tape_widget.note_count(), 1)

        note = self.tape_widget.note(0)
        assert isinstance(note, Note)

        self.assertEqual(note.title, 'Note 1')
        self.assertEqual(note.body,  '')
        self.assertEqual(note.tags,  [])

        # ASSUMPTION: This test executes in much less than 10 seconds.
        self.assertTrue(note.created_at > datetime.utcnow() - timedelta(0, 10))
        self.assertEqual(note.created_at, note.modified_at)

    def test_add_note_should_add_existing_note(self):
        assert self.tape_widget.note_count() == 0

        self.tape_widget.add_note(self.notes[0])

        self.assertEqual(self.tape_widget.note_count(), 1)
        self.assertEqual(self.tape_widget.note(0), self.notes[0])

    def test_add_note_should_append_notes_at_the_end_of_the_tape(self):
        assert self.tape_widget.note_count() == 0

        self.tape_widget.add_note(self.notes[0])
        self.tape_widget.add_note()
        self.tape_widget.add_note(self.notes[1])

        self.assertEqual(self.tape_widget.note_count(), 3)
        self.assertEqual(self.tape_widget.note(0), self.notes[0])
        self.assertEqual(self.tape_widget.note(2), self.notes[1])

    def test_remove_note_should_remove_existing_note_from_the_tape(self):
        self.prepare_tape(range(3))

        self.tape_widget.remove_note(self.notes[1])

        self.assertEqual(self.tape_widget.note_count(), 2)
        self.assertEqual(self.tape_widget.note(0), self.notes[0])
        self.assertEqual(self.tape_widget.note(1), self.notes[2])

    def test_remove_note_should_do_nothing_if_note_not_found(self):
        self.prepare_tape(range(2))

        self.tape_widget.remove_note(self.notes[2])

        self.assertEqual(self.tape_widget.note_count(), 2)
        self.assertEqual(self.tape_widget.note(0), self.notes[0])
        self.assertEqual(self.tape_widget.note(1), self.notes[1])

    def test_by_default_all_notes_should_be_visible(self):
        assert self.tape_widget.get_filter() == ''

        self.prepare_tape(range(3))

        self.assertEqual(self.tape_widget.note_count(), 3)
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

        self.assertEqual(self.tape_widget.note_count(), 3)
        self.assertEqual(self.tape_widget._tape_filter_proxy_model.rowCount(), 1)
        self.assertEqual(self.tape_widget._tape_filter_proxy_model.data(self.tape_widget._tape_filter_proxy_model.index(0, 0)).to_dict(), self.notes[1].to_dict())

    def test_dump_notes_should_dump_all_notes_as_dicts(self):
        self.prepare_tape()

        dump = self.tape_widget.dump_notes()

        self.assertEqual(len(dump), len(self.notes))
        for (dumped_note, note) in zip(dump, self.notes):
            # NOTE: Intentionally not checking all properties. Don't want to sync this every time one is added.
            self.assertEqual(dumped_note['title'], note.title)
            self.assertEqual(dumped_note['body'],  note.body)

    def test_delete_note_handler_should_do_nothing_if_nothing_is_selected(self):
        self.prepare_tape()

        assert len(self.tape_widget._note_list_view.selectedIndexes()) == 0

        self.tape_widget._delete_note_handler()

        self.assertEqual(self.tape_widget.note_count(), len(self.notes))

    def test_delete_note_handler_should_delete_selected_note(self):
        assert len(self.notes) >= 2
        self.prepare_tape()

        index = self.tape_widget._tape_filter_proxy_model.index(1, 0)

        self.tape_widget._note_list_view.selectionModel().select(QItemSelection(index, index), QItemSelectionModel.Select)
        assert len(self.tape_widget._note_list_view.selectedIndexes()) == 1

        self.tape_widget._delete_note_handler()

        self.assertEqual(self.tape_widget.note_count(), len(self.notes) - 1)
