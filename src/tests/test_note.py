import unittest
from datetime    import datetime
from collections import deque

from ..note import Note, InvalidTagCharacter, MissingProperties, WrongAttributeType

class NoteTest(unittest.TestCase):
    def test_init_should_initialize_note(self):
        note = Note(
            body        = "Y",
            tags        = ["a", "b", "c"],
            created_at  = datetime(2013, 6, 16),
            modified_at = datetime(2013, 7, 16),
            id          = 666
        )

        self.assertEqual(note.body,        "Y")
        self.assertEqual(note.tags,        ["a", "b", "c"])
        self.assertEqual(note.created_at,  datetime(2013, 6, 16))
        self.assertEqual(note.modified_at, datetime(2013, 7, 16))
        self.assertEqual(note.id,          666)

    def test_init_should_initialize_note_with_defaults(self):
        note = Note()

        self.assertEqual(note.body,  '')
        self.assertEqual(note.tags,  [])
        self.assertEqual(note.id,    None)

        # TODO: Use mocks for datetime to test created_at and modified_at

    def test_init_should_set_modified_at_to_created_at_if_not_specified(self):
        note = Note(
            body        = "Y",
            tags        = ["a", "b", "c"],
            created_at  = datetime(2013, 6, 16)
        )

        assert note.created_at == datetime(2013, 6, 16)
        self.assertEqual(note.modified_at, note.created_at)

    def test_to_dict_should_put_all_note_attributes_in_a_dict_containing_only_primitive_types_and_structures_composed_of_them(self):
        note_dict = Note(
            body        = "Y",
            tags        = ["a", "b", "c"],
            created_at  = datetime(2013, 6, 16),
            modified_at = datetime(2013, 7, 16),
            id          = 666
        ).to_dict()

        self.assertEqual(note_dict['body'],        "Y")
        self.assertEqual(note_dict['tags'],        ["a", "b", "c"])
        self.assertEqual(note_dict['created_at'],  "2013-06-16T00:00:00.000000")
        self.assertEqual(note_dict['modified_at'], "2013-07-16T00:00:00.000000")
        self.assertEqual(note_dict['id'],          666)

    def test_from_dict_should_return_note_objects(self):
        note = Note.from_dict({
            'body':        "Y",
            'tags':        ["a", "b", "c"],
            'created_at':  "2013-06-16T00:00:00.000000",
            'modified_at': "2013-07-16T00:00:00.000000",
            'id':          None
        })

        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.body,        "Y")
        self.assertEqual(note.tags,        ["a", "b", "c"])
        self.assertEqual(note.created_at,  datetime(2013, 6, 16))
        self.assertEqual(note.modified_at, datetime(2013, 7, 16))

    def test_from_dict_should_detect_missing_properties(self):
        note_dict = {
            'body':        "Y",
            'tags':        ["a", "b", "c"],
            'created_at':  "2013-06-16T00:00:00.000000",
            'modified_at': "2013-07-16T00:00:00.000000",
            'id':          None
        }

        try:
            Note.from_dict(note_dict)
        except MissingProperties:
            assert False, "A property is missing from the original dict. The test is flawed."

        for missing_property in note_dict.keys():
            filtered_note_dict = {property: note_dict[property] for property in note_dict if property != missing_property}

            with self.assertRaises(MissingProperties):
                note = Note.from_dict(filtered_note_dict)

    def test_from_dict_should_ignore_extra_properties(self):
        note = Note.from_dict({
            'body':        "Y",
            'tags':        ["a", "b", "c"],
            'created_at':  "2013-06-16T00:00:00.000000",
            'modified_at': "2013-07-16T00:00:00.000000",
            'foo':         'bar',
            'id':          None
        })

        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.body,        "Y")
        self.assertEqual(note.tags,        ["a", "b", "c"])
        self.assertEqual(note.created_at,  datetime(2013, 6, 16))
        self.assertEqual(note.modified_at, datetime(2013, 7, 16))
        self.assertTrue(not hasattr(note,  'foo'))

    def test_from_dict_should_detect_invalid_characters_in_tags(self):
        with self.assertRaises(InvalidTagCharacter):
            note = Note.from_dict({
                'body':        "Y",
                'tags':        ["a", "b", "c,d,e"],
                'created_at':  "2013-06-16T00:00:00.000000",
                'modified_at': "2013-07-16T00:00:00.000000",
                'id':          None
            })

    def test_from_dict_should_detect_wrong_attribute_types(self):
        note_dict = {
            'body':        "Y",
            'tags':        ["a", "b", "c"],
            'created_at':  "2013-06-16T00:00:00.000000",
            'modified_at': "2013-07-16T00:00:00.000000",
            'id':          1
        }

        # ASSUMPTION: This does not raise exceptions
        Note.from_dict(note_dict)

        wrong_type_samples = [
            ('body',        1),
            ('tags',        ("a", "b", "c")),
            ('tags',        ()),
            ('tags',        {}),
            ('tags',        set()),
            ('tags',        deque(["a", "b", "c"])),
            ('tags',        [1, 2, 3]),
            ('created_at',  1234567890),
            ('created_at',  datetime(2013, 1, 1)),
            ('modified_at', 1234567890),
            ('modified_at', datetime(2013, 1, 1)),
            ('id',          "10"),
            ('id',          [])
        ]

        for tested_attribute, wrong_value in wrong_type_samples:
            filtered_note_dict = {attribute: note_dict[attribute] if attribute != tested_attribute else wrong_value for attribute in note_dict}

            with self.assertRaises(WrongAttributeType):
                Note.from_dict(filtered_note_dict)

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
