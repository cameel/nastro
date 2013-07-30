import unittest
from io         import StringIO
from contextlib import closing

from ..iterator import HotlistIterator, LineType, DuplicateAttribute, InvalidLine, StructuralError

NOTE_FILE_FIXTURES = [
    (
        "Opera Hotlist version 2.0\n"
        "Options: encoding = utf8, version=3\n"
        "\n"
        "#FOLDER\n"
        "	ID=386\n"
        "	NAME=folder 1\n"
        "	CREATED=1301917631\n"
        "	EXPANDED=YES\n"
        "	UNIQUEID=4710F1B05EB111E0881E839B765D815D\n"
        "\n"
        "#FOLDER\n"
        "	ID=388\n"
        "	NAME=folder 2\n"
        "	CREATED=1317504992\n"
        "	UNIQUEID=6DEECC10EC7511E0866BFCFEA00A66EC\n"
        "\n"
        "#NOTE\n"
        "	ID=389\n"
        "	UNIQUEID=7A622360DCB811E095CBF98131828EE4\n"
        "	NAME=note 1\n"
        "	CREATED=1315774570\n"
        "\n"
        # Yeah, it's actually called 'SEPERATOR' by Opera
        "#SEPERATOR\n"
        "	ID=1718\n"
        "	UNIQUEID=00864980724711E0866DB9FAAEFC5346\n"
        "\n"
        "#NOTE\n"
        "	ID=390\n"
        "	UNIQUEID=A9C9FFD0EA1711E087A2D913B5105712\n"
        "	NAME=note 2 title\02\02\02\02note body\n"
        "	CREATED=1317244817\n"
        "\n"
        "\n"
        "-\n"
        "\n"
        "-\n"
    ),
    (
        "Opera Hotlist version 2.0\n"
        "Options: encoding = utf8, version=3\n"
        "\n"
        "#FOLDER\n"
        "	ID=1\n"
        "	NAME=F1\02\02abc\n"
        "	CREATED=1301917631\n"
        "\n"
        "#NOTE\n"
        "	ID=2\n"
        "	NAME=N1\n"
        "	CREATED=1315774570\n"
        "\n"
        "#FOLDER\n"
        "	ID=3\n"
        "	NAME=F2\n"
        "	CREATED=1317504992\n"
        "\n"
        "#NOTE\n"
        "	ID=4\n"
        "	NAME=N2\02\02def\n"
        "	CREATED=1315774570\n"
        "\n"
        "\n"
        "-\n"
        "\n"
        "-\n"
    ),
    (
        "Opera Hotlist version 2.0\n"
        "Options: encoding = utf8, version=3\n"
        "\n"
        "#FOLDER\n"
        "	ID=1\n"
        "	NAME=F1\n"
        "	CREATED=1301917631\n"
        "#NOTE\n"
        "	ID=2\n"
        "	NAME=N1\n"
        "	CREATED=1315774570\n"
        "#FOLDER\n"
        "	ID=3\n"
        "	NAME=T1\n"
        "	CREATED=1317504992\n"
        "	TRASH FOLDER=YES\n"
        "#NOTE\n"
        "	ID=4\n"
        "	NAME=NT1\n"
        "	CREATED=1315774570\n"
        "#NOTE\n"
        "	ID=5\n"
        "	NAME=NT2\n"
        "	CREATED=1315774570\n"
        "#FOLDER\n"
        "	ID=6\n"
        "	NAME=FT1\n"
        "	CREATED=1301917631\n"
        "-\n"
        "#FOLDER\n"
        "	ID=7\n"
        "	NAME=FT2\n"
        "	CREATED=1301917631\n"
        "#NOTE\n"
        "	ID=8\n"
        "	NAME=NT3\n"
        "	CREATED=1315774570\n"
        "-\n"
        "-\n"
        "-\n"
        "#NOTE\n"
        "	ID=9\n"
        "	NAME=N2\n"
        "	CREATED=1315774570\n"
    )
]

