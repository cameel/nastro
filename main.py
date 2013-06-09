#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Entry point of the application """

from PyKDE4.kdecore import KCmdLineArgs, KAboutData, ki18n
from PyKDE4.kdeui   import KApplication

import sys

from main_window import MainWindow

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

def create_application():
    about_data = create_about_data()
    KCmdLineArgs.init(sys.argv, about_data)

    application = KApplication()
    window      = MainWindow()
    window.show()

    return (about_data, application, window)

if __name__ == '__main__':
    (about_data, application, window) = create_application()

    return_code = application.exec_()
    sys.exit(return_code)
