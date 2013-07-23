""" The UI widget that represents a scrollable tape composed of notes """

from PyQt4.QtGui  import QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QPushButton, QListView, QAbstractItemView
from PyQt4.QtGui  import QStandardItem, QStandardItemModel, QItemSelection, QItemSelectionModel
from PyQt4.QtCore import SIGNAL, Qt

from datetime import datetime

from .note_delegate           import NoteDelegate
from .note                    import Note
from .tape_filter_proxy_model import TapeFilterProxyModel

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

        self.connect(self._add_note_button,    SIGNAL('clicked()'),                    self._new_note_handler)
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

    def note(self, position):
        assert 0 <= position < self._tape_model.rowCount()

        note = self._tape_model.item(position).data(Qt.EditRole)
        assert isinstance(note, Note)

        return note

    def note_count(self):
        return self._tape_model.rowCount()

    def notes(self):
        for i in range(self._tape_model.rowCount()):
            note = self._tape_model.item(i).data(Qt.EditRole)
            assert isinstance(note, Note)

            yield note

    def add_note(self, note = None):
        if note != None:
            assert self._find_note(note) == None
        else:
            note = Note(
                title       = "Note {}".format(self._tape_model.rowCount() + 1),
                body        = "",
                tags        = [],
                created_at  = datetime.utcnow()
            )

        root_item = self._tape_model.invisibleRootItem()
        item = QStandardItem()
        item.setData(note, Qt.EditRole)
        root_item.appendRow(item)

    def remove_note(self, note):
        # TODO: Removal by index may be more efficient for large lists
        note_position = self._find_note(note)
        if note_position != None:
            self._tape_model.takeRow(note_position)

    def _find_note(self, note_to_find):
        try:
            return next(i for (i, note) in enumerate(self.notes()) if note == note_to_find)
        except StopIteration:
            return None

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

    def selected_note_positions(self):
        selected_indexes = self._view.selectedIndexes()

        result = []
        for index in selected_indexes:
            result.append(index.row())

        return result

    def select_note(self, position):
        index = self._tape_filter_proxy_model.index(position, 0)
        self._view.selectionModel().select(
            QItemSelection(index, index),
            QItemSelectionModel.Select
        )

    def deselect_note(self, position):
        index = self._tape_filter_proxy_model.index(position, 0)
        self._view.selectionModel().select(
            QItemSelection(index, index),
            QItemSelectionModel.Deselect
        )

    def clear_selection(self):
        self._view.selectionModel().clear()

    def _delete_note_handler(self):
        positions = sorted(self.selected_note_positions(), reverse = True)
        assert positions == sorted(set(positions), reverse = True), "There are duplicates"

        # NOTE: The list must be iterated in reversed order because positions of all elements
        # past the deleted one shift by one and we'd have to account for that otherwise.
        for position in positions:
            self._tape_model.removeRow(position)

    def _new_note_handler(self):
        self.add_note()

        new_note_position = self._tape_filter_proxy_model.rowCount() - 1
        new_note_index    = self._tape_filter_proxy_model.index(new_note_position, 0)

        self.set_filter('')
        self.clear_selection()
        self.select_note(new_note_position)
        self._view.scrollTo(new_note_index)
