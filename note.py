""" A class that represents a single note """

class Note:
    def __init__(self, title, body, tags, timestamp):
        self.title     = title
        self.body      = body
        self.tags      = tags
        self.timestamp = timestamp
