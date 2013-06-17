import unittest
from datetime import datetime

from note import Note, InvalidTagCharacter, MissingProperties

class NoteTest(unittest.TestCase):
    def test_from_dict_should_return_note_objects(self):
        note = Note.from_dict({
            'title':     "X",
            'body':      "Y",
            'tags':      ["a", "b", "c"],
            'timestamp': "2013-06-16T00:00:00.000000"
        })

        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.title,     "X")
        self.assertEqual(note.body,      "Y")
        self.assertEqual(note.tags,      ["a", "b", "c"])
        self.assertEqual(note.timestamp, datetime(2013, 6, 16))

    def test_from_dict_should_detect_missing_properties(self):
        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'body':      "Y",
                'tags':      ["a", "b", "c"],
                'timestamp': "2013-06-16T00:00:00.000000"
            })

        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'title':     "X",
                'tags':      ["a", "b", "c"],
                'timestamp': "2013-06-16T00:00:00.000000"
            })

        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'title':     "X",
                'body':      "Y",
                'timestamp': "2013-06-16T00:00:00.000000"
            })

        with self.assertRaises(MissingProperties):
            note = Note.from_dict({
                'title':     "X",
                'body':      "Y",
                'tags':      ["a", "b", "c"],
            })

    def test_from_dict_should_ignore_extra_properties(self):
        note = Note.from_dict({
            'title':     "X",
            'body':      "Y",
            'tags':      ["a", "b", "c"],
            'timestamp': "2013-06-16T00:00:00.000000",
            'foo':       'bar'
        })

        self.assertTrue(isinstance(note, Note))
        self.assertEqual(note.title,     "X")
        self.assertEqual(note.body,      "Y")
        self.assertEqual(note.tags,      ["a", "b", "c"])
        self.assertEqual(note.timestamp, datetime(2013, 6, 16))
        self.assertTrue(not hasattr(note, 'foo'))

    def test_from_dict_should_detect_invalid_characters_in_tags(self):
        with self.assertRaises(InvalidTagCharacter):
            note = Note.from_dict({
                'title':     "X",
                'body':      "Y",
                'tags':      ["a", "b", "c,d,e"],
                'timestamp': "2013-06-16T00:00:00.000000"
            })
