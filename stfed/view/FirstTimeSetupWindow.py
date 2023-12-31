import dataclasses

from PySide6 import QtCore, QtGui, QtWidgets

import stfed.repos.user_preferences
from stfed.view.autogenerated.Ui_FirstTimeSetupWindow import Ui_FirstTimeSetupWindow


class FirstTimeSetupWindow(QtWidgets.QWidget, Ui_FirstTimeSetupWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # sizePolicy.xxxPolicy.Fixed apparently does nothing
        self.setFixedSize(self.size())
        self.__user_preferences_repo = stfed.repos.user_preferences.repo
        self.done_button.clicked.connect(self.__done_button_clicked)
        self.browse_button.clicked.connect(self.__browse_button_clicked)
        self.directories_text_edit.textChanged.connect(self.__directories_text_edit_text_changed)

    def __done_button_clicked(self):
        lookup_paths = [
            l.strip()
            for l in self.directories_text_edit.toPlainText().split('\n')
            if len(l.strip()) > 0
        ]
        #TODO: validation?
        prefs = self.__user_preferences_repo.get()
        prefs = dataclasses.replace(prefs, lookup_paths=lookup_paths)
        self.__user_preferences_repo.update(prefs)
        self.close()

    def __directories_text_edit_text_changed(self):
        new_text = "Continue" if len(self.directories_text_edit.toPlainText()) > 0 else "Skip"
        self.done_button.setText(new_text)

    def __browse_button_clicked(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory(self)
        if filename is None or filename == '':
            return
        text = self.directories_text_edit.toPlainText()
        if filename in text.split('\n'):
            return
        if len(text) > 0 and not text.endswith('\n'):
            text = text + '\n'
        text = text + filename
        self.directories_text_edit.setPlainText(text)
