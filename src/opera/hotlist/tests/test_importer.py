import unittest
from io         import StringIO
from contextlib import closing
from datetime   import datetime

from ..iterator     import HotlistIterator
from ..importer     import import_opera_notes, line_strip, MissingNoteAttributes
from ....note       import Note
from .test_iterator import NOTE_FILE_FIXTURES

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

