""" Tools for importing data from Opera """

from datetime import datetime

from PyQt5.QtGui  import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt

from ...note   import Note, InvalidTagCharacter
from .iterator import HotlistIterator, ParseError, StructuralError

class MissingNoteAttributes(ParseError): pass
class InvalidAttributeValue(ParseError): pass

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

def element_to_note(attributes):
    required_note_attributes = ['CREATED']

    missing_attributes = [attribute_name for attribute_name in required_note_attributes if not attribute_name in attributes]
    if len(missing_attributes) > 0:
        note_id = attributes['ID'] if 'ID' in attributes else '???'
        raise MissingNoteAttributes("Note (ID={}) is missing one or more required attributes: {}".format(note_id, ', '.join(missing_attributes)))

    (title, body) = title_body_split(attributes.get('NAME'))

    return Note(
        title      = title,
        body       = body,
        tags       = [],
        # NOTE: Opera saves timestamps in localtime rather than UTC. This makes it impossible
        # to correctly decode it unless we're now in the same time zone.
        created_at = datetime.utcfromtimestamp(int(attributes['CREATED']))
    )

def tree_validating_iterator(hotlist_iterator):
    """ Top level elements are at level 0. 'end' elements are at the same level as their matching folders. """
    level = 0
    for element in hotlist_iterator:
        if element == 'end':
            if level <= 0:
                raise StructuralError("Found folder end marker without a matching folder")

            level -= 1

            yield (element, level)
        else:
            element_name, attributes = element

            yield (element, level)

            if element_name == 'FOLDER':
                level += 1

    if level > 0:
        # It may be a good idea to replace it with a warning when we have an UI for importers
        raise StructuralError("Not all folders have matching end markers. The file may have been truncated.")

def trash_aware_hotlist_iterator(tree_validating_iterator):
    trash_level = None
    for (element, level) in tree_validating_iterator:
        if element == 'end':
            assert level >= 0

            if trash_level != None and level < trash_level:
                trash_level = None
        else:
            element_name, attributes = element

            if element_name == 'FOLDER':
                if 'TRASH FOLDER' in attributes:
                    if attributes['TRASH FOLDER'].upper() not in ['YES', 'NO']:
                        raise InvalidAttributeValue("Unrecognized value of 'TRASH FOLDER' attribute: '{}'".format(attributes['TRASH FOLDER']))

                    if attributes['TRASH FOLDER'] == 'YES':
                        if trash_level != None:
                            raise StructuralError("Nested trash folders are not supported")

                        trash_level = level

        yield (element, level, trash_level != None)

def import_opera_notes(note_file, skip_trash_folder = True):
    iterator = trash_aware_hotlist_iterator(tree_validating_iterator(HotlistIterator(note_file)))

    model      = QStandardItemModel()
    item_stack = [model]
    for (element, level, in_trash_folder) in iterator:
        if not (in_trash_folder and skip_trash_folder):
            if element == 'end':
                item_stack.pop()
            else:
                element_name, attributes = element

                if element_name in ['NOTE', 'FOLDER']:
                    note = element_to_note(attributes)
                    assert note != None

                    item = QStandardItem()
                    item.setData(note, Qt.EditRole)

                    assert len(item_stack) > 0
                    item_stack[-1].appendRow(item)

                    if element_name == 'FOLDER':
                        item_stack.append(item)

    return model
