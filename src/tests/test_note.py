import unittest
from datetime import datetime

from ..note import Note, InvalidTagCharacter, MissingProperties

class NoteTest(unittest.TestCase):
    def test_init_should_initialize_note(self):
        note = Note(
            title       = "X",
            body        = "Y",
            tags        = ["a", "b", "c"],
            created_at  = datetime(2013, 6, 16),
            modified_at = datetime(2013, 7, 16)
        )

        self.assertEqual(note.title,       "X")
        self.assertEqual(note.body,        "Y")
        self.assertEqual(note.tags,        ["a", "b", "c"])
        self.assertEqual(note.created_at,  datetime(2013, 6, 16))
        self.assertEqual(note.modified_at, datetime(2013, 7, 16))

    def test_init_should_initialize_note_with_defaults(self):
        note = Note()

        self.assertEqual(note.title, '')
        self.assertEqual(note.body,  '')
        self.assertEqual(note.tags,  [])

        # TODO: Use mocks for datetime to test created_at and modified_at

    def test_init_should_set_modified_at_to_created_at_if_not_specified(self):
        note = Note(
            title       = "X",
            body        = "Y",
            tags        = ["a", "b", "c"],
            created_at  = datetime(2013, 6, 16)
        )

        assert note.created_at == datetime(2013, 6, 16)
        self.assertEqual(note.modified_at, note.created_at)

    def test_from_dict_should_return_note_objects(self):
        note = Note.from_dict({
            'title':       "X",
            'body':        "Y",
            'tags':        ["a", "b", "c"],
            'created_at':  "2013-06-16T00:00:00.000000",
            'modified_at': "2013-07-16T00:00:00.000000"
        })

        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.title,       "X")
        self.assertEqual(note.body,        "Y")
        self.assertEqual(note.tags,        ["a", "b", "c"])
        self.assertEqual(note.created_at,  datetime(2013, 6, 16))
        self.assertEqual(note.modified_at, datetime(2013, 7, 16))

    def test_from_dict_should_detect_missing_properties(self):
        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'body':        "Y",
                'tags':        ["a", "b", "c"],
                'created_at':  "2013-06-16T00:00:00.000000",
                'modified_at': "2013-07-16T00:00:00.000000"
            })

        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'title':       "X",
                'tags':        ["a", "b", "c"],
                'created_at':  "2013-06-16T00:00:00.000000",
                'modified_at': "2013-07-16T00:00:00.000000"
            })

        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'title':       "X",
                'body':        "Y",
                'created_at':  "2013-06-16T00:00:00.000000",
                'modified_at': "2013-07-16T00:00:00.000000"
            })

        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'title':       "X",
                'body':        "Y",
                'tags':        ["a", "b", "c"],
                'modified_at': "2013-07-16T00:00:00.000000"
            })


        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'title':       "X",
                'body':        "Y",
                'tags':        ["a", "b", "c"],
                'created_at':  "2013-06-16T00:00:00.000000"
            })

    def test_from_dict_should_ignore_extra_properties(self):
        note = Note.from_dict({
            'title':       "X",
            'body':        "Y",
            'tags':        ["a", "b", "c"],
            'created_at':  "2013-06-16T00:00:00.000000",
            'modified_at': "2013-07-16T00:00:00.000000",
            'foo':         'bar'
        })

        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.title,       "X")
        self.assertEqual(note.body,        "Y")
        self.assertEqual(note.tags,        ["a", "b", "c"])
        self.assertEqual(note.created_at,  datetime(2013, 6, 16))
        self.assertEqual(note.modified_at, datetime(2013, 7, 16))
        self.assertTrue(not hasattr(note,  'foo'))

    def test_from_dict_should_detect_invalid_characters_in_tags(self):
        with self.assertRaises(InvalidTagCharacter):
            note = Note.from_dict({
                'title':       "X",
                'body':        "Y",
                'tags':        ["a", "b", "c,d,e"],
                'created_at':  "2013-06-16T00:00:00.000000",
                'modified_at': "2013-07-16T00:00:00.000000"
            })

    def test_split_tags_should_split_a_string_into_a_list_of_tags(self):
        self.assertEqual(Note.split_tags(''),                 [])
        self.assertEqual(Note.split_tags(','),                [])
        self.assertEqual(Note.split_tags(',,,'),              [])
        self.assertEqual(Note.split_tags('a'),                ['a'])
        self.assertEqual(Note.split_tags('a,,,'),             ['a'])
        self.assertEqual(Note.split_tags('a, b'),             ['a', 'b'])
        self.assertEqual(Note.split_tags(' a,b '),            ['a', 'b'])
        self.assertEqual(Note.split_tags('abc def, ghi'),     ['abc def', 'ghi'])
        self.assertEqual(Note.split_tags('\tabc\tdef,\tghi'), ['abc\tdef', 'ghi'])
        self.assertEqual(Note.split_tags('\nabc\ndef,\nghi'), ['abc\ndef', 'ghi'])

    def test_split_tags_should_sort_tags_alphabetically(self):
        self.assertEqual(Note.split_tags('b, a, c'), ['a', 'b', 'c'])

    def test_split_tags_should_remove_duplicates(self):
        self.assertEqual(Note.split_tags('a, a, a'),      ['a'])
        self.assertEqual(Note.split_tags('a, b,  a,  b'), ['a', 'b'])

    def test_join_tags_should_join_a_list_of_tags_into_a_string(self):
        self.assertEqual(Note.join_tags([]),                      '')
        self.assertEqual(Note.join_tags(['', '']),                ', ')
        self.assertEqual(Note.join_tags(['', '', '', '']),        ', , , ')
        self.assertEqual(Note.join_tags(['a']),                   'a')
        self.assertEqual(Note.join_tags(['a', '', '', '', '']),   'a, , , , ')
        self.assertEqual(Note.join_tags(['a', 'b']),              'a, b')
        self.assertEqual(Note.join_tags([' a', 'b ']),            ' a, b ')
        self.assertEqual(Note.join_tags(['b', 'a']),              'b, a')
        self.assertEqual(Note.join_tags(['a', 'a', 'a']),         'a, a, a')
        self.assertEqual(Note.join_tags([' abc def ', 'ghi']),    ' abc def , ghi')
        self.assertEqual(Note.join_tags(['\tabc\tdef\t', 'ghi']), '\tabc\tdef\t, ghi')
        self.assertEqual(Note.join_tags(['\nabc\ndef\n', 'ghi']), '\nabc\ndef\n, ghi')

    def test_serialize_timestamp_should_convert_datetime_to_unambiguous_string_representation(self):
        self.assertEqual(Note.serialize_timestamp(datetime(2013, 7, 26, 13, 37, 11, 123456)), "2013-07-26T13:37:11.123456")

    def test_deserialize_timestamp_should_convert_serialized_datetime_back_into_timestamp(self):
        self.assertEqual(Note.deserialize_timestamp("2013-07-26T13:37:11.123456"), datetime(2013, 7, 26, 13, 37, 11, 123456))
        self.assertEqual(Note.deserialize_timestamp("2013-7-26T1:37:11.123456"),   datetime(2013, 7, 26, 1, 37, 11, 123456))

    def test_deserialize_timestamp_should_raise_an_exception_if_string_does_not_represent_a_timestamp(self):
        with self.assertRaises(Exception):
            Note.deserialize_timestamp("")

        with self.assertRaises(Exception):
            Note.deserialize_timestamp("2013-07-26")

        with self.assertRaises(Exception):
            Note.deserialize_timestamp("13:37:11.123456")

        with self.assertRaises(Exception):
            Note.deserialize_timestamp("2013-07-26 13:37:11.123456")

        with self.assertRaises(Exception):
            Note.deserialize_timestamp("2013 - 07-26T13:37:11.123456")

        with self.assertRaises(Exception):
            Note.deserialize_timestamp("date")

        with self.assertRaises(Exception):
            Note.deserialize_timestamp("2013-00-26 13:37:11.123456")

        with self.assertRaises(Exception):
            Note.deserialize_timestamp("02013-7-026T013:037:011.0123456")

        with self.assertRaises(Exception):
            Note.deserialize_timestamp("      2013-07-26T13:37:11.123456      ")
