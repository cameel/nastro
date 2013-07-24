from PyQt4.QtGui  import QSortFilterProxyModel
from PyQt4.QtCore import QRegExp

from .note import Note

class TapeFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        # FIXME: This filter is very slow for large amounts of data (like 3k+ notes).
        # index() and data() calls below seem to be quite heavy - the filter is slow even
        # if I return immediately after them.
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        note  = source_model.data(index)
        assert isinstance(note, Note)

        return self.__class__.note_matches(self.filterRegExp(), note)

    def setFilterFixedString(self, fixed_string):
        # In case of fixed strings we want case-insensitive match
        super().setFilterFixedString(fixed_string)

        regex = self.filterRegExp()
        super().setFilterRegExp(QRegExp(regex.pattern(), False, regex.patternSyntax()))

    @classmethod
    def note_matches(cls, regex, note):
        for text_component in [note.title] + note.tags + [note.body]:
            if regex.indexIn(text_component) != -1:
                return True

        return False
