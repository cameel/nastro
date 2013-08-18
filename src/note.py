""" A class that represents a single note """

from datetime import datetime

class MissingProperties(Exception):   pass
class InvalidTagCharacter(Exception): pass
class WrongAttributeType(Exception):  pass

class Note:
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
    SERIALIZED_ATTRIBUTE_TYPES = {
        'body':        (str,),
        'tags':        (list,),
        'created_at':  (str,),
        'modified_at': (str,),
        'id':          (int, type(None))
    }

    def __init__(self, body = '', tags = [], created_at = datetime.utcnow(), modified_at = None, id = None):
        assert created_at != None

        self.body        = body
        self.tags        = tags
        self.created_at  = created_at
        self.modified_at = modified_at if modified_at != None else created_at
        self.id          = id

        # NOTE: Types are strictly enforced here because we want it to be possible to
        # serialize a note into a dict of primivites and deserialize it back into an identical object.
        # If we let the caller pass derived types, those types would be lost after deserialization.
        assert type(self.body)        == str
        assert type(self.created_at)  == datetime
        assert type(self.modified_at) == datetime
        assert type(self.id)          in [int, type(None)]
        assert type(self.tags)        == list
        assert all(type(tag) == str for tag in self.tags)

    def to_dict(self):
        """ Converts note attributes into primitive values suitable for serialization
            and puts them into a dict. """

        note_dict = {
            'body':        self.body,
            'tags':        self.tags,
            'created_at':  self.serialize_timestamp(self.created_at),
            'modified_at': self.serialize_timestamp(self.modified_at),
            'id':          self.id
        }

        assert all(type(note_dict[attribute]) in self.SERIALIZED_ATTRIBUTE_TYPES[attribute] for attribute in self.SERIALIZED_ATTRIBUTE_TYPES)
        assert all(type(tag) == str for tag in note_dict['tags'])

        return note_dict

    @classmethod
    def from_dict(cls, note_dict):
        """ Converts raw values from specified dict into a Note.

            The dict is expected to be suitable for serialization and therefore
            the values are expected to be of specific primitive types. """

        missing_properties = set(cls.SERIALIZED_ATTRIBUTE_TYPES.keys()) - set(note_dict.keys())
        if len(missing_properties) > 0:
            raise MissingProperties("Some required properties are missing: {}".format(missing_properties))

        for attribute in cls.SERIALIZED_ATTRIBUTE_TYPES:
            if not type(note_dict[attribute]) in cls.SERIALIZED_ATTRIBUTE_TYPES[attribute]:
                raise WrongAttributeType("Expected the type of attribute {} to be one of {}; got {}".format(
                    attribute, cls.SERIALIZED_ATTRIBUTE_TYPES[attribute], type(note_dict[attribute])
                ))

        for tag in note_dict['tags']:
            if type(tag) != str:
                raise WrongAttributeType("Tag '{}' is not a string".format(tag))

        if any(',' in tag for tag in note_dict['tags']):
            raise InvalidTagCharacter("Commas (,) are not allowed in tags")

        return cls(
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
