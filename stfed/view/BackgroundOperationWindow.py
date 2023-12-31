from PySide6 import QtCore, QtGui, QtWidgets

from stfed.view.autogenerated.Ui_BackgroundOperationWindow import Ui_BackgroundOperationWindow


class BackgroundOperationWindow(QtWidgets.QWidget, Ui_BackgroundOperationWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # sizePolicy.xxxPolicy.Fixed apparently does nothing
        self.setFixedSize(self.size())

    def set_progress(self, progress: float, comment: str) -> None:
        self.label.setText(comment)
        self.progress_bar.setValue(int(progress * 100))

    def done(self) -> None:
        self.hide()

