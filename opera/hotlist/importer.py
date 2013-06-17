""" Tools for importing data from Opera """

from datetime import datetime

from note      import Note
from .iterator import HotlistIterator, ParseError

class MissingNoteAttributes(ParseError):
    pass

def line_strip(text):
    """Strips leading empty lines and all trailing whitespace from the text"""
    try:
        first_nonwhitespace_index = next(i for i, character in enumerate(text) if not character.isspace())
    except StopIteration:
        return ''

    last_nonwhitespace_index = len(text) - 1 - next(i for i, character in enumerate(reversed(text)) if not character.isspace())
    assert last_nonwhitespace_index >= first_nonwhitespace_index

    try:
        first_nonwhitespace_line_start = first_nonwhitespace_index - next(i for i, character in enumerate(reversed(text[:first_nonwhitespace_index])) if character == '\n')
    except StopIteration:
        first_nonwhitespace_line_start = 0

    return text[first_nonwhitespace_line_start:last_nonwhitespace_index + 1]

def element_to_note(element):
    element_name, attributes = element

    required_note_attributes = ['CREATED']

    if element_name == 'NOTE':
        missing_attributes = [attribute_name for attribute_name in required_note_attributes if not attribute_name in attributes]
        if len(missing_attributes) > 0:
            note_id = attributes['ID'] if 'ID' in attributes else '???'
            raise MissingNoteAttributes("Note (ID={}) is missing one or more required attributes: {}".format(note_id, ', '.join(missing_attributes)))

        if 'NAME' in attributes:
            title_and_body = attributes['NAME'].replace('\02\02', '\n').split('\n', 1)

            assert len(title_and_body) > 0, 'split() always returns at least one item'

            title = title_and_body[0].strip()
            body  = line_strip(title_and_body[1]) if len(title_and_body) > 1 else ''
        else:
            title = ''
            body  = ''

        return Note(
            title,
            body,
            [],
            datetime.fromtimestamp(int(attributes['CREATED']))
        )

    return None

def import_opera_notes(note_file):
    notes = []
    for element in HotlistIterator(note_file):
        if element != 'end':
            note = element_to_note(element)
            if note != None:
                notes.append(note)

    return notes
