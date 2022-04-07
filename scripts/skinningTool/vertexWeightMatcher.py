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
from maya import cmds, mel

from qtUtil import *

from skinningTools  import SkinningTools

class SkinWeightsWidget(QWidget):
    '''as long as the vertex order is the same, this widget will transfer skindata from 1 object to another based on vertex selection'''
    def __init__(self, parent=None):
        super(SkinWeightsWidget, self).__init__(parent)

        frame = QFrame()
        grid = QGridLayout()
        frame.setLayout(grid)
        self.source = QLabel('No source')
        self.source.setMaximumHeight(23)
        self.source.setMinimumHeight(23)
        grid.addWidget(self.source, 0, 0)
        self.btn = QPushButton('Grab source')
        self.btn.clicked.connect(self.__grabSourceCB)
        grid.addWidget(self.btn, 1, 0)
        self.target = QLabel('No target')
        self.target.setMaximumHeight(23)
        self.target.setMinimumHeight(23)
        grid.addWidget(self.target, 0, 1)
        self.btn1 = QPushButton('Grab target')
        self.btn1.clicked.connect(self.__grabTargetCB)
        grid.addWidget(self.btn1, 1, 1)
        

        l = QVBoxLayout()
        l.setSpacing(0)
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)
        l.addWidget(frame)
        self.btn2 = QPushButton('Copy selected vertices')
        self.btn2.clicked.connect(self.__copySkinDataCB)
        l.addWidget(self.btn2)
        self.additive = QCheckBox('Additive')
        l.addWidget(self.additive)
        l.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.__loadBar= None
    
    def __grabSC(self):
        t = cmds.ls(sl=1)
        if not t:
            return None
        skinCluster = SkinningTools.skinCluster(t[0], True)
        if skinCluster == None:
            print "no skincluster found"
            return None
        return skinCluster
    def __grabSourceCB(self):
        skinCluster = self.__grabSC()
        if skinCluster == None:
            return
        self.source.setText(skinCluster)
        
    def __grabTargetCB(self):
        skinCluster = self.__grabSC()
        if skinCluster == None:
            return
        self.target.setText(skinCluster)

    def addLoadingBar(self, loadingBar):
        self.__loadBar = loadingBar
    
    def __copySkinDataCB(self):
        source = str(self.source.text())
        target = str(self.target.text())
        if not cmds.objExists(source) or not cmds.objExists(target):
            cmds.error('Must load an existing source and target skin cluster to copy between')
            return
        expandedVertices = SkinningTools().convertToVertexList(cmds.ls(sl=1, fl=1))
        if not expandedVertices:
            cmds.error('Must select vertices to copy weights for')
        
        
        #get input data
        outInfluences = cmds.skinCluster(target, q=True, influence=True)
        inWeights = cmds.SkinWeights(cmds.skinCluster(source, q=True, g=True)[0], source, q=True)
        inInfluences = cmds.skinCluster(source, q=True, influence=True)
        
        #make sure all input influences exist on output
        add = []
        for influence in inInfluences:
            if influence not in outInfluences:
                add.append(influence)
        if add:
            cmds.skinCluster(target, addInfluence=add, wt=0, e=True)
        
        #get output data
        outWeights = cmds.SkinWeights(cmds.skinCluster(target, q=True, g=True)[0], target, q=True)
        outInfluences = cmds.skinCluster(target, q=True, influence=True)
        numInInf = len(inInfluences)
        numOutInf = len(outInfluences)

        if self.__loadBar != None:
            percentage = 99.0/len(expandedVertices) 
        
        #copy input data to output
        for iteration, vertex in enumerate(expandedVertices):
            id = int(vertex.rsplit('[',1)[-1].split(']',1)[0])
            #zero out
            if not self.additive.isChecked():
                outWeights[id * numOutInf : (id + 1) * numOutInf] = [0]*numOutInf
            for i in range(numInInf):
                offset = outInfluences.index(inInfluences[i])
                outWeights[id * numOutInf + offset] += inWeights[id * numInInf + i]
            #normalize
            tw = 0
            for i in range(numOutInf):
                tw += outWeights[id * numOutInf + i]
            if tw == 0:
                continue
            ratio = 1.0 / tw
            for i in range(numOutInf):
                outWeights[id * numOutInf + i] *= ratio

            if self.__loadBar != None:
                self.__loadBar.setValue( percentage*(iteration + 1) )
                qApp.processEvents()
                
        cmds.SkinWeights(cmds.skinCluster(target, q=True, g=True)[0], target, nwt=outWeights)
        if self.__loadBar != None:
            self.__loadBar.setValue( 100 )
            qApp.processEvents()


