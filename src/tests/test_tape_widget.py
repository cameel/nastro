import unittest
import sys
from datetime import datetime, timedelta

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QApplication

from ..tape_widget import TapeWidget
from ..note        import Note
from ..note_widget import NoteWidget

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

    def test_note_should_return_note_at_specified_index(self):
        for note in self.notes:
            self.tape_widget.add_note(note)

        for (i, note) in enumerate(self.notes):
            self.assertEqual(self.tape_widget.note(i), note)

    def test_note_count_should_return_the_number_of_notes(self):
        self.assertEqual(self.tape_widget.note_count(), 0)

        for note in self.notes:
            self.tape_widget.add_note(note)

        self.assertEqual(self.tape_widget.note_count(), len(self.notes))

    def test_notes_should_enumerate_all_notes_in_the_same_order_as_note(self):
        with self.assertRaises(StopIteration):
            next(self.tape_widget.notes())

        for note in self.notes:
            self.tape_widget.add_note(note)

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
        assert self.tape_widget.note_count() == 0

        for note in self.notes[0:3]:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == 3

        self.tape_widget.remove_note(self.notes[1])

        self.assertEqual(self.tape_widget.note_count(), 2)
        self.assertEqual(self.tape_widget.note(0), self.notes[0])
        self.assertEqual(self.tape_widget.note(1), self.notes[2])

    def test_remove_note_should_do_nothing_if_note_not_found(self):
        assert self.tape_widget.note_count() == 0

        for note in self.notes[0:2]:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == 2

        self.tape_widget.remove_note(self.notes[2])

        self.assertEqual(self.tape_widget.note_count(), 2)
        self.assertEqual(self.tape_widget.note(0), self.notes[0])
        self.assertEqual(self.tape_widget.note(1), self.notes[1])

    def test_search_should_find_matching_notes(self):
        keyword = 'B'

        assert self.tape_widget.note_count() == 0
        assert keyword in self.notes[1].body
        assert not keyword.lower() in self.notes[0].body.lower()
        assert not keyword.lower() in self.notes[2].body.lower()
        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[0:3])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:3])

        for note in self.notes[0:3]:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == 3

        mask = self.tape_widget.search(keyword)

        self.assertEqual(mask, [False, True, False])

    def test_search_should_be_case_insensitive(self):
        keyword = 'B'

        assert self.tape_widget.note_count() == 0
        assert keyword         != keyword.lower()
        assert keyword         in self.notes[1].body
        assert keyword.lower() in self.notes[3].body
        assert not keyword.lower() in self.notes[0].body.lower()
        assert not keyword.lower() in self.notes[2].body.lower()
        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[0:4])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:4])

        for note in self.notes[0:4]:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == 4

        mask = self.tape_widget.search(keyword)

        self.assertEqual(mask, [False, True, False, True])

    def test_search_should_look_in_titles(self):
        keyword = 'X'

        assert self.tape_widget.note_count() == 0
        assert keyword in self.notes[0].title
        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[1:4])
        assert all(keyword.lower() not in note.body.lower()                 for note in self.notes[0:4])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:4])

        for note in self.notes[0:4]:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == 4

        mask = self.tape_widget.search(keyword)

        self.assertEqual(mask, [True, False, False, False])

    def test_search_should_look_in_tags(self):
        keyword = 'III'

        assert self.tape_widget.note_count() == 0
        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[0:4])
        assert all(keyword.lower() not in note.body.lower()                 for note in self.notes[0:4])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:3])
        assert keyword.lower() in self.notes[3].tags[1].lower()

        for note in self.notes[0:4]:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == 4

        mask = self.tape_widget.search(keyword)

        self.assertEqual(mask, [False, False, False, True])

    def test_search_should_not_ignore_whitespace(self):
        keyword = 'PPP RRR'

        assert self.tape_widget.note_count() == 0
        assert all(keyword.lower() not in note.title.lower() for note in self.notes[0:4])
        assert all(keyword.lower() not in note.body.lower()  for note in self.notes[0:4])
        assert 'PPP RRR'  in self.notes[1].tags[1]
        assert 'PPP\tRRR' in self.notes[2].tags[1]

        for note in self.notes[0:4]:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == 4

        mask = self.tape_widget.search(keyword)

        self.assertEqual(mask, [False, True, False, False])

    def test_search_should_return_all_notes_if_searching_for_empty_text(self):
        keyword = ''

        assert self.tape_widget.note_count() == 0

        for note in self.notes:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == len(self.notes)

        mask = self.tape_widget.search(keyword)

        self.assertEqual(mask, [True for note in self.notes])

    """
    def test_search_handler_should_hide_non_matching_notes(self):
        keyword = 'B'

        assert self.tape_widget.note_count() == 0
        assert keyword in self.notes[1].body
        assert not keyword.lower() in self.notes[0].body.lower()
        assert not keyword.lower() in self.notes[2].body.lower()
        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[0:3])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:3])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:3])

        for note in self.notes[0:3]:
            self.tape_widget.add_note(note)
        assert self.tape_widget.note_count() == 3

        self.tape_widget.show()
        assert all(note_widget.isVisible() for note_widget in self.tape_widget._note_widgets)

        self.tape_widget.search_handler(keyword)
        assert self.tape_widget.search(keyword) == [False, True, False]

        self.assertEqual(self.tape_widget.note_count(), 3)
        self.assertTrue(not self.tape_widget._note_widgets[0].isVisible())
        self.assertTrue(    self.tape_widget._note_widgets[1].isVisible())
        self.assertTrue(not self.tape_widget._note_widgets[2].isVisible())
    """

    def test_dump_notes_should_dump_all_notes_as_dicts(self):
        for note in self.notes:
            self.tape_widget.add_note(note)

        dump = self.tape_widget.dump_notes()

        self.assertEqual(len(dump), len(self.notes))
        for (dumped_note, note) in zip(dump, self.notes):
            # NOTE: Intentionally not checking all properties. Don't want to sync this every time one is added.
            self.assertEqual(dumped_note['title'], note.title)
            self.assertEqual(dumped_note['body'],  note.body)
