""" A Qt delegate for models dealing with Note objects """

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QItemDelegate, QStyle
from PyQt5.QtGui     import QPixmap, QPen, QPalette
from PyQt5.QtCore    import Qt, QSize, QPoint, QRect

from datetime import datetime

from .note_edit   import NoteEdit
from .note_widget import NoteWidget
from .note        import Note

class NoteDelegate(QItemDelegate):
    SELECTION_PEN_WIDTH = 2

    class NoteEditContainer(QWidget):
        def __init__(self, parent = None):
            super().__init__(parent)

            self.__editor = NoteEdit(self)

            # It seems that some views (e.g. QTreeView) use QPalette.Base as their background role.
            # It makes sense for them but not for our editor - it forces the text fields and the
            # area around them to be the same color. We have to explicitly revert it to the original
            # state to be able to change on of these colors without changing the other.
            self.setBackgroundRole(QPalette.Window)

            self.__editor.setAutoFillBackground(True)

            layout = QVBoxLayout()
            layout.addWidget(self.__editor)
            layout.addStretch()
            self.setLayout(layout)

            layout.setContentsMargins(0, 0, 0, 0)

        def editor(self):
            return self.__editor

        def set_margin_size(self, margin_size):
            self.setContentsMargins(
                margin_size,
                margin_size,
                margin_size,
                margin_size
            )

    def __init__(self, parent = None):
        super().__init__(parent)

        # A widget painted in display mode. This is NOT the editor widget.
        self._display_widget = NoteWidget()

    def createEditor(self, parent, option, index):
        editor_container = self.NoteEditContainer(parent)
        editor_container.set_margin_size(self.SELECTION_PEN_WIDTH)

        return editor_container

    def setEditorData(self, editor_container, index):
        value = index.model().data(index, Qt.EditRole)
        assert isinstance(value, Note), "Note instance expected, got {}: '{}'".format(value.__class__, value)

        editor_container.editor().load_note(value)

    def setModelData(self, editor_container, model, index):
        value = editor_container.editor().dump_note()
        assert isinstance(value, Note), "Note instance expected, got {}: '{}'".format(value.__class__, value)

        if value.to_dict() != model.data(index, Qt.EditRole).to_dict():
            model.setData(index, value, Qt.EditRole)

            # NOTE: sizeHintChanged() is quite heavy if there are a lot of notes becase it makes
            # some views (most notably QListView) call sizeHint() on every model item.
            # We want to emit it only if the size actually changed.
            self.sizeHintChanged.emit(index)

    def _draw_focus_frame(self, painter, rect, width):
        pen = QPen()
        pen.setWidth(width)
        pen.setStyle(Qt.DashLine)

        painter.setPen(pen)
        painter.drawRect(QRect(rect.x() + width // 2, rect.y() + width // 2, rect.width() - width, rect.height() - width))

    def paint(self, painter, option, index):
        value = index.model().data(index, Qt.DisplayRole)
        assert isinstance(value, Note), "Note instance expected, got {}: '{}'".format(value.__class__, value)

        if option.rect.width() > 0 and option.rect.height() > 0:
            painter.save()

            # FIXME: It would be more efficient to create the widget in __init__() and then just
            # replace the note with load_note() but it does not work. Its labels retain don't update
            # their height immediately after setText(), probably because they're using signals to
            # communicate with the layout and these signals are processed asynchronously by Qt event loop.
            # As a result, the widget ignores resize() call and remains at the size corresponding to the
            # previous note - the look of the note is different depending on which other note was painted before.
            display_widget = NoteWidget()
            display_widget.load_note(value)
            display_widget.resize(option.rect.size())

            # If the widget refuses to change its size, it might indicate a layout problem (see note above).
            assert display_widget.size() == option.rect.size(), "Wanted to resize widget to {}x{} but it insists on {}x{}".format(
                option.rect.size().width(),    option.rect.size().height(),
                display_widget.size().width(), display_widget.size().height()
            )

            # FIXME: Draw the widget directly, without the intermediate pixmap
            pixmap = QPixmap(option.rect.size())
            display_widget.render(pixmap)
            painter.drawPixmap(option.rect.topLeft(), pixmap)

            if option.state & QStyle.State_Selected:
                self._draw_focus_frame(painter, option.rect, self.SELECTION_PEN_WIDTH)

            painter.restore()

    def updateEditorGeometry(self, editor_container, option, index):
        if editor_container.parent() != None:
            # Put the bottom of the editor at the same level as bottom of the tree view
            assert editor_container.parent().height() > option.rect.y()

            height = editor_container.parent().height() - option.rect.y()
        else:
            # It's unlikely for the view not to provide a parent widget but if it doesn't for some reason,
            # just use provided option.rect
            height = option.rect.height()

        editor_container.setGeometry(QRect(
            option.rect.x(),
            option.rect.y(),
            option.rect.width(),
            height
        ))

    def sizeHint(self, option, index):
        value = index.model().data(index, Qt.DisplayRole)
        assert isinstance(value, Note), "Note instance expected, got {}: '{}'".format(value.__class__, value)

        # NOTE: While there are problems with updating widget size after changing label text (see note in paint()),
        # sizeHint() works correctly so it's not necessary to create a new widget here. It's important because
        # sizeHint() is called much more often than paint() and must execute quickly.
        self._display_widget.load_note(value)

        # Ignore width suggested by widget. We want the label to be cut off at some point if it's too long.
        # We don't want the horizontal scroll bar inside the list view.
        hint = self._display_widget.sizeHint()
        return QSize(option.rect.width(), hint.height())
