""" A class that represents a single note """

from datetime import datetime

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
