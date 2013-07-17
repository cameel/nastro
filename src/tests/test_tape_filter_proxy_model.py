import unittest
import sys
from datetime import datetime

from PyQt4.QtTest import QTest
from PyQt4.QtGui  import QStandardItemModel, QStandardItem
from PyQt4.QtCore import Qt

from ..note                    import Note
from ..tape_filter_proxy_model import TapeFilterProxyModel

class TapeFilterProxyModelTest(unittest.TestCase):
    def setUp(self):
        self.source_model            = QStandardItemModel()
        self.tape_filter_proxy_model = TapeFilterProxyModel()

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

        root_item = self.source_model.invisibleRootItem()
        for note in self.notes:
            item = QStandardItem()
            item.setData(note, Qt.EditRole)
            root_item.appendRow(item)

        assert self.source_model.rowCount() == len(self.notes)

        self.tape_filter_proxy_model.setSourceModel(self.source_model)

    def select_note_dicts(self, model, mask = None):
        assert mask == None or model.rowCount() == len(mask)
        assert mask == None or all(bit in [True, False] for bit in mask)

        dicts = []
        for i in range(model.rowCount()):
            if mask == None or mask[i]:
                index = model.index(i, 0)
                dicts.append(model.data(index).to_dict())

        return dicts

    def test_unfiltered_model_should_contain_all_notes(self):
        mask = [True, True, True, True]
        self.assertEqual(self.select_note_dicts(self.tape_filter_proxy_model), self.select_note_dicts(self.source_model, mask))

    def test_filtered_model_should_contain_all_notes_if_searching_for_empty_string(self):
        self.tape_filter_proxy_model.setFilterFixedString('')

        mask = [True, True, True, True]
        self.assertEqual(self.select_note_dicts(self.tape_filter_proxy_model), self.select_note_dicts(self.source_model, mask))

    def test_filtered_model_should_contain_only_matching_notes(self):
        keyword = 'B'

        assert keyword in self.notes[1].body
        assert not keyword.lower() in self.notes[0].body.lower()
        assert not keyword.lower() in self.notes[2].body.lower()
        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[0:3])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:3])

        self.tape_filter_proxy_model.setFilterFixedString(keyword)

        mask = [False, True, False, True]
        self.assertEqual(self.select_note_dicts(self.tape_filter_proxy_model), self.select_note_dicts(self.source_model, mask))

    def test_filtered_model_should_treat_fixed_string_as_case_insensitive(self):
        keyword = 'B'

        assert keyword         != keyword.lower()
        assert keyword         in self.notes[1].body
        assert keyword.lower() in self.notes[3].body
        assert not keyword.lower() in self.notes[0].body.lower()
        assert not keyword.lower() in self.notes[2].body.lower()
        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[0:4])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:4])

        self.tape_filter_proxy_model.setFilterFixedString(keyword)

        mask = [False, True, False, True]
        self.assertEqual(self.select_note_dicts(self.tape_filter_proxy_model), self.select_note_dicts(self.source_model, mask))

    def test_filtered_model_should_contain_items_with_matching_titles(self):
        keyword = 'X'

        assert keyword in self.notes[0].title
        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[1:4])
        assert all(keyword.lower() not in note.body.lower()                 for note in self.notes[0:4])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:4])

        self.tape_filter_proxy_model.setFilterFixedString(keyword)

        mask = [True, False, False, False]
        self.assertEqual(self.select_note_dicts(self.tape_filter_proxy_model), self.select_note_dicts(self.source_model, mask))

    def test_filtered_model_should_contain_items_with_matching_tags(self):
        keyword = 'III'

        assert all(keyword.lower() not in note.title.lower()                for note in self.notes[0:4])
        assert all(keyword.lower() not in note.body.lower()                 for note in self.notes[0:4])
        assert all(keyword.lower() not in Note.join_tags(note.tags).lower() for note in self.notes[0:3])
        assert keyword.lower() in self.notes[3].tags[1].lower()

        self.tape_filter_proxy_model.setFilterFixedString(keyword)

        mask = [False, False, False, True]
        self.assertEqual(self.select_note_dicts(self.tape_filter_proxy_model), self.select_note_dicts(self.source_model, mask))

    def test_filtered_model_should_only_contain_notes_with_exactly_matching_whitespace(self):
        keyword = 'PPP RRR'

        assert all(keyword.lower() not in note.title.lower() for note in self.notes[0:4])
        assert all(keyword.lower() not in note.body.lower()  for note in self.notes[0:4])
        assert 'PPP RRR'  in self.notes[1].tags[1]
        assert 'PPP\tRRR' in self.notes[2].tags[1]

        self.tape_filter_proxy_model.setFilterFixedString(keyword)

        mask = [False, True, False, False]
        self.assertEqual(self.select_note_dicts(self.tape_filter_proxy_model), self.select_note_dicts(self.source_model, mask))
