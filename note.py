""" A class that represents a single note """

from datetime import datetime

class MissingProperties(Exception):
    pass

class Note:
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

    def __init__(self, title, body, tags, timestamp):
        self.title     = title
        self.body      = body
        self.tags      = tags
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'title':     self.title,
            'body':      self.body,
            'tags':      self.tags,
            # NOTE: isoformat() is supposedly faster but it's output is harder
            # to parse as the microsecond part is omitted if it's 0.
            'timestamp': self.timestamp.strftime(self.TIMESTAMP_FORMAT)
        }

    @classmethod
    def from_dict(cls, note_dict):
        missing_properties = set(['title', 'body', 'tags', 'timestamp']) - set(note_dict.keys())
        if len(missing_properties) > 0:
            raise MissingProperties("Not all required note properties are present")

        return cls(
            note_dict['title'],
            note_dict['body'],
            note_dict['tags'],
            datetime.strptime(note_dict['timestamp'], cls.TIMESTAMP_FORMAT)
        )
