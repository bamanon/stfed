from PySide6 import QtCore, QtGui, QtWidgets

import stfed.model
import stfed.factories.fon
from stfed.view.autogenerated.Ui_FonResourcePreview import Ui_FonResourcePreview
from stfed.repos.user_preferences import repo as user_preferences_repo


class FonResourcePreview(QtWidgets.QWidget, Ui_FonResourcePreview):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__pixmap = None
        self.__subscriptions = []
        self.__subscriptions.append(
            user_preferences_repo.values().map_subscribe(
                lambda p: p.double_width_image_preview,
                self.__on_double_width_preview_pref_changed))


    def set_model(self, resource: stfed.model.Resource):
        fon = stfed.factories.fon.parse(resource)
        content = stfed.factories.fon.export_as_png(fon)
        self.__pixmap = QtGui.QPixmap()
        self.__pixmap.loadFromData(content, 'PNG')

        adj = 2 if user_preferences_repo.get().double_width_image_preview else 1
        pixmap = self.__pixmap.scaled(self.__pixmap.width() * adj * 2, self.__pixmap.height() * 2)
        self.label.setPixmap(pixmap)
      

    def __on_double_width_preview_pref_changed(self, new_value: bool):
        if self.__pixmap is None:
            return
        adj = 2 if new_value else 1
        pixmap = self.__pixmap.scaled(self.__pixmap.width() * adj * 2, self.__pixmap.height() * 2)
        self.label.setPixmap(pixmap)
            

    def destroy(self, destroyWindow: bool=True, destroySubWindows: bool=True) -> None:
        for s in self.__subscriptions:
            s.unsubscribe()
        return super().destroy(destroyWindow, destroySubWindows)
