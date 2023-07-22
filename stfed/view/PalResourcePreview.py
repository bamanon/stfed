import wave
import io

from PySide6 import QtCore, QtGui, QtWidgets

import stfed.model
import stfed.factories.pal
from stfed.view.autogenerated.Ui_PalResourcePreview import Ui_PalResourcePreview


class PalResourcePreview(QtWidgets.QWidget, Ui_PalResourcePreview):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


    def set_model(self, resource: stfed.model.Resource):
        palette = stfed.factories.pal.parse(resource.data())
        html = stfed.factories.pal.export_as_html(palette)
        self.label.setText(html)
