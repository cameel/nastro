""" A class that represents a single note """

from datetime import datetime

class MissingProperties(Exception):
    pass

class InvalidTagCharacter(Exception):
    pass

class Note:
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

    def __init__(self, title = '', body = '', tags = [], created_at = datetime.utcnow(), modified_at = None):
        assert created_at != None

        self.title       = title
        self.body        = body
        self.tags        = tags
        self.created_at  = created_at
        self.modified_at = modified_at if modified_at != None else created_at

    def to_dict(self):
        return {
            'title':       self.title,
            'body':        self.body,
            'tags':        self.tags,
            # NOTE: isoformat() is supposedly faster but it's output is harder
            # to parse as the microsecond part is omitted if it's 0.
            'created_at':  self.created_at.strftime(self.TIMESTAMP_FORMAT),
            'modified_at': self.modified_at.strftime(self.TIMESTAMP_FORMAT)
        }

    @classmethod
    def from_dict(cls, note_dict):
        missing_properties = set(['title', 'body', 'tags', 'created_at', 'modified_at']) - set(note_dict.keys())
        if len(missing_properties) > 0:
            raise MissingProperties("Not all required note properties are present")

        if any(',' in tag for tag in note_dict['tags']):
            raise InvalidTagCharacter("Commas (,) are not allowed in tags")

        return cls(
            title       = note_dict['title'],
            body        = note_dict['body'],
            tags        = note_dict['tags'],
            created_at  = datetime.strptime(note_dict['created_at'],  cls.TIMESTAMP_FORMAT),
            modified_at = datetime.strptime(note_dict['modified_at'], cls.TIMESTAMP_FORMAT)
        )

    @classmethod
    def split_tags(cls, text):
        return sorted(set([tag.strip() for tag in text.split(',') if tag.strip() != '']))

    @classmethod
    def join_tags(cls, tags):
        return ', '.join(tags)

    def __repr__(self):
        return 'Note' + repr(self.to_dict())
