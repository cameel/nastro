import unittest
from io         import StringIO
from contextlib import closing
from datetime   import datetime

from ..iterator     import HotlistIterator, LineType, StructuralError
from ..importer     import import_opera_notes, line_strip, MissingNoteAttributes, InvalidAttributeValue, FOLDER_TAG_SEPARATOR
from ....note       import Note
from .test_iterator import NOTE_FILE_FIXTURES

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

    def test_import_opera_notes_should_import_a_well_formed_file(self):
        fixture = NOTE_FILE_FIXTURES[0]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            notes = import_opera_notes(note_file)

        self.assertEqual(len(notes), 2)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(notes[0].title,     "note 1")
        self.assertEqual(notes[0].body,      "")
        self.assertEqual(notes[0].timestamp, datetime(2011, 9, 11, 22, 56, 10))

        self.assertEqual(notes[1].title,     "note 2 title")
        self.assertEqual(notes[1].body,      "note body")
        self.assertEqual(notes[1].timestamp, datetime(2011, 9, 28, 23, 20, 17))

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
            notes = import_opera_notes(note_file)

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "note title")
        self.assertEqual(notes[0].body,  "   note body")

    def test_import_opera_notes_should_not_ignore_notes_with_no_text(self):
        fixture = (
            "#NOTE\n"
            "	ID=386\n"
            "	CREATED=1317244817\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            notes = import_opera_notes(note_file)

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title,     '')
        self.assertEqual(notes[0].body,      '')
        self.assertEqual(notes[0].timestamp, datetime(2011, 9, 28, 23, 20, 17))

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

    def test_import_opera_notes_should_add_folder_paths_as_tags(self):
        fixture = NOTE_FILE_FIXTURES[0]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            notes = import_opera_notes(note_file)

        self.assertEqual(len(notes), 2)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(notes[0].title, "note 1")
        self.assertEqual(notes[0].tags,  ['folder 1/folder 2'])

        self.assertEqual(notes[1].title, "note 2 title")
        self.assertEqual(notes[1].tags,  ['folder 1/folder 2'])

    def test_import_opera_notes_should_detect_folder_end_without_matching_folder(self):
        fixture = NOTE_FILE_FIXTURES[1] + '-\n'

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) < count_folder_ends(fixture)

        with self.assertRaises(StructuralError):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file)

    def test_import_opera_notes_should_add_folders_with_body_as_notes(self):
        fixture = NOTE_FILE_FIXTURES[1]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            notes = import_opera_notes(note_file)

        self.assertEqual(len(notes), 3)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(notes[0].title, "F1")
        self.assertEqual(notes[0].body,  "abc")
        self.assertEqual(notes[0].tags,  ['F1'])

        self.assertEqual(notes[1].title, "N1")
        self.assertEqual(notes[1].body,  "")
        self.assertEqual(notes[1].tags,  ['F1'])

        self.assertEqual(notes[2].title, "N2")
        self.assertEqual(notes[2].body,  "def")
        self.assertEqual(notes[2].tags,  ['F1/F2'])

    def test_import_opera_notes_should_detect_folder_without_matching_end(self):
        fixture = NOTE_FILE_FIXTURES[1][0:-2]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) > count_folder_ends(fixture)

        with self.assertRaises(StructuralError):
            with closing(StringIO(fixture)) as note_file:
                import_opera_notes(note_file)

    def test_import_opera_notes_should_not_escape_or_remove_tag_separators_from_folder_titles(self):
        folder_title = "F1" + FOLDER_TAG_SEPARATOR + "F2"
        note_title   = "N1" + FOLDER_TAG_SEPARATOR + "N2"
        note_body    = "N3" + FOLDER_TAG_SEPARATOR + "N4"

        fixture = (
            "Opera Hotlist version 2.0\n"
            "Options: encoding = utf8, version=3\n"
            "\n"
            "#FOLDER\n"
            "	ID=1\n"
            "	NAME=" + folder_title + "\n"
            "	CREATED=1301917631\n"
            "\n"
            "#NOTE\n"
            "	ID=2\n"
            "	NAME=" + note_title + "\x02\x02" + note_body + "\n"
            "	CREATED=1315774570\n"
            "\n"
            "-\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            notes = import_opera_notes(note_file)

        self.assertEqual(len(notes), 1)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(notes[0].title, note_title)
        self.assertEqual(notes[0].body,  note_body)
        self.assertEqual(notes[0].tags,  [folder_title])

    def test_import_opera_notes_should_skip_notes_inside_trash_folder(self):
        fixture = NOTE_FILE_FIXTURES[2]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with closing(StringIO(fixture)) as note_file:
            notes = import_opera_notes(note_file, skip_trash_folder = True)

        self.assertEqual(len(notes), 2)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(notes[0].title, "N1")
        self.assertEqual(notes[0].tags,  ['F1'])

        self.assertEqual(notes[1].title, "N2")
        self.assertEqual(notes[1].tags,  [''])

    def test_import_opera_notes_should_not_skip_notes_inside_trash_folder_if_requested_not_to(self):
        fixture = NOTE_FILE_FIXTURES[2]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])
        assert count_folder_starts(fixture) == count_folder_ends(fixture)

        with closing(StringIO(fixture)) as note_file:
            notes = import_opera_notes(note_file, skip_trash_folder = False)

        self.assertEqual(len(notes), 5)
        self.assertTrue([isinstance(note, Note) for note in notes])

        self.assertEqual(notes[0].title, "N1")
        self.assertEqual(notes[0].tags,  ['F1'])

        self.assertEqual(notes[1].title, "NT1")
        self.assertEqual(notes[1].tags,  ['F1/T1'])

        self.assertEqual(notes[2].title, "NT2")
        self.assertEqual(notes[2].tags,  ['F1/T1'])

        self.assertEqual(notes[3].title, "NT3")
        self.assertEqual(notes[3].tags,  ['F1/T1/FT1'])

        self.assertEqual(notes[4].title, "N2")
        self.assertEqual(notes[4].tags,  [''])

    def test_import_opera_notes_should_not_detect_invalid_trash_folder_attribute_values(self):
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
