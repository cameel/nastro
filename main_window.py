from PyKDE4.kdeui   import KMainWindow, KDatePicker
from PyQt4.QtGui    import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QTextEdit

class MainWindow(object):
    def __init__(self):
        self.main_panel = QWidget()

        self.window = KMainWindow()
        self.window.setCentralWidget(self.main_panel)

    def show(self):
        self.window.show()
