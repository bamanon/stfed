from PySide6 import QtCore, QtGui, QtWidgets


class ImageDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter: QtGui.QPainter, opt: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        decoration = index.data(QtCore.Qt.DecorationRole)
        if decoration is not None:
            if isinstance(decoration, QtGui.QIcon):
                original_size = decoration.availableSizes()[0]
                h1 = original_size.height()
                w1 = original_size.width()
                w2 = opt.rect.width()
                h2 = opt.rect.height()
                vscale = h2/h1
                hscale = w2/w1
                scale = min(hscale, vscale)
                h1prim = int(scale * h1)
                w1prim = int(scale * w1)
                decoration = decoration.pixmap(QtCore.QSize(w1prim, h1prim))
            if isinstance(decoration, QtGui.QPixmap):
                w1prim = decoration.width()
                h1prim = decoration.height()
                origin_x = opt.rect.center().x() - w1prim // 2
                origin_y = opt.rect.center().y() - h1prim // 2
                painter.drawPixmap(QtCore.QPoint(origin_x, origin_y), decoration)
                return
        super().paint(painter, opt, index)
        