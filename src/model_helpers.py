from PyQt4.QtCore import QModelIndex

def level(item):
    """ Returns a nesting level of an item. It's mostly intended to be used with
        QModelIndex but it should work with anything that has a parent() method
        that returns None at the top level and that is organized like a tree.

        Top-level items are at level 0. Each nesting level adds 1.

        Note that the item returned by QStandardItemModel.invisibleRootItem() is also
        at level 0 even though it's meant to act as a parent for the top-level items.
        That's because its parent() method reports that it does not have a parent. """

    assert item not in [None, QModelIndex()]

    level = 0
    while item.parent() not in [None, QModelIndex()]:
        item = item.parent()
        level += 1

    return level

def tree_path(item):
    """ Returns a list of row numers pertaining to the item and all its ancestors on the
        path to the root.

        Works for both model items and model indexes. Should work for anything that has
        parent() and row() methods and is organized like a tree. """

    assert item not in [None, QModelIndex()]

    path = [item.row()]
    while item.parent() not in [None, QModelIndex()]:
        item = item.parent()
        path.append(item.row())

    return path
