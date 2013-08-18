""" An iterator that goes over top-level elements of an Opera Hotlist file """

import re

HEADER_LINE_PATTERNS = [
    re.compile(r'^Opera\s+Hotlist\s+version\s+[\d.]'),
    re.compile(r'^Options:.*')
]
# FIXME: Can we really assume that element names do not contain any funny characters?
ELEMENT_PATTERN    = re.compile('^#(?P<name>[A-Z_\-]+)\s*$')
# NOTE: value is intentionally not being stripped from whitespace here. There may be a leading indentation
# in NAME attributes that we want to preserve.
ATTRIBUTE_PATTERN  = re.compile('^\t(?P<name>[^=]*)=(?P<value>.*)$')
END_MARKER_PATTERN = re.compile('^-\s*$')

class LineType:
    EMPTY     = 0
    HEADER    = 1
    END       = 2
    ELEMENT   = 3
    ATTRIBUTE = 4

class ParseError(Exception):          pass
class InvalidLine(ParseError):        pass
class StructuralError(ParseError):    pass
class DuplicateAttribute(ParseError): pass

class HotlistIterator:
    def __init__(self, note_file):
        self._note_file = note_file
        self._last_line = ' '

    def __iter__(self):
        self._note_file.seek(0)

        line = self._last_line
        while line != '' and (line.strip() == '' or type(self).is_header_line(line)):
            line = self._note_file.readline()

        self._last_line = line

        return self

    def __next__(self):
        while self._last_line != '' and self._last_line.strip() == '':
            self._last_line = self._note_file.readline()

        if self._last_line == '':
            raise StopIteration

        line_info = type(self).parse_hotlist_line(self._last_line)
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

            (attributes, self._last_line) = type(self).read_element_attributes(element_name, self._note_file)
            return (element_name, attributes)

    @classmethod
    def read_element_attributes(cls, element_name, note_file):
        attributes = {}

        line = note_file.readline()
        while line != '':
            line_info = cls.parse_hotlist_line(line)

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

    @classmethod
    def is_header_line(cls, line):
        for pattern in HEADER_LINE_PATTERNS:
            match = pattern.match(line)
            if match != None:
                return True

        return False

    @classmethod
    def parse_hotlist_line(cls, line):
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

            groupdict = match.groupdict()

            return {
                'type':  LineType.ATTRIBUTE,
                'name':  groupdict['name'].strip()  if 'name'  in groupdict else '',
                # NOTE: Value intentionally not stripped. Only specific, known attributes should be stripped
                # when it's known that the indentation is not significant for them.
                'value': groupdict['value'] if 'value' in groupdict else ''
            }

        if cls.is_header_line(line):
            return {'type': LineType.HEADER}

        return {'type': None}
