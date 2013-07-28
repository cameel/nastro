from PyQt5.QtCore import Qt

from .note          import Note
from .model_helpers import all_items

def item_to_note(item):
    note = item.data(Qt.EditRole)
    assert isinstance(note, Note)
    return note

def item_to_id(item):
    return item_to_note(item).id
