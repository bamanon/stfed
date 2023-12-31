from PySide6 import QtCore, QtGui, QtWidgets

import stfed.factories.sqb
from stfed.view.autogenerated.Ui_SqbResourcePreview import Ui_SqbResourcePreview


class SqbResourcePreview(QtWidgets.QWidget, Ui_SqbResourcePreview):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.entries_table.setHorizontalHeaderLabels(["Id", "Text"])

    def set_model(self, resource):
        collection = stfed.factories.sqb.parse(resource)
        self.entries_table.setRowCount(0)
        self.entries_table.setRowCount(len(collection.squibs))
        for rowid, (key, value) in enumerate(collection.squibs.items()):
            it = QtWidgets.QTableWidgetItem(str(key))
            it.setTextAlignment(QtGui.Qt.AlignmentFlag.AlignTop)
            self.entries_table.setItem(rowid, 0, it)
            self.entries_table.setItem(rowid, 1, QtWidgets.QTableWidgetItem(value))
        self.entries_table.resizeRowsToContents()

