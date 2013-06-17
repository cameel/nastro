""" Tools for importing data from Opera """

import re
from datetime import datetime

from note import Note

HEADER_LINE_PATTERNS = [
    re.compile(r'^Opera\s+Hotlist\s+version\s+[\d.]'),
    re.compile(r'^Options:.*')
]
# FIXME: Can we really assume that element names do not contain any funny characters?
ELEMENT_PATTERN    = re.compile('^#(?P<name>[A-Z_\-]+)\s*$')
# NOTE: value is intentionally not being stripped from whitespace here. There may be a leading indentation
# in NAME attributes that we want to preserve.
ATTRIBUTE_PATTERN  = re.compile('^\t(?P<name>[^=]+)=(?P<value>.*)$')
END_MARKER_PATTERN = re.compile('^-\s*$')

class LineType:
    EMPTY     = 0
    HEADER    = 1
    END       = 2
    ELEMENT   = 3
    ATTRIBUTE = 4

class ParseError(Exception):
    pass

class InvalidLine(ParseError):
    pass

class StructuralError(ParseError):
    pass

class DuplicateAttribute(ParseError):
    pass

class ElementIterator:
    def __init__(self, note_file):
        self._note_file = note_file
        self._last_line = ' '

    def __iter__(self):
        self._note_file.seek(0)

        line = self._last_line
        while line != '' and (line.strip() == '' or is_header_line(line)):
            line = self._note_file.readline()

        self._last_line = line

        return self

    def __next__(self):
        while self._last_line != '' and self._last_line.strip() == '':
            self._last_line = self._note_file.readline()

        if self._last_line == '':
            raise StopIteration

        line_info = parse_hotlist_line(self._last_line)
        assert line_info['type'] not in [LineType.EMPTY, LineType.HEADER]

        if line_info['type'] == None:
            raise InvalidLine("Invalid line format: " + line)

        if line_info['type'] == LineType.ATTRIBUTE:
            raise StructuralError("Found an attribute without a preceding element: {name}={value}".format(**line_info))

        if line_info['type'] == LineType.END:
            self._last_line = self._note_file.readline()
            return 'end'

        if line_info['type'] == LineType.ELEMENT:
            element_name = line_info['name']

            (attributes, self._last_line) = ElementIterator.read_element_attributes(element_name, self._note_file)
            return (element_name, attributes)

    @classmethod
    def read_element_attributes(cls, element_name, note_file):
        attributes = {}

        line = note_file.readline()
        while line != '':
            line_info = parse_hotlist_line(line)

            if line_info['type'] in [LineType.ELEMENT, LineType.END]:
                return (attributes, line)
            elif line_info['type'] == LineType.ATTRIBUTE:
                if line_info['name'] in attributes:
                    # FIXME: This does not say which specific element it is and there may be lots of them
                    raise DuplicateAttribute('Element {} contains a duplicate attribute: {name}={value}'.format(element_name, **line_info))

                attributes[line_info['name']] = line_info['value']
            elif line_info['type'] == None:
                raise InvalidLine("Invalid line format: " + line)
            elif line_info['type'] == LineType.HEADER:
                raise StructuralError("Header lines inside elements are not allowed: " + line)
            elif line_info['type'] == LineType.EMPTY:
                pass

            line = note_file.readline()

        return (attributes, '')

def is_header_line(line):
    for pattern in HEADER_LINE_PATTERNS:
        match = pattern.match(line)
        if match != None:
            return True

    return False

def parse_hotlist_line(line):
    if line.strip() == '':
        return {'type': LineType.EMPTY}

    match = END_MARKER_PATTERN.match(line)
    if match != None:
        return {'type': LineType.END}

    match = ELEMENT_PATTERN.match(line)
    if match != None:
        assert 'name' in match.groupdict()

        return {
            'type': LineType.ELEMENT,
            'name': match.groupdict()['name']
        }

    match = ATTRIBUTE_PATTERN.match(line)
    if match != None:
        assert 'name'  in match.groupdict()
        assert 'value' in match.groupdict()

        return {
            'type':  LineType.ATTRIBUTE,
            'name':  match.groupdict()['name'].strip(),
            # NOTE: Value intentionally not stripped. Only specific, known attributes should be stripped
            # when it's known that the indentation is not significant for them.
            'value': match.groupdict()['value']
        }

    if is_header_line(line):
        return {'type': LineType.HEADER}

    return {'type': None}

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

    if element_name == 'NOTE':
        if 'NAME' in attributes:
            # FIXME: What about notes without names?
            title_and_body = attributes['NAME'].replace('\02\02', '\n').split('\n', 1)

            # Currently the regexes match only attributes with non-empty values
            assert len(title_and_body) > 0

            return Note(
                title_and_body[0].strip(),
                line_strip(title_and_body[1]) if len(title_and_body) > 1 else '',
                [],
                datetime.fromtimestamp(int(attributes['CREATED']))
            )

    return None

def import_opera_notes(note_file):
    notes = []
    for element in ElementIterator(note_file):
        if element != 'end':
            note = element_to_note(element)
            if note != None:
                notes.append(note)

    return notes
