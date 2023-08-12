#!/usr/bin/env python3

from PySide6 import QtGui, QtWidgets

import stfed.repos.user_preferences
import stfed.view.MainWindow


def main():
    try:
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID('bamanon.stfed')
    except ImportError:
        pass

    app = QtWidgets.QApplication([])
    app.setWindowIcon(QtGui.QIcon('resources/icon.ico'))

    if QtGui.QIcon.themeName() is None:
        QtGui.QIcon.setThemeSearchPaths(QtGui.QIcon.themeSearchPaths() + ["resources/themes"])
        theme_name = 'breeze'
        background_lightness = QtGui.QColor.lightnessF(app.palette().color(QtGui.QPalette.ColorRole.Window))
        if background_lightness < 0.5:
            theme_name = 'breeze-dark'
        QtGui.QIcon.setThemeName(theme_name)

    w = stfed.view.MainWindow.MainWindow()
    w.show()
    app.exec()
    stfed.repos.user_preferences.repo.commit()


main()
