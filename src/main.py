#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Entry point of the application """

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore    import QTimer

import sys
import os

from .main_window import MainWindow

application = None
window      = None

def create_application():
    global application
    global window

    application = QApplication(sys.argv)
    window      = MainWindow()
    window.show()

    return (application, window)

def start_signal_timer():
    # NOTE: Python does not process signals while executing C extensions.
    # This prevents us from stopping the application with Ctrl+C while the
    # Qt loop is running. To let the application process signals we need to
    # periodically pass control from Qt to the interpreter. This timer is a
    # hack to achieve just that.
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    return timer

def global_exception_handler(type, value, traceback):
    global original_excepthook
    global application
    global window

    if type != KeyboardInterrupt:
        # The standard exception hook prints the traceback to the stdout. We want that.
        # If some other component has installed its own exception hook before us, we probably
        # want it executed too. Hopefully it calls the standard one.
        original_excepthook(type, value, traceback)

        QMessageBox.critical(window, "Unhandled exception: " + type.__name__, str(value))
    else:
        print("SIGINT")
        sys.exit(1)

def main():
    global original_excepthook

    (application, window) = create_application()

    original_excepthook = sys.excepthook
    sys.excepthook      = global_exception_handler

    timer = start_signal_timer()

    return_code = application.exec_()
    sys.exit(return_code)
