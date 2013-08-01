import unittest
from io         import StringIO
from contextlib import closing
from datetime   import datetime

from ..iterator             import HotlistIterator, LineType, StructuralError
from ..importer             import import_opera_notes, line_strip, tree_validating_iterator, trash_aware_hotlist_iterator
from ..importer             import MissingNoteAttributes, InvalidAttributeValue
from ....note               import Note
from ....utils              import localtime_to_utc
from ....note_model_helpers import all_notes
from .test_iterator         import NOTE_FILE_FIXTURES

def count_folder_starts(note_file_content):
    num_folder_starts = 0
    for line in note_file_content.splitlines():
        line_info          = HotlistIterator.parse_hotlist_line(line)
        num_folder_starts += line_info['type'] == LineType.ELEMENT and line_info['name'] == 'FOLDER'

    return num_folder_starts

def count_folder_ends(note_file_content):
    num_folder_ends = 0
    for line in note_file_content.splitlines():
        line_info        = HotlistIterator.parse_hotlist_line(line)
        num_folder_ends += line_info['type'] == LineType.END

    return num_folder_ends

class HotlistImporterTest(unittest.TestCase):
    def test_line_strip_should_strip_leading_and_trailing_empty_lines(self):
        leading_whitespace = (
            "\n"
            "     \n"
            "\t\n"
            "\t   \t\n"
            "\n"
            "\n"
        )
        body = (
            "a line\n"
            "next line\n"
            "next line\n"
            "\n"
            "     \n"
            "\t\n"
            "\tnext line\n"
            "\n"
            "     next line"
        )
        trailing_whitespace = (
            "\n"
            "     \n"
            "\t\n"
            "\t   \t\n"
            "\n"
            "\n"
        )
        text = leading_whitespace + body + trailing_whitespace

        stripped_text = line_strip(text)

        self.assertEqual(stripped_text, body)

    def test_line_strip_should_not_strip_leading_intentation(self):
        leading_whitespace = (
            "\n"
            "   \n"
            "    \n"
        )
        body = (
            "    a line\n"
            "  next line\n"
            "\tnext line\n"
            "\n"
            "     \n"
            "\t\n"
            "\tnext line\n"
            "\n"
            "     next line"
        )
        trailing_whitespace = (
            "\n"
            "     \n"
        )
        text = leading_whitespace + body + trailing_whitespace

        stripped_text = line_strip(text)

        self.assertEqual(stripped_text, body)

    def test_line_strip_should_return_empty_string_if_theres_only_whitespace(self):
        text = (
            "\n"
            "     \n"
            "\t\n"
            "\t   \t\n"
            "\n"
            "\n"
        )

        stripped_text = line_strip(text)

        self.assertEqual(stripped_text, '')

    def test_tree_validating_iterator_should_enumerate_elements_from_a_well_formed_file(self):
        fixture = NOTE_FILE_FIXTURES[0]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            input_elements = list(HotlistIterator(note_file))

        output_tuples = list(tree_validating_iterator(input_elements))

        self.assertEqual(len(output_tuples), len(input_elements))
        self.assertEqual([element for element, level in output_tuples], input_elements)
        self.assertEqual([level   for element, level in output_tuples], [0, 1, 2, 2, 2, 1, 0])

    def test_tree_validating_iterator_should_detect_folder_end_without_matching_folder(self):
        fixture = NOTE_FILE_FIXTURES[1] + '-\n'

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) < count_folder_ends(fixture)

        with self.assertRaises(StructuralError):
            with closing(StringIO(fixture)) as note_file:
                list(tree_validating_iterator(HotlistIterator(note_file)))

    def test_tree_validating_iterator_should_detect_folder_without_matching_end(self):
        fixture = NOTE_FILE_FIXTURES[1][0:-2]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) > count_folder_ends(fixture)

        with self.assertRaises(StructuralError):
            with closing(StringIO(fixture)) as note_file:
                list(tree_validating_iterator(HotlistIterator(note_file)))

    def test_trash_aware_hotlist_iterator_should_enumerate_elements_from_a_well_formed_file(self):
        fixture = NOTE_FILE_FIXTURES[0]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            input_tuples = list(tree_validating_iterator(HotlistIterator(note_file)))
            assert len(input_tuples) == 7

        output_tuples = list(trash_aware_hotlist_iterator(input_tuples))

        self.assertEqual(len(output_tuples), len(input_tuples))
        self.assertEqual([(element, level) for element, level, in_trash_folder in output_tuples], input_tuples)
        self.assertEqual([in_trash_folder  for element, level, in_trash_folder in output_tuples], [False, False, False, False, False, False, False])

    def test_trash_aware_hotlist_iterator_should_mark_notes_inside_trash_folder(self):
        fixture = NOTE_FILE_FIXTURES[2]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with closing(StringIO(fixture)) as note_file:
            input_tuples = list(tree_validating_iterator(HotlistIterator(note_file)))

        output_tuples = list(trash_aware_hotlist_iterator(input_tuples))

        self.assertEqual(len(output_tuples), len(input_tuples))
        self.assertEqual([(element, level)  for element, level, in_trash_folder in output_tuples], input_tuples)
        self.assertEqual(
            [in_trash_folder for element, level, in_trash_folder in output_tuples],
            [False, False, True, True, True, True, True, True, True, True, True, False, False]
        )

    def test_trash_aware_hotlist_iterator_should_detect_invalid_trash_folder_attribute_values(self):
        fixture = (
            "#FOLDER\n"
            "	ID=1\n"
            "	NAME=T1\n"
            "	CREATED=1301917631\n"
            "	TRASH FOLDER=NEIN\n"
            "-\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with closing(StringIO(fixture)) as note_file:
            input_tuples = list(tree_validating_iterator(HotlistIterator(note_file)))

        with self.assertRaises(InvalidAttributeValue):
            list(trash_aware_hotlist_iterator(input_tuples))

    def test_trash_aware_hotlist_iterator_should_detect_nested_trash_folders(self):
        fixture = (
            "#FOLDER\n"
            "	ID=1\n"
            "	NAME=T1\n"
            "	CREATED=1301917631\n"
            "	TRASH FOLDER=YES\n"
            "#FOLDER\n"
            "	ID=2\n"
            "	NAME=T2\n"
            "	CREATED=1301917631\n"
            "	TRASH FOLDER=YES\n"
            "-\n"
            "-\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with closing(StringIO(fixture)) as note_file:
            input_tuples = list(tree_validating_iterator(HotlistIterator(note_file)))

        with self.assertRaises(StructuralError):
            list(trash_aware_hotlist_iterator(input_tuples))

    def test_import_opera_notes_should_import_a_well_formed_file(self):
        fixture = NOTE_FILE_FIXTURES[0]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            model = import_opera_notes(note_file)
            notes = list(all_notes(model))

        self.assertEqual(len(notes), 4)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.item(0).rowCount(), 1)
        self.assertEqual(model.item(0).child(0).rowCount(), 2)
        self.assertEqual(model.item(0).child(0).child(0).rowCount(), 0)
        self.assertEqual(model.item(0).child(0).child(1).rowCount(), 0)

        # NOTE: Opera stores timestamps in localtime and the importer has to guess the time zone
        # to convert it to UTC (which we're using internally). It assumes that it's the one we're
        # using on this machine. This means that the expected timestamp depends on our geographical
        # location. To prevent the test from failing on a different machine we have to convert it from
        # localtime rather than just hard-code UTC value.
        self.assertEqual(notes[0].body,        "folder 1")
        self.assertEqual(notes[0].created_at,  localtime_to_utc(datetime(2011, 4, 4, 13, 47, 11)))
        self.assertEqual(notes[0].modified_at, notes[0].created_at)

        self.assertEqual(notes[1].body,        "folder 2")
        self.assertEqual(notes[1].created_at,  localtime_to_utc(datetime(2011, 10, 1, 23, 36, 32)))
        self.assertEqual(notes[1].modified_at, notes[1].created_at)

        self.assertEqual(notes[2].body,        "note 1")
        self.assertEqual(notes[2].created_at,  localtime_to_utc(datetime(2011, 9, 11, 22, 56, 10)))
        self.assertEqual(notes[2].modified_at, notes[2].created_at)

        self.assertEqual(notes[3].body,        "note 2 title\n\nnote body")
        self.assertEqual(notes[3].created_at,  localtime_to_utc(datetime(2011, 9, 28, 23, 20, 17)))
        self.assertEqual(notes[3].modified_at, notes[3].created_at)

    def test_import_opera_notes_should_strip_leading_empty_lines_and_trailing_whitespace_from_note_body(self):
        fixture = (
            "#NOTE\n"
            "	ID=386\n"
            "	NAME=note title\x02\x02\x02\x02  \x02\x02\t\x02\x02   note body\t    \x02\x02\x02\x02  \x02\x02\t\x02\x02   \n"
            "	CREATED=1301917631\n"
            "	EXPANDED=YES\n"
            "	UNIQUEID=4710F1B05EB111E0881E839B765D815D\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            model = import_opera_notes(note_file)
            notes = list(all_notes(model))

        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(len(notes),       1)
        self.assertEqual(notes[0].body, "note title\n\n  \n\t\n   note body")

    def test_import_opera_notes_should_not_ignore_notes_with_no_text(self):
        fixture = (
            "#NOTE\n"
            "	ID=386\n"
            "	CREATED=1317244817\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            model = import_opera_notes(note_file)
            notes = list(all_notes(model))

        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(len(notes),       1)
        self.assertEqual(notes[0].body,        '')
        self.assertEqual(notes[0].created_at,  localtime_to_utc(datetime(2011, 9, 28, 23, 20, 17)))
        self.assertEqual(notes[0].modified_at, notes[0].created_at)

    def test_import_opera_notes_should_detect_missing_timestamp(self):
        fixture = (
            "#NOTE\n"
            "	ID=386\n"
            "	NAME=note\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with self.assertRaises(MissingNoteAttributes):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file)

    def test_import_opera_notes_should_detect_missing_timestamp_in_notes_with_no_text(self):
        fixture = (
            "#NOTE\n"
            "	ID=386\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with self.assertRaises(MissingNoteAttributes):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file)

    def test_import_opera_notes_should_detect_folder_end_without_matching_folder(self):
        fixture = NOTE_FILE_FIXTURES[1] + '-\n'

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) < count_folder_ends(fixture)

        with self.assertRaises(StructuralError):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file)

    def test_import_opera_notes_should_add_folders_as_parent_notes(self):
        fixture = NOTE_FILE_FIXTURES[1]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            model = import_opera_notes(note_file)
            notes = list(all_notes(model))

        self.assertEqual(len(notes), 4)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.item(0).rowCount(), 2)
        self.assertEqual(model.item(0).child(0).rowCount(), 0)
        self.assertEqual(model.item(0).child(1).rowCount(), 1)
        self.assertEqual(model.item(0).child(1).child(0).rowCount(), 0)

        self.assertEqual(notes[0].body,  "F1\nabc")
        self.assertEqual(notes[0].tags,  [])

        self.assertEqual(notes[1].body,  "N1")
        self.assertEqual(notes[1].tags,  [])

        self.assertEqual(notes[2].body,  "F2")
        self.assertEqual(notes[2].tags,  [])

        self.assertEqual(notes[3].body,  "N2\ndef")
        self.assertEqual(notes[3].tags,  [])

    def test_import_opera_notes_should_detect_folder_without_matching_end(self):
        fixture = NOTE_FILE_FIXTURES[1][0:-2]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) > count_folder_ends(fixture)

        with self.assertRaises(StructuralError):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file)

    def test_import_opera_notes_should_not_create_empty_tags_for_top_level_folder(self):
        fixture = (
            "#NOTE\n"
            "	NAME=x\n"
            "	CREATED=1315774570\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            model = import_opera_notes(note_file)
            notes = list(all_notes(model))

        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(len(notes),       1)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(notes[0].tags, [])

    def test_import_opera_notes_should_skip_notes_inside_trash_folder(self):
        fixture = NOTE_FILE_FIXTURES[2]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with closing(StringIO(fixture)) as note_file:
            model = import_opera_notes(note_file, skip_trash_folder = True)
            notes = list(all_notes(model))

        self.assertEqual(len(notes), 3)

        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.item(0).rowCount(), 1)
        self.assertEqual(model.item(0).child(0).rowCount(), 0)
        self.assertEqual(model.item(1).rowCount(), 0)

        self.assertTrue([isinstance(note, Note) for note in notes])
        self.assertTrue([len(note.tags) == 0    for note in notes])
        self.assertEqual([note.body for note in notes], ["F1", "N1", "N2"])

    def test_import_opera_notes_should_not_skip_notes_inside_trash_folder_if_requested_not_to(self):
        fixture = NOTE_FILE_FIXTURES[2]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with closing(StringIO(fixture)) as note_file:
            model = import_opera_notes(note_file, skip_trash_folder = False)
            notes = list(all_notes(model))

        self.assertEqual(len(notes), 9)

        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.item(0).rowCount(), 2)
        self.assertEqual(model.item(0).child(0).rowCount(), 0)
        self.assertEqual(model.item(0).child(1).rowCount(), 4)
        self.assertEqual(model.item(0).child(1).child(0).rowCount(), 0)
        self.assertEqual(model.item(0).child(1).child(1).rowCount(), 0)
        self.assertEqual(model.item(0).child(1).child(2).rowCount(), 0)
        self.assertEqual(model.item(0).child(1).child(3).rowCount(), 1)
        self.assertEqual(model.item(0).child(1).child(3).child(0).rowCount(), 0)
        self.assertEqual(model.item(1).rowCount(), 0)

        self.assertTrue([isinstance(note, Note) for note in notes])
        self.assertTrue([len(note.tags) == 0    for note in notes])
        self.assertEqual(
            [note.body for note in notes],
            ["F1", "N1", "T1", "NT1", "NT2", "FT1", "FT2", "NT3", "N2"]
        )

    def test_import_opera_notes_should_detect_invalid_trash_folder_attribute_values(self):
        fixture = (
            "#FOLDER\n"
            "	ID=1\n"
            "	NAME=T1\n"
            "	CREATED=1301917631\n"
            "	TRASH FOLDER=NEIN\n"
            "-\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with self.assertRaises(InvalidAttributeValue):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file, skip_trash_folder = True)

        with self.assertRaises(InvalidAttributeValue):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file, skip_trash_folder = False)

    def test_import_opera_notes_should_detect_nested_trash_folders(self):
        fixture = (
            "#FOLDER\n"
            "	ID=1\n"
            "	NAME=T1\n"
            "	CREATED=1301917631\n"
            "	TRASH FOLDER=YES\n"
            "#FOLDER\n"
            "	ID=2\n"
            "	NAME=T2\n"
            "	CREATED=1301917631\n"
            "	TRASH FOLDER=YES\n"
            "-\n"
            "-\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with self.assertRaises(StructuralError):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file, skip_trash_folder = True)

        with self.assertRaises(StructuralError):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file, skip_trash_folder = False)
