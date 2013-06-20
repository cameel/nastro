#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Entry point of the application """

from PyKDE4.kdecore import KCmdLineArgs, KAboutData, ki18n
from PyKDE4.kdeui   import KApplication
from PyQt4.QtGui    import QMessageBox
from PyQt4.QtCore   import QTimer

import sys

from main_window import MainWindow

application = None
window      = None

def create_about_data():
    app_name     = "Nastro"
    catalog      = ""
    program_name = ki18n("Nastro")
    version      = "0.0.1"
    description  = ki18n("Note organizer/journal")
    license      = KAboutData.License_GPL
    # FIXME: ki18n can't handle "Śliwak"
    copyright    = ki18n("(c) 2013 Kamil Sliwak")
    # FIXME: Is this really a good way to pass empty license text? Maybe just an empty string?
    text         = ki18n("none")
    # TODO: home page
    home_page    = ""
    bug_email    = "cameel2/at/gmail/com"

    return KAboutData(app_name, catalog, program_name, version, description, license, copyright, text, home_page, bug_email)

def setup_command_line():
    about_data = create_about_data()
    KCmdLineArgs.init(sys.argv, about_data)

    config = {}
    return (about_data, config)

def create_application():
    global application
    global window

    application = KApplication()
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

    (about_data, command_line_config) = setup_command_line()
    (application, window)             = create_application()

    original_excepthook = sys.excepthook
    sys.excepthook      = global_exception_handler

    timer = start_signal_timer()

    return_code = application.exec_()
    sys.exit(return_code)

if __name__ == '__main__':
    main()
