""" A class that represents a single note """

from datetime import datetime

class MissingProperties(Exception):
    pass

class InvalidTagCharacter(Exception):
    pass

class Note:
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

    def __init__(self, title = '', body = '', tags = [], created_at = datetime.utcnow(), modified_at = None, id = None):
        assert created_at != None
        assert not isinstance(id, str)

        self.title       = title
        self.body        = body
        self.tags        = tags
        self.created_at  = created_at
        self.modified_at = modified_at if modified_at != None else created_at
        self.id          = id

    def to_dict(self):
        return {
            'title':       self.title,
            'body':        self.body,
            'tags':        self.tags,
            'created_at':  self.serialize_timestamp(self.created_at),
            'modified_at': self.serialize_timestamp(self.modified_at),
            'id':          self.id
        }

    @classmethod
    def from_dict(cls, note_dict):

        missing_properties = set(['title', 'body', 'tags', 'created_at', 'modified_at', 'id']) - set(note_dict.keys())
        if len(missing_properties) > 0:
            raise MissingProperties("Some required properties are missing: {}".format(missing_properties))

        if any(',' in tag for tag in note_dict['tags']):
            raise InvalidTagCharacter("Commas (,) are not allowed in tags")

        return cls(
            title       = note_dict['title'],
            body        = note_dict['body'],
            tags        = note_dict['tags'],
            created_at  = cls.deserialize_timestamp(note_dict['created_at']),
            modified_at = cls.deserialize_timestamp(note_dict['modified_at']),
            id          = note_dict['id']
        )

    @classmethod
    def split_tags(cls, text):
        return sorted(set([tag.strip() for tag in text.split(',') if tag.strip() != '']))

    @classmethod
    def join_tags(cls, tags):
        return ', '.join(tags)

    @classmethod
    def serialize_timestamp(cls, timestamp):
        # NOTE: isoformat() is supposedly faster but its output is harder
        # to parse as the microsecond part is omitted if it's 0.
        return timestamp.strftime(cls.TIMESTAMP_FORMAT)

    @classmethod
    def deserialize_timestamp(cls, serialized_timestamp):
        return datetime.strptime(serialized_timestamp, cls.TIMESTAMP_FORMAT)

    def __repr__(self):
        return 'Note' + repr(self.to_dict())
