from PySide6 import QtCore

class ThreadWrapper(QtCore.QThread):
    on_progress = QtCore.Signal(float, str)

    def __init__(self, work):
        super().__init__()
        self.__work = work

    def run(self):
        self.__work(self.on_progress)

