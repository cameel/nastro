""" The UI widget that represents a scrollable tape composed of notes """

from PyQt4.QtGui  import QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QPushButton, QListView, QAbstractItemView
from PyQt4.QtGui  import QStandardItem, QStandardItemModel, QItemSelection, QItemSelectionModel
from PyQt4.QtCore import SIGNAL, Qt

from datetime import datetime

from .note_delegate           import NoteDelegate
from .note                    import Note
from .tape_filter_proxy_model import TapeFilterProxyModel
from .model_helpers           import remove_items, all_items

class TapeWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._main_layout    = QVBoxLayout(self)
        self._search_box     = QLineEdit(self)
        self._button_layout  = QHBoxLayout()

        self._view = QListView()
        self._view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self._view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self._add_note_button = QPushButton(self)
        self._add_note_button.setText("New note")

        self._delete_note_button = QPushButton(self)
        self._delete_note_button.setText("Delete note")

        self._button_layout.addWidget(self._add_note_button)
        self._button_layout.addWidget(self._delete_note_button)
        self._button_layout.addStretch()

        self._main_layout.addWidget(self._search_box)
        self._main_layout.addLayout(self._button_layout)
        self._main_layout.addWidget(self._view)

        self._tape_model              = QStandardItemModel()
        self._tape_filter_proxy_model = TapeFilterProxyModel()
        self._note_delegate           = NoteDelegate()

        self._tape_filter_proxy_model.setSourceModel(self._tape_model)
        self._view.setItemDelegate(self._note_delegate)
        self._view.setModel(self._tape_filter_proxy_model)

        self.connect(self._add_note_button,    SIGNAL('clicked()'),                    self.add_and_focus_note)
        self.connect(self._delete_note_button, SIGNAL('clicked()'),                    self._delete_note_handler)
        self.connect(self._search_box,         SIGNAL('textChanged(const QString &)'), self._tape_filter_proxy_model.setFilterFixedString)

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

    def notes(self):
        for item in all_items(self._tape_model):
            assert isinstance(item.data(Qt.EditRole), Note)
            yield item.data(Qt.EditRole)

    def create_empty_note(self):
        return Note(
            title       = "Note {}".format(self._tape_model.rowCount() + 1),
            body        = "",
            tags        = [],
            created_at  = datetime.utcnow()
        )


    def add_note(self, note = None):
        if note != None:
            assert note not in self.notes()
        else:
            note = self.create_empty_note()

        root_item = self._tape_model.invisibleRootItem()
        item = QStandardItem()
        item.setData(note, Qt.EditRole)
        root_item.appendRow(item)

    def add_and_focus_note(self):
        self.add_note()

        # NOTE: It's likely that the new note does not match the filter and won't not be present
        # in the proxy model. We want to select it and focus on it so the filter must be cleared.
        # And it must be cleared before taking the index in the proxy because changing the filter
        # may change the set of notes present in the proxy and invalidate the index.
        self.set_filter('')

        new_note_position    = self._tape_filter_proxy_model.rowCount() - 1
        new_note_proxy_index = self._tape_filter_proxy_model.index(new_note_position, 0)

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

    def dump_notes(self):
        notes = []
        for note in self.notes():
            notes.append(note.to_dict())

        return notes

    def load_notes(self, notes):
        self.clear()

        try:
            for note in notes:
                self.add_note(note)
        except:
            self.clear()
            raise

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

    def _delete_note_handler(self):
        self.remove_notes(self.selected_indexes())



