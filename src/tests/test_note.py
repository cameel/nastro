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