class VertexSelectionWidget(QWidget):
    '''simple UI that manages the selected vertices and stores them with the UI'''
    def __init__(self, parent=None):
        super(VertexSelectionWidget, self).__init__(parent)

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.itemSelectionChanged.connect(self.__applySelectionCB)
        self.list.itemDoubleClicked.connect(self.__deleteItemCB)
        self.settings = QSettings('GG', 'SimpleClothUI')
        
        self.btn = QPushButton('StoreSelection')
        self.btn.clicked.connect(self.__storeSelectionCB)

        self.btn1 = QPushButton('ClearList')
        self.btn1.clicked.connect(self.__clearSelectionCB)
        
        for key in self.settings.allKeys():
            try:
                forceString = str(key)
            except:
                continue
            if not 'vertexselections/' in forceString:
                continue
            data = self.settings.value(key, None)
            if data is None:
                continue
            if QT_VERSION == "pyqt4":
                self.__addItem(key.split('/',1)[1], data.toPyObject())
            else:
                self.__addItem(key.split('/',1)[1], data)

        l = QVBoxLayout()
        l.setSpacing(0)
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)
        l.addWidget(self.list)
        l1 = QHBoxLayout()
        l1.setSpacing(0)
        l1.setContentsMargins(0,0,0,0)
        l1.addWidget(self.btn)
        l1.addWidget(self.btn1)
        l.addLayout(l1)
        # TODO: make sure settings are saved on close/hide

    def __deleteItemCB(self, item):
        self.settings.remove(item.text())
        self.list.takeItem(self.list.row(item))

    def __clearSelectionCB(self):
        self.list.clear()
        self.settings.clear()

        
    def __addItem(self, name, pyData):
        match = self.list.findItems(name, Qt.MatchExactly)
        if len(match):
            match[0].setData(Qt.UserRole, pyData)
            return match[0]
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, pyData)
        self.list.addItem(item)
        return item
    
    def __storeSelectionCB(self):
        expandedVertices = SkinningTools().convertToVertexList(cmds.ls(sl=1, fl=1))
        
        name = QInputDialog.getText(self, 'Name selection', 'Please enter a name for this selection', text=expandedVertices[0].split('.',1)[0])
        if not name[1]:
            return
        name = name[0]
        item = self.__addItem(name, expandedVertices)
        
        self.settings.setValue('vertexselections/%s'%name, item.data(Qt.UserRole))
        cmds.select(expandedVertices)
    
    def doCorrectSelectionVisualization(self, skinMesh):
        objType = cmds.objectType(skinMesh)
        if objType == "transform":
            shape = cmds.listRelatives(skinMesh, c=1, s=1)[0]
            objType = cmds.objectType(shape)

        mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
        if objType == "nurbsSurface" or objType == "nurbsCurve":
            mel.eval('doMenuNURBComponentSelection("%s", "controlVertex");'%skinMesh )
        elif objType == "lattice":
            mel.eval('doMenuLatticeComponentSelection("%s", "latticePoint");'%skinMesh )
        else:
            mel.eval('doMenuComponentSelection("%s", "vertex");'%skinMesh )

    def __applySelectionCB(self):
        cmds.select(clear=True)
        for item in self.list.selectedItems():
            if QT_VERSION == "pyqt4":
                selectionItem = item.data(Qt.UserRole).toPyObject()
            else:
                selectionItem = item.data(Qt.UserRole)

            if cmds.objExists(str(selectionItem[0].split('.')[0])): 
                SkinningTools.doCorrectSelectionVisualization(str(selectionItem[0].split('.')[0]))
                cmds.select(selectionItem, add=True)
            else:
                cmds.warning('%s does not exist in currentScene'%(selectionItem[0].split('.')[0]))
