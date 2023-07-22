#!/usr/bin/env python3

from PySide6.QtWidgets import QApplication
from PySide6 import QtGui

import stfed.repos.user_preferences
from stfed.view.MainWindow import MainWindow


def main():
    app = QApplication([])
    app.setWindowIcon(QtGui.QIcon('resources/icon.ico'))
    w = MainWindow()
    w.show()
    app.exec()
    stfed.repos.user_preferences.repo.commit()


main()
