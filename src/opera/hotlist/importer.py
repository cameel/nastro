""" Tools for importing data from Opera """

from datetime import datetime

from ...note   import Note, InvalidTagCharacter
from .iterator import HotlistIterator, ParseError, StructuralError

FOLDER_TAG_SEPARATOR = '/'

class MissingNoteAttributes(ParseError):
    pass

class InvalidAttributeValue(ParseError):
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

def title_body_split(name_attribute):
    if name_attribute != None:
        title_and_body = name_attribute.replace('\02\02', '\n').split('\n', 1)
        assert len(title_and_body) > 0, 'split() always returns at least one item'

        return (
            title_and_body[0].strip(),
            line_strip(title_and_body[1]) if len(title_and_body) > 1 else ''
        )
    else:
        return ('', '')

def element_to_note(attributes, folder_path):
    required_note_attributes = ['CREATED']

    missing_attributes = [attribute_name for attribute_name in required_note_attributes if not attribute_name in attributes]
    if len(missing_attributes) > 0:
        note_id = attributes['ID'] if 'ID' in attributes else '???'
        raise MissingNoteAttributes("Note (ID={}) is missing one or more required attributes: {}".format(note_id, ', '.join(missing_attributes)))

    (title, body) = title_body_split(attributes.get('NAME'))

    tag = FOLDER_TAG_SEPARATOR.join(folder_path)
    return Note(
        title      = title,
        body       = body,
        tags       = [tag] if tag != '' else [],
        # NOTE: Opera saves timestamps in localtime rather than UTC. This makes it impossible
        # to correctly decode it unless we're now in the same time zone.
        created_at = datetime.utcfromtimestamp(int(attributes['CREATED']))
    )

def import_opera_notes(note_file, skip_trash_folder = True):
    notes        = []
    folder_stack = []
    trash_level  = None
    for element in HotlistIterator(note_file):
        if element == 'end':
            if len(folder_stack) == 0:
                raise StructuralError("Found folder end marker without a matching folder")

            folder_stack.pop()

            if trash_level != None and len(folder_stack) < trash_level:
                trash_level = None
        else:
            element_name, attributes = element

            body = ''
            if element_name == 'FOLDER':
                if 'TRASH FOLDER' in attributes:
                    if attributes['TRASH FOLDER'].upper() not in ['YES', 'NO']:
                        raise InvalidAttributeValue("Unrecognized value of 'TRASH FOLDER' attribute: '{}'".format(attributes['TRASH FOLDER']))

                    if attributes['TRASH FOLDER'] == 'YES':
                        if trash_level != None:
                            raise StructuralError("Nested trash folders are not supported")

                        trash_level = len(folder_stack)

                # NOTE: If there are two folders with identical names (or differing only with whitespace),
                # they won't be unambiguously discernible by tags after import.
                (title, body) = title_body_split(attributes.get('NAME'))
                folder_stack.append(title)

            if (trash_level == None or not skip_trash_folder) and (element_name == 'NOTE' or body != ''):
                note = element_to_note(attributes, folder_stack)
                if note != None:
                    notes.append(note)

    if len(folder_stack) > 0:
        # It may be a good idea to replace it with a warning when we have na UI for importers
        raise StructuralError("Not all folders have matching end markers. The file may have been truncated.")

    return notes
