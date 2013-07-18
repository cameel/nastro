""" A Qt delegate for models dealing with Note objects """

from PyQt4.QtGui  import QItemDelegate, QStyle, QPixmap, QPen
from PyQt4.QtCore import Qt, QSize, QPoint, QRect

from datetime import datetime

from .note_widget import NoteWidget
from .note        import Note

class NoteDelegate(QItemDelegate):
    def __init__(self, parent = None):
        super().__init__(parent)

        # A widget painted in display mode. This is NOT the editor widget.
        self._display_widget = NoteWidget()

    def createEditor(self, parent, option, index):
        return NoteWidget(parent)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        assert isinstance(value, Note), "Note instance expected, got {}: '{}'".format(value.__class__, value)

        editor.load_note(value)

    def setModelData(self, editor, model, index):
        value = editor.dump_note()
        assert isinstance(value, Note), "Note instance expected, got {}: '{}'".format(value.__class__, value)

        model.setData(index, value, Qt.EditRole)

    def _draw_focus_frame(self, painter, rect, width):
        pen = QPen()
        pen.setWidth(width)
        pen.setStyle(Qt.DashLine)

        painter.setPen(pen)
        painter.drawRect(QRect(rect.x() + width // 2, rect.y() + width // 2, rect.width() - width, rect.height() - width))

    def paint(self, painter, option, index):
        value = index.model().data(index, Qt.DisplayRole)
        assert isinstance(value, Note), "Note instance expected, got {}: '{}'".format(value.__class__, value)

        painter.save()

        self._display_widget.load_note(value)
        self._display_widget.resize(option.rect.size())

        # FIXME: Draw the widget directly, without the intermediate pixmap
        pixmap = QPixmap(option.rect.size())
        self._display_widget.render(pixmap)
        painter.drawPixmap(option.rect.topLeft(), pixmap)

        if option.state & QStyle.State_Selected:
            self._draw_focus_frame(painter, option.rect, 2)

        painter.restore()

    def updateEditorGeometry(self, editor, option, index):
        # FIXME: Why do I have to make the editor 3 pixels smaller on each side to make it have the same size
        # as the one I draw in paint()?
        editor.setGeometry(QRect(option.rect.x() + 3, option.rect.y() + 3, option.rect.width() - 6, option.rect.height() - 6))

    def sizeHint(self, option, index):
        value = index.model().data(index, Qt.DisplayRole)
        assert isinstance(value, Note), "Note instance expected, got {}: '{}'".format(value.__class__, value)

        self._display_widget.load_note(value) 
        return self._display_widget.sizeHint()
