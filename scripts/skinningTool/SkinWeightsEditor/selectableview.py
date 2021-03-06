# -*- coding: utf-8 -*-
# SkinWeights command and component editor
# Copyright (C) 2018 Trevor van Hoof
# Website: http://www.trevorius.com
#
# pyqt attribute sliders
# Copyright (C) 2018 Daniele Niero
# Website: http://danieleniero.com/
#
# neighbour finding algorythm
# Copyright (C) 2018 Jan Pijpers
# Website: http://www.janpijpers.com/
#
# skinningTools and UI
# Copyright (C) 2018 Perry Leijten
# Website: http://www.perryleijten.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General
# Public License.
#--------------------------------------------------------------------------------------
from ..qtUtil import *
            
from skinningTool.SkinWeightsEditor import view
from functools import partial

class SkinWeightsSelectable(view.SkinWeightsViewport):
    def __init__(self, *args):
        super(SkinWeightsSelectable, self).__init__(*args)
        self._selectionArea = None
        self.__isPressed = False

    def mousePressEvent(self, event):
        self.__isPressed = True
        x, y = self.rowColumnAt(event.pos())
        self._selectionArea = [x, y, x, y]
        self.repaint()

    def mouseMoveEvent(self, event):
        if self.__isPressed == False or self._selectionArea == None:
            return
        x, y = self.rowColumnAt(event.pos())
        self._selectionArea = [
            min(x, self._selectionArea[0]),
            min(y, self._selectionArea[1]),
            max(x, self._selectionArea[2]),
            max(y, self._selectionArea[3])]
        self.repaint()

    def mouseReleaseEvent(self, event):
        self.__isPressed = False
        x, y = self.rowColumnAt(event.pos())
        self._selectionArea = [
            min(x, self._selectionArea[0]),
            min(y, self._selectionArea[1]),
            max(x, self._selectionArea[2]),
            max(y, self._selectionArea[3])]
        self.repaint()

    def setSelectionArea(self, left, top, right, bottom):
        self._selectionArea = [min(left, right), min(top, bottom), max(left, right), max(top, bottom)]
        self.repaint()

    def clearSelection(self):
        self._selectionArea = None
        self.repaint()

    def isSelected(self, col, row):
        if self._selectionArea is None:
            return False
        if col < self._selectionArea[0] or col > self._selectionArea[2] or \
            row < self._selectionArea[1] or row > self._selectionArea[3]:
            return False
        return True

    def _drawRow(self, painter, startCol, endCol, row, x, y, colCount):
        while startCol < endCol:
            v = self._model.value(startCol, row)

            pen = painter.pen()
            if self._model.isLockedColumn(startCol):
                painter.setPen(Qt.gray)
            elif self.isSelected(startCol, row):
                r = QRect(x, y, self.CELL_WIDTH - 1, self.CELL_HEIGHT - 1)
                pen = painter.pen()
                painter.setPen(Qt.NoPen)
                if QT_VERSION == "pyqt4":
                    painter.setBrush(QPalette(QPalette.Active).highlight())
                else:
                    painter.setBrush(QApplication.palette('').highlight())
                painter.drawRect(r)
                painter.setBrush(Qt.NoBrush)
                painter.setPen(pen)

            r = QRect(x + self.PADDING, y, self.CELL_WIDTH - self.PADDING - 1, self.CELL_HEIGHT - 1)
            painter.drawText(r, Qt.AlignTop | Qt.AlignLeft, '%.3f'%v)
            painter.setPen(pen)

            x += self.CELL_WIDTH
            startCol += 1


class SkinWeightsTable(view.SkinWeightsView):
    def _initView(self, model):
        self._view = SkinWeightsSelectable(model)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.RightButton:
            mdl = self._view.model()
            c = self._columnAt(event.pos().x())
            menu = QMenu(self)
            lockAction = QAction('lock', self)
            lockAction.setCheckable(True)
            menu.addAction(lockAction)
            if mdl.isLockedColumn(c):
                lockAction.setChecked(True)
                unlockAllAction = QAction('unlock All', self)
                unlockAllAction.setCheckable(True)
                unlockAllAction.setChecked(True)
                menu.addAction(unlockAllAction)
                unlockAllAction.triggered.connect(self.unlockAllHeader)

            lockAction.triggered.connect(partial(self.lockHeader, c))
            
            menu.popup(self.mapToGlobal(event.pos()))
        else:
            self._selectColumnLeft = self._columnAt(event.pos().x())
            if self._selectColumnLeft < 0:
                self._view.clearSelection()
                self.repaint()
                return
            self._view.setSelectionArea(self._selectColumnLeft, 0, self._selectColumnLeft, self._view.model().rowCount() - 1)

    def lockHeader(self, column, isChecked):
        self._view.model().setLockedColumn(column, isChecked)
        self._view.repaint()

    def unlockAllHeader(self):
        self._view.model().unlockAllColumns()
        self._view.repaint()

    def mouseMoveEvent(self, event):
        mdl = self._view.model()
        c = self._columnAt(event.pos().x())

        if event.buttons() != Qt.NoButton:
            if self._selectColumnLeft < 0:
                return
            self._view.setSelectionArea(self._selectColumnLeft, 0, c, mdl.rowCount() - 1)
            return

        if c < 0 or c > mdl.columnCount() - 1 \
          or event.pos().y() > view.SkinWeightsViewport.CELL_HEIGHT:
            return

        x = int(event.pos().x()/view.SkinWeightsViewport.CELL_WIDTH)*view.SkinWeightsViewport.CELL_WIDTH
        y = -view.SkinWeightsViewport.CELL_HEIGHT * 2
        QToolTip.showText(self.mapToGlobal(QPoint(x, y)), self.headerLabel(c))

    def mouseReleaseEvent(self, event):
        self.mouseMoveEvent(event)