class HotlistIteratorTest(unittest.TestCase):
    def test_element_iterator_should_iterate_over_notes_in_a_well_formed_file(self):
        fixture = NOTE_FILE_FIXTURES[0]

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] != None for line in fixture.splitlines()])

        notes = []
        with closing(StringIO(fixture)) as note_file:
            iterator = HotlistIterator(note_file)
            for note_info in iterator:
                notes.append(note_info)

        self.assertEqual(len(notes), 7)
        self.assertEqual(notes[0], ('FOLDER', {
            'ID':       '386',
            'NAME':     "folder 1",
            'CREATED':  '1301917631',
            'EXPANDED': 'YES',
            'UNIQUEID': '4710F1B05EB111E0881E839B765D815D'
        }))
        self.assertEqual(notes[1], ('FOLDER', {
            'ID':       '388',
            'NAME':     "folder 2",
            'CREATED':  '1317504992',
            'UNIQUEID': '6DEECC10EC7511E0866BFCFEA00A66EC'
        }))
        self.assertEqual(notes[2], ('NOTE', {
            'ID':       '389',
            'NAME':     "note 1",
            'CREATED':  '1315774570',
            'UNIQUEID': '7A622360DCB811E095CBF98131828EE4'
        }))
        self.assertEqual(notes[3], ('SEPERATOR', {
            'ID':       '1718',
            'UNIQUEID': '00864980724711E0866DB9FAAEFC5346'
        }))
        self.assertEqual(notes[4], ('NOTE', {
            'ID':       '390',
            'NAME':     "note 2 title\02\02\02\02note body",
            'CREATED':  '1317244817',
            'UNIQUEID': 'A9C9FFD0EA1711E087A2D913B5105712'
        }))
        self.assertEqual(notes[5], "end")
        self.assertEqual(notes[6], "end")

    def test_element_iterator_should_detect_invalid_lines(self):
        fixture = (
            "Opera Hotlist version 2.0\n"
            "Options: encoding = utf8, version=3\n"
            "\n"
            "#FOLDER\n"
            "	ID=386\n"
            "***********************\n"
            "	CREATED=1301917631\n"
            "	EXPANDED=YES\n"
            "	UNIQUEID=4710F1B05EB111E0881E839B765D815D\n"
        )

        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[5])['type'] == None

        with closing(StringIO(fixture)) as note_file:
            with self.assertRaises(InvalidLine):
                iterator = HotlistIterator(note_file)
                for note_info in iterator:
                    pass

    def test_element_iterator_should_detect_attributes_outside_elements(self):
        fixture = (
            "Opera Hotlist version 2.0\n"
            "Options: encoding = utf8, version=3\n"
            "\n"
            "	ID=386\n"
            "#FOLDER\n"
        )

        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[3])['type'] == LineType.ATTRIBUTE
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[4])['type'] == LineType.ELEMENT

        with closing(StringIO(fixture)) as note_file:
            with self.assertRaises(StructuralError):
                iterator = HotlistIterator(note_file)
                for note_info in iterator:
                    pass
    def test_read_element_attributes_should_extract_attributes_correctly_given_only_attribute_lines(self):
        fixture = (
            "	ID=413\n"
            "	UNIQUEID=BCDBB060953E11E0A3A8D585C4226479\n"
            "	NAME=note content\02\02\02\02next line\n"
            "	CREATED=1307915751"
        )
        expected_attributes = {
            'ID':       '413',
            'UNIQUEID': 'BCDBB060953E11E0A3A8D585C4226479',
            'NAME':     "note content\02\02\02\02next line",
            'CREATED':  '1307915751'
        }

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] == LineType.ATTRIBUTE for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            (attributes, next_line) = HotlistIterator.read_element_attributes('NOTE', note_file)

            self.assertEqual(next_line, '')
            self.assertEqual(attributes, expected_attributes)
            self.assertEqual(note_file.tell(), len(fixture))

    def test_read_element_attributes_should_skip_leading_empty_lines(self):
        fixture = (
            "\n"
            "	\n"
            "	ID=413\n"
        )
        expected_attributes = {
            'ID': '413'
        }

        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[0])['type'] == LineType.EMPTY
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[1])['type'] == LineType.EMPTY
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[2])['type'] == LineType.ATTRIBUTE

        with closing(StringIO(fixture)) as note_file:
            (attributes, next_line) = HotlistIterator.read_element_attributes('NOTE', note_file)

            self.assertEqual(next_line, '')
            self.assertEqual(attributes, expected_attributes)
            self.assertEqual(note_file.tell(), len(fixture))

    def test_read_element_attributes_should_stop_before_folder_end(self):
        fixture = (
            "	ID=413\n"
            "-\n"
            "	UNIQUEID=BCD"
        )
        expected_attributes = {
            'ID': '413'
        }

        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[0])['type'] == LineType.ATTRIBUTE
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[1])['type'] == LineType.END
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[2])['type'] == LineType.ATTRIBUTE

        with closing(StringIO(fixture)) as note_file:
            (attributes, next_line) = HotlistIterator.read_element_attributes('NOTE', note_file)

            self.assertEqual(next_line, '-\n')
            self.assertEqual(attributes, expected_attributes)
            self.assertEqual(note_file.tell(), fixture.find("-\n") + len("-\n"))

    def test_read_element_attributes_should_stop_before_next_element(self):
        fixture = (
            "	ID=413\n"
            "#NOTE\n"
            "	ID=414\n"
        )
        expected_attributes = {
            'ID': '413'
        }

        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[0])['type'] == LineType.ATTRIBUTE
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[1])['type'] == LineType.ELEMENT
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[2])['type'] == LineType.ATTRIBUTE

        with closing(StringIO(fixture)) as note_file:
            (attributes, next_line) = HotlistIterator.read_element_attributes('NOTE', note_file)

            self.assertEqual(next_line, '#NOTE\n')
            self.assertEqual(attributes, expected_attributes)
            self.assertEqual(note_file.tell(), fixture.find("#NOTE\n") + len("#NOTE\n"))

    def test_read_element_attributes_should_detect_duplicate_attributes(self):
        fixture = (
            "	ID=413\n"
            "	ID=414\n"
        )

        assert all([HotlistIterator.parse_hotlist_line(line)['type'] == LineType.ATTRIBUTE for line in fixture.splitlines()])

        with closing(StringIO(fixture)) as note_file:
            with self.assertRaises(DuplicateAttribute):
                HotlistIterator.read_element_attributes('NOTE', note_file)

    def test_read_element_attributes_should_detect_invalid_lines(self):
        fixture = (
            "**********************\n"
            "	ID=414\n"
        )

        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[0])['type'] == None
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[1])['type'] == LineType.ATTRIBUTE

        with closing(StringIO(fixture)) as note_file:
            with self.assertRaises(InvalidLine):
                HotlistIterator.read_element_attributes('NOTE', note_file)

    def test_read_element_attributes_should_detect_headers_in_a_wrong_place(self):
        fixture = (
            "Options: *\n"
            "	ID=414\n"
        )

        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[0])['type'] == LineType.HEADER
        assert HotlistIterator.parse_hotlist_line(fixture.splitlines()[1])['type'] == LineType.ATTRIBUTE

        with closing(StringIO(fixture)) as note_file:
            with self.assertRaises(StructuralError):
                HotlistIterator.read_element_attributes('NOTE', note_file)

    def test_is_header_line_should_detect_header_lines(self):
        fixtures = [
            # Lines actually seen in the wild
            (True,  "Opera Hotlist version 2.0"),
            (True,  "Options: encoding = utf8, version=3"),
            # Contrived examples that should still be accepted
            (True,  "Opera Hotlist version 3.0"),
            (True,  "Opera Hotlist version 1.2.3"),
            (True,  "Opera Hotlist version 2.0 beta"),
            (True,  "Options: encoding = utf8, version=4"),
            (True,  "Options: encoding = utf8"),
            (True,  "Options:"),
            (True,  "Options: sth"),
            # Examples that should not be accepted
            (False, " Opera Hotlist version 2.0"),
            (False, "Opera Hotlist"),
            (False, ""),
            (False, " "),
            (False, " Options: encoding = utf8, version=4"),
            (False, "Optio"),
            (False, "#Options"),
            (False, "\tA=B")
        ]

        for expected_result, line in fixtures:
            self.assertEqual((HotlistIterator.is_header_line(line), line), (expected_result, line))

    def test_parse_hotlist_line(self):
        fixtures = [
            # Lines actually seen in the wild
            ("#FOLDER\n",                    {'type': LineType.ELEMENT,   'name': 'FOLDER'}),
            ("#NOTE\n",                      {'type': LineType.ELEMENT,   'name': 'NOTE'}),
            ("\tID=3266\n",                  {'type': LineType.ATTRIBUTE, 'name': 'ID',           'value': '3266'}),
            ("\tNAME=Trash\n",               {'type': LineType.ATTRIBUTE, 'name': 'NAME',         'value': 'Trash'}),
            ("\tCREATED=1188605760\n",       {'type': LineType.ATTRIBUTE, 'name': 'CREATED',      'value': '1188605760'}),
            ("\tTRASH FOLDER=YES\n",         {'type': LineType.ATTRIBUTE, 'name': 'TRASH FOLDER', 'value': 'YES'}),
            ("-\n",                          {'type': LineType.END}),
            ("\n",                           {'type': LineType.EMPTY}),
            ("Opera Hotlist version 2.0\n",  {'type': LineType.HEADER}),
            # Contrived examples that should still be recognized
            ("#NOTE\t \n",                   {'type': LineType.ELEMENT, 'name': 'NOTE'}),
            ("- \n",                         {'type': LineType.END}),
            ("",                             {'type': LineType.EMPTY}),
            (" \n",                          {'type': LineType.EMPTY}),
            ("\t\n",                         {'type': LineType.EMPTY}),
            ("\tA=B\n",                      {'type': LineType.ATTRIBUTE, 'name': 'A',            'value': 'B'}),
            ("\tA B=C D\n",                  {'type': LineType.ATTRIBUTE, 'name': 'A B',          'value': 'C D'}),
            ("\tA=B=C=D\n",                  {'type': LineType.ATTRIBUTE, 'name': 'A',            'value': 'B=C=D'}),
            ("\tąęół=cde\n",                 {'type': LineType.ATTRIBUTE, 'name': 'ąęół',         'value': 'cde'}),
            ("\tabc=\n",                     {'type': LineType.ATTRIBUTE, 'name': 'abc',          'value': ''}),
            ("\tTRASH_FOLDER=YES\n",         {'type': LineType.ATTRIBUTE, 'name': 'TRASH_FOLDER', 'value': 'YES'}),
            ("\t\t=abc\n",                   {'type': LineType.ATTRIBUTE, 'name': '',             'value': 'abc'}),
            ("\t  =abc\n",                   {'type': LineType.ATTRIBUTE, 'name': '',             'value': 'abc'}),
            ("\t=abc\n",                     {'type': LineType.ATTRIBUTE, 'name': '',             'value': 'abc'}),
            ("\t=\n",                        {'type': LineType.ATTRIBUTE, 'name': '',             'value': ''}),
            ("\t = \n",                      {'type': LineType.ATTRIBUTE, 'name': '',             'value': ' '}),
            # Examples that should not be recognized
            ("#note\n",                      {'type': None}),
            (" #NOTE \n",                    {'type': None}),
            ("\t#NOTE \n",                   {'type': None}),
            ("#\n",                          {'type': None}),
            ("#A NOTE\n",                    {'type': None}),
            (" -\n",                         {'type': None}),
            ("1+2\n",                        {'type': None}),
        ]

        for line, expected_result in fixtures:
            self.assertEqual((HotlistIterator.parse_hotlist_line(line), line), (expected_result, line))

    def test_parse_hotlist_line_should_strip_whitespace_from_attribute_names(self):
        fixtures = [
            # Strip name
            ("\t\tID=3266\n",               {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266'}),
            ("\t  ID=3266\n",               {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266'}),
            ("\t  \tID=3266\n",             {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266'}),
            ("\tID\t=3266\n",               {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266'}),
            ("\tID =3266\n",                {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266'}),
            ("\tID \t =3266\n",             {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266'}),
            ("\t ID =3266\n",               {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266'}),
            # Don't strip value
            ("\tID=\t3266\n",               {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '\t3266'}),
            ("\tID=  3266\n",               {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '  3266'}),
            ("\tID=  \t3266\n",             {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '  \t3266'}),
            ("\tID=3266\t\n",               {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266\t'}),
            ("\tID=3266 \n",                {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266 '}),
            ("\tID=3266 \t \n",             {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '3266 \t '}),
            ("\tID= 3266 \n",               {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': ' 3266 '}),
            ("\tID=\x02\x023266\x02\x02\n", {'type': LineType.ATTRIBUTE, 'name': 'ID', 'value': '\x02\x023266\x02\x02'}),
        ]

        for line, expected_result in fixtures:
            self.assertEqual((HotlistIterator.parse_hotlist_line(line), line), (expected_result, line))
