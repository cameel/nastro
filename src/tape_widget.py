""" The UI widget that represents a scrollable tape composed of notes """

from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QPushButton, QTreeView, QAbstractItemView, QMessageBox
from PyQt5.QtGui     import QStandardItem, QStandardItemModel
from PyQt5.QtCore    import Qt, QModelIndex, QItemSelection, QItemSelectionModel

from datetime import datetime

from .note_delegate           import NoteDelegate
from .note                    import Note
from .tape_filter_proxy_model import TapeFilterProxyModel
from .model_helpers           import all_items, remove_items
from .note_model_helpers      import item_to_id, set_item_note, all_notes, assign_note_ids

class TapeWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._main_layout    = QVBoxLayout(self)
        self._search_box     = QLineEdit(self)
        self._button_layout  = QHBoxLayout()

        self._view = QTreeView()
        self._view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self._view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._view.setHeaderHidden(True)

        self._add_note_button = QPushButton(self)
        self._add_note_button.setText("New note")

        self._add_child_button = QPushButton(self)
        self._add_child_button.setText("New child")

        self._add_sibling_button = QPushButton(self)
        self._add_sibling_button.setText("New sibling")

        self._delete_note_button = QPushButton(self)
        self._delete_note_button.setText("Delete note")

        self._button_layout.addWidget(self._add_note_button)
        self._button_layout.addWidget(self._add_sibling_button)
        self._button_layout.addWidget(self._add_child_button)
        self._button_layout.addWidget(self._delete_note_button)
        self._button_layout.addStretch()

        self._main_layout.addWidget(self._search_box)
        self._main_layout.addLayout(self._button_layout)
        self._main_layout.addWidget(self._view)

        self._tape_filter_proxy_model = TapeFilterProxyModel()
        self._note_delegate           = NoteDelegate()

        self._tape_model = QStandardItemModel()
        self.set_model(self._tape_model)
        self._view.setItemDelegate(self._note_delegate)
        self._view.setModel(self._tape_filter_proxy_model)

        self._add_note_button.clicked.connect(lambda checked: self.add_and_focus_note())
        self._add_sibling_button.clicked.connect(self._new_sibling_handler)
        self._add_child_button.clicked.connect(self._new_child_handler)
        self._delete_note_button.clicked.connect(self.delete_selected_notes)
        self._search_box.textChanged.connect(self._tape_filter_proxy_model.setFilterFixedString)

    def model(self):
        """ Returns the model that contains all notes managed by the tape.

            The model should be treated as read-only. You can only modify it indirectly through
            the methods provided by TapeWidget. """

        return self._tape_model

    def proxy_model(self):
        """ Returns the model that contains notes matching current filter.

            The model should be treated as read-only. You can only modify it indirectly through
            the methods provided by TapeWidget. """

        return self._tape_filter_proxy_model

    def set_model(self, model):
        assert (
            len(set([item_to_id(item) for item in all_items(model) if item_to_id(item) != None])) ==
            len(    [item_to_id(item) for item in all_items(model) if item_to_id(item) != None])
        )

        # NOTE: If there's an exception in setSourceModel(), we can hope that the source model
        # remains unchanged. That's why we assing to _tape_model only if that instruction succeeds.
        self._tape_filter_proxy_model.setSourceModel(model)
        self._tape_model = model

    def notes(self):
        return all_notes(self._tape_model)

    def assign_ids(self):
        assign_note_ids(self._tape_model)

    def create_empty_note(self):
        return Note(
            body       = "",
            tags       = [],
            created_at = datetime.utcnow()
        )

    def add_note(self, note = None, parent_index = None):
        # NOTE: Remember to use indexes from _tape_model, not _tape_filter_proxy_model here
        assert parent_index == None or self._tape_model.itemFromIndex(parent_index) != None and parent_index.isValid()

        root_item = self._tape_model.invisibleRootItem()
        if parent_index == None:
            parent_item = root_item
        else:
            parent_item = self._tape_model.itemFromIndex(parent_index)

        if note != None:
            assert note not in self.notes()
        else:
            note = self.create_empty_note()

        item = QStandardItem()
        set_item_note(item, note)
        parent_item.appendRow(item)

    def add_and_focus_note(self, parent_proxy_index = None):
        if parent_proxy_index != None:
            parent_index = self._tape_filter_proxy_model.mapToSource(parent_proxy_index)
        else:
            parent_index = None

        self.add_note(parent_index = parent_index)

        if parent_proxy_index != None:
            self._view.expand(parent_proxy_index)

            parent_item = self._tape_model.itemFromIndex(parent_index)
        else:
            parent_item = self._tape_model.invisibleRootItem()

        # NOTE: It's likely that the new note does not match the filter and won't not be present
        # in the proxy model. We want to select it and focus on it so the filter must be cleared.
        # And it must be cleared before taking the index in the proxy because changing the filter
        # may change the set of notes present in the proxy and invalidate the index.
        self.set_filter('')

        new_note_index       = parent_item.child(parent_item.rowCount() - 1).index()
        new_note_proxy_index = self._tape_filter_proxy_model.mapFromSource(new_note_index)

        self.clear_selection()
        self.set_note_selection(new_note_proxy_index, True)
        self._view.scrollTo(new_note_proxy_index)

    def remove_notes(self, indexes):
        remove_items(self._tape_model, indexes)

    def clear(self):
        self._tape_model.clear()

    def set_filter(self, text):
        # NOTE: This triggers textChanged() signal which applies the filter
        self._search_box.setText(text)

    def get_filter(self):
        return self._search_box.text()

    def selected_proxy_indexes(self):
        return self._view.selectedIndexes()

    def selected_indexes(self):
        return [self._tape_filter_proxy_model.mapToSource(proxy_index) for proxy_index in self.selected_proxy_indexes()]

    def set_note_selection(self, proxy_index, select):
        assert proxy_index != None and proxy_index.isValid()
        assert self._tape_model.itemFromIndex(self._tape_filter_proxy_model.mapToSource(proxy_index)) != None

        self._view.selectionModel().select(
            QItemSelection(proxy_index, proxy_index),
            QItemSelectionModel.Select if select else QItemSelectionModel.Deselect
        )

    def clear_selection(self):
        self._view.selectionModel().clear()

    def delete_selected_notes(self):
        self.remove_notes(self.selected_indexes())

    def _new_sibling_handler(self):
        selected_proxy_indexes = self._view.selectedIndexes()
        if len(selected_proxy_indexes) > 1:
            self.clear_selection()
            selected_proxy_indexes = []

        if len(selected_proxy_indexes) == 0 or selected_proxy_indexes[0].parent() == QModelIndex():
            self.add_and_focus_note()
        else:
            self.add_and_focus_note(selected_proxy_indexes[0].parent())

    def add_child_to_selected_element(self):
        selected_proxy_indexes = self._view.selectedIndexes()
        if len(selected_proxy_indexes) != 1:
            return False
        else:
            self.add_and_focus_note(selected_proxy_indexes[0])
            return True

    def _new_child_handler(self):
        added = self.add_child_to_selected_element()
        if not added:
            QMessageBox.warning(self, "Can't add note", "To be able to add a new child note select exactly one parent")
