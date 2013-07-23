from itertools import islice

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

def subtree_items(root):
    model = root.model()
    item  = root
    while True:
        yield item

        if item.rowCount() > 0:
            item = item.child(0)
        else:
            while item.parent() not in [root, None] and item.row() >= item.parent().rowCount() - 1:
                assert item.parent() != QModelIndex(), "This function operaties on items, not indexes"
                item = item.parent()

            # This is a workaround for an old bug in Qt that causes the parent() of top-level
            # items of QStandardItemModel to return None rather than invisibleRootItem().
            # This was supposedly fixed a year ago but I'm experiencing it with python-pyqt4 4.10.2
            # and qt4 4.8.5 on Arch Linux.
            # See https://bugreports.qt-project.org/browse/QTBUG-18785
            if item.parent() == None:
                parent = root
            else:
                parent = item.parent()

            if item.row() >= parent.rowCount() - 1:
                break

            item = parent.child(item.row() + 1)

def all_items(model):
    return islice(subtree_items(model.invisibleRootItem()), 1, None)
