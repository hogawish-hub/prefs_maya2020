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
from maya  import cmds
import types, functools, difflib

from qtUtil import *

class RemapDialog(QDialog):
    def __init__(self, parent=None, variableOwner = None):
        super(RemapDialog, self).__init__(parent)
        self.setWindowTitle('remapper')
        self.varOwner = variableOwner
        self.connectionDict = {}
        self.bestGuess = False
        self.bases = []
        self.targets = []
        self.closeCommand = None

        self.setLayout(QHBoxLayout())
        self._splitter = QSplitter()
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().addWidget(self._splitter)
        fr1 = QFrame()
        fr2 = QFrame()
        leftLay = QVBoxLayout()
        leftLay.setContentsMargins(0,0,0,0)
        fr1.setLayout(leftLay)
        rightLay = QVBoxLayout()
        rightLay.setContentsMargins(0,0,0,0)
        fr2.setLayout(rightLay)
        self._splitter.addWidget(fr1)
        self._splitter.addWidget(fr2)
        baseSearchLayout = QHBoxLayout()
        baseSearchLayout.setContentsMargins(0,0,0,0)
        targetSearchLayout = QHBoxLayout()
        targetSearchLayout.setContentsMargins(0,0,0,0)
        leftLay.addLayout(baseSearchLayout)
        rightLay.addLayout(targetSearchLayout)
        self.baseSearch = QLineEdit()
        self.targetSearch = QLineEdit()
        baseSearchLayout.addWidget(self.baseSearch)
        targetSearchLayout.addWidget(self.targetSearch)
        self.baseList = QListWidget()
        self.baseList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.targetList = QListWidget()
        self.targetList.setSelectionMode(QAbstractItemView.MultiSelection)
        leftLay.addWidget(self.baseList)
        rightLay.addWidget(self.targetList)
        self.acceptButton = QPushButton("accept")
        self.clearConnectionsButton = QPushButton("clear")
        leftLay.addWidget(self.acceptButton)
        rightLay.addWidget(self.clearConnectionsButton)        
        
        def keyPressEventOverride(superFn, event):
            key = event.key()
            if key == Qt.Key_Control or key == Qt.Key_Shift: return
            superFn(event)

        fn = self.baseSearch.keyPressEvent
        superFn  = functools.partial(fn, self.baseSearch)
        self.baseSearch.keyPressEvent = functools.partial(keyPressEventOverride, fn)

        fn = self.targetSearch.keyPressEvent
        superFn  = functools.partial(fn, self.targetSearch)
        self.targetSearch.keyPressEvent = functools.partial(keyPressEventOverride, fn)

        self.acceptButton.clicked.connect(self.close)
        self.clearConnectionsButton.clicked.connect(self.clearConnections)
        self.baseList.itemSelectionChanged.connect(self.clearSelection)
        self.targetList.itemSelectionChanged.connect(self.createConnection)
        self.baseSearch.textChanged.connect(self.baseCompletion)
        self.targetSearch.textChanged.connect(self.targetCompletion)

    def addBase(self, base):
        vtype = type(base)
        if vtype in types.StringTypes:
            self.bases.append(base)
            self.baseList.addItem(base)
            self.connectionDict[base] = []
        else:
            self.bases.extend(base)
            for b in base:
                self.baseList.addItem(b)
                self.connectionDict[b] = []
        self._doBestGuess()

    def addTarget(self, target):
        vtype = type(target)
        if vtype in types.StringTypes:
            self.targets.append(target)
            self.targetList.addItem(target)
        else:
            self.targets.extend(target)
            for t in target:
                self.targetList.addItem(t)
        self._doBestGuess()

    def _doBestGuess(self):
        if not self.bestGuess:
            self._colorItems()
            return 

        for base in self.bases:
            closest = difflib.get_close_matches(base, self.targets, n=1)
            t = type(closest)
            if t in (types.ListType, types.TupleType) and len(closest) != 0:
                self.connectionDict[base].append( closest[0] )
            #@TODO: expand on this function: search for more available 
        self._colorItems()

    def setBestGuess(self, input):
        self.bestGuess = input 

    def populateLists(self, bases, targets, bestGuess=False):
        self.bestGuess = bestGuess
        self.bases = bases
        self.targets = targets

        for base in self.bases:
            self.connectionDict[base] = []
            self.baseList.addItem(base)

        for target in self.targets:
            self.targetList.addItem(target)

        self._doBestGuess()
    
    def baseCompletion(self, *args):
        currentText =  str(self.sender().text()).lower()
        self.baseList.clear()
        for base in self.bases:
            if currentText == '':
                self.baseList.addItem(base)
                continue
            if currentText in base.lower():
                self.baseList.addItem(base)
        self._colorItems()

    def targetCompletion(self, *args):
        currentText =  str(self.sender().text()).lower()
        self.targetList.clear()
        for target in self.targets:
            if currentText == '':
                self.targetList.addItem(target)
                continue
            if currentText in target.lower():
                self.targetList.addItem(target)
        self._colorItems()

    def _colorItems(self, *args):
        for i in xrange(self.baseList.count()):
            if self.connectionDict[str(self.baseList.item(i).text())] == []:
                self.baseList.item(i).setBackground( QBrush(QColor("darkred")))
            elif len(self.connectionDict[str(self.baseList.item(i).text())]) > 1:
                self.baseList.item(i).setBackground( QBrush(QColor("darkblue")))
            else:
                self.baseList.item(i).setBackground( QBrush(QColor("green")))
        #@TODO: think of ways to deal with not connected objects

    def createConnection(self):
        if len(self.baseList.selectedItems()) == 0:
            return
        base = str(self.baseList.selectedItems()[0].text())
        selectionListTarget = self.targetList.selectedItems()
        self.connectionDict[base] = []
        for targetItem in selectionListTarget:
            self.connectionDict[base].append(str(targetItem.text()))
        self._colorItems()

    def clearSelection(self):
        if len(self.sender().selectedItems()) == 0:
            return
        getList = self.connectionDict[str(self.sender().selectedItems()[0].text())]
        selection_model = self.targetList.selectionModel()
        self.targetList.clearSelection()
        for target in getList:
            item = self.targetList.findItems(target, Qt.MatchExactly)[0]
            index = self.targetList.indexFromItem(item)
            selection_model.select(index, QItemSelectionModel.Select)
        
    def clearConnections(self):
        for key, value in self.connectionDict.iteritems():
            self.connectionDict[key] = []
        self._colorItems()

    def setCloseCommand(self, inCommand):
        self.closeCommand = inCommand

    def closeEvent(self, event = None, *args):
        notConnected = []
        for key, value in self.connectionDict.iteritems():
            if not value == []:
                continue
            notConnected.append(key)
        
        if len(notConnected) > 0:
            result = cmds.confirmDialog( 
                title='not all joints connected', 
                message='not all joints are connected, \nif you continue a joint wil be created to connect all values to.\npress cancel to connect manually!',
                button=['Continue','Cancel'], defaultButton='Cancel', 
                cancelButton='Cancel', dismissString='Cancel' )

            if result == 'Continue':
                cmds.select(cl=1)
                name = "DEFAULT__CONNECTION__JOINT"
                if not cmds.objExists(name):
                    cmds.joint(n=name)
                for key, value in self.connectionDict.iteritems():
                    if not value == []:
                        continue
                    self.connectionDict[key].append(name)
            else:
                event.ignore()
                return
            
        if self.varOwner != None:
            self.varOwner(self.connectionDict)
        
        if self.closeCommand !=None:
            self.closeCommand(self.connectionDict)
        # continue basic close event process
        super(RemapDialog, self).closeEvent(event, *args)
        self.deleteLater()
