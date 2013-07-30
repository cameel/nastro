from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui  import QStandardItem, QStandardItemModel

from collections import deque

from .note          import Note, MissingProperties
from .model_helpers import all_items

class EmptyNoteId(MissingProperties):          pass
class MissingParentId(MissingProperties):      pass
class MissingPrevSiblingId(MissingProperties): pass
class MissingNote(Exception):                  pass
class SiblingCycle(Exception):                 pass
class ParentCycle(Exception):                  pass
class InconsistentParentIds(Exception):        pass
class ConflictingSiblingIds(Exception):        pass

def item_to_note(item):
    note = item.data(Qt.EditRole)
    assert isinstance(note, Note)
    return note

def item_to_id(item):
    return item_to_note(item).id

def all_notes(model):
    for item in all_items(model):
        assert isinstance(item.data(Qt.EditRole), Note)
        yield item.data(Qt.EditRole)

def assign_note_ids(model):
    assert (
        len(set([item_to_id(item) for item in all_items(model) if item_to_id(item) != None])) ==
        len(    [item_to_id(item) for item in all_items(model) if item_to_id(item) != None])
    )

    max_id        = 0
    num_empty_ids = 0
    for note in all_notes(model):
        if note.id != None:
            max_id = max(max_id, note.id)
        else:
            num_empty_ids += 1

    if num_empty_ids > 0:
        next_id = max_id + 1
        for note in all_notes(model):
            if note.id == None:
                note.id = next_id
                next_id += 1

    return num_empty_ids

def dump_notes(model):
    assert (
        len(set([item_to_id(item) for item in all_items(model) if item_to_id(item) != None])) ==
        len(    [item_to_id(item) for item in all_items(model) if item_to_id(item) != None])
    )

    assign_note_ids(model)

    raw_notes = []
    for item in all_items(model):
        note = item.data(Qt.EditRole)
        assert note.id != None

        note_dict = note.to_dict()
        assert not 'parent_id'       in note_dict
        assert not 'prev_sibling_id' in note_dict

        # There is an old bug in Qt that causes the parent() of top-level items in QStandardItemModel
        # to return None rather than invisibleRootItem(). This was supposedly fixed a year ago but I'm
        # experiencing it with both python-pyqt4 4.10.2/qt4 4.8.5 and pyqt5 5.0/qt5 5.1.0 on Arch Linux.
        # See https://bugreports.qt-project.org/browse/QTBUG-18785
        if item.parent() in [None, model.invisibleRootItem()]:
            note_dict['parent_id']       = None
            note_dict['prev_sibling_id'] = model.item(item.row() - 1).data(Qt.EditRole).id if item.row() > 0 else None
        else:
            note_dict['parent_id']       = item.parent().data(Qt.EditRole).id
            note_dict['prev_sibling_id'] = item.parent().child(item.row() - 1).data(Qt.EditRole).id if item.row() > 0 else None

        raw_notes.append(note_dict)

    return raw_notes

def load_notes(raw_notes):
    item_map = {}
    for note_dict in raw_notes:
        note = Note.from_dict(note_dict)

        if note.id == None:
            raise EmptyNoteId("Found a note with empty id: {} (created from: {})".format(note, note_dict))
        if not 'parent_id' in note_dict:
            raise MissingParentId("parent_id attribute is missing for note {}".format(note.id))
        if not 'prev_sibling_id' in note_dict:
            raise MissingPrevSiblingId("prev_sibling_id attribute is missing for note {}".format(note.id))

        item = QStandardItem()
        item.setData(note, Qt.EditRole)
        item_map[note.id] = (item, note_dict['parent_id'], note_dict['prev_sibling_id'])

    new_model = QStandardItemModel()
    inserted  = set()
    for sequential_id in item_map.keys():
        priority_ids = deque([sequential_id])
        while len(priority_ids) > 0:
            id = priority_ids[-1]
            assert id != None
            assert id in item_map

            if id in inserted:
                priority_ids.pop()
            else:
                (item, parent_id, prev_sibling_id) = item_map[id]
                assert item_to_id(item) == id

                if prev_sibling_id != None and prev_sibling_id not in inserted:
                    # All preceding siblings need to be inserted before an item.
                    # Parent does not have to be inserted before the item though.

                    if prev_sibling_id not in item_map:
                        raise MissingNote("Note with id {} is missing".format(id))

                    if prev_sibling_id in priority_ids:
                        raise SiblingCycle("Children of note {} form a cycle rather than a list".format(parent_id))

                    priority_ids.append(prev_sibling_id)
                else:
                    assert prev_sibling_id == None or prev_sibling_id in item_map

                    if parent_id != None and parent_id not in item_map:
                        raise MissingNote("Note with id {} is missing".format(parent_id))

                    if prev_sibling_id != None and parent_id != item_map[prev_sibling_id][1]:
                        raise InconsistentParentIds("Notes {} and {} are marked as siblngs but have different parents: {} and {} respectively".format(
                            id, prev_sibling_id, parent_id, item_map[prev_sibling_id][1]
                        ))

                    parent = item_map[parent_id][0] if parent_id != None else new_model

                    assert prev_sibling_id == None or parent.rowCount() > 0
                    assert prev_sibling_id == None or item_to_id(item_map[prev_sibling_id][0]) == prev_sibling_id

                    if (prev_sibling_id == None and parent.rowCount() > 0 or
                        prev_sibling_id != None and parent_id == None and item_to_id(parent.item(parent.rowCount() - 1))  != prev_sibling_id or
                        prev_sibling_id != None and parent_id != None and item_to_id(parent.child(parent.rowCount() - 1)) != prev_sibling_id):

                        raise ConflictingSiblingIds("At least one other note has the same prev_sibling_id as note {}".format(id))

                    parent.appendRow(item)
                    inserted.add(id)
                    priority_ids.pop()

    if len(list(all_items(new_model))) != len(raw_notes):
        raise ParentCycle("Not all items are reachable from the top level of the new model. There must be a vertical cycle somewhere.")

    return new_model
