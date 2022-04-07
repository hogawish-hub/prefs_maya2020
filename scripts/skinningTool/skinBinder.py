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
from kdtree         import KDTree
from skinningTools  import SkinningTools;
from maya           import cmds, mel
from maya.api       import OpenMaya
from math           import *
from colorButton    import QColorButton
import maya.OpenMaya as oldOpenMaya
import os, functools, polySelectionUtils

from qtUtil import *

class SkinBinder(object):
    def __init__(self):
        super(SkinBinder, self).__init__()
        self.addedLayouts = []

    def createLocator(self, pos = [0.0, 0.0, 0.0], object= None, name = "Locator"):
        loc = cmds.spaceLocator()[0]
        cmds.setAttr(loc+'.t', pos[0], pos[1], pos[2])
        if object != None:
            pc = cmds.pointConstraint(object, loc, mo=False)
            cmds.delete(pc)
        cmds.addAttr( loc, ln ="parentObject", dt="string", k=True )
        cmds.setAttr( loc+'.parentObject', name, type = "string" )
        return loc

    def dividePoints(self, inpos, divisions, parent):
        posA = OpenMaya.MVector(inpos[0][0], inpos[0][1], inpos[0][2])
        posB= OpenMaya.MVector(inpos[1][0], inpos[1][1], inpos[1][2])
        posC = posB -posA
        distance = posC.length()
        amount = distance / divisions
        locs = []
        for i in range(divisions+1):
            posD = (posA + (posC.normalize() * (i *amount)))
            pos = (posD.x ,posD.y ,posD.z )
            locs.append([pos, parent])
        return locs

    def createSkinBindVisualiser(self, errorMargin = 0.01, positionMargin = 0.01, primaryAxis = "y", jnts = cmds.ls(sl=True, type = "joint") ):
        axis = ["x", "y", "z"]
        singlelocs   = []
        doubleLocs   = []
        visualCurves = []
        
        rightSide= []                
        doubleParentList = []
        uniqueJnts = list(set(jnts))
        if (len(uniqueJnts)) == 0:
            return
        for jnt in uniqueJnts:
            children = cmds.listRelatives(jnt, c=1, type = "joint")
            
            side = cmds.getAttr(jnt+".side") 

            base = cmds.xform(jnt,q=1,ws=1,t=1)
            baseVector = OpenMaya.MVector(base[0], base[1], base[2])
            if children != None and len(children) > 0 :
                childrenAlligned = True
                for child in children:
                    for ax in axis:
                        if ax == primaryAxis:
                            continue
                        if cmds.getAttr(child+'.t%s'%ax) < errorMargin:
                            continue
                        childrenAlligned = False        
                
                beginSame  = False
                linearList = []
                parentList = []
                orderList  = []
                
                for child in children:
                    if not child in uniqueJnts:
                        continue
                        
                    if childrenAlligned and len(children) > 1:
                        chPos = cmds.xform(child, q=1,ws=1,t=1)
                        chPosVector = OpenMaya.MVector(chPos[0], chPos[1], chPos[2])
                        dist = (chPosVector - baseVector).length()
                        if dist < errorMargin:
                            beginSame = True
                        orderList.append(dist)
                        linearList.append([dist,chPos])     
                        parentList.append([dist, child])
                        continue    
                        
                    chPos   = cmds.xform(child, q=1,ws=1,t=1)
                    chPosVector = OpenMaya.MVector(chPos[0], chPos[1], chPos[2])
                    vector1 = (chPosVector-baseVector)*positionMargin
                    vector2 = (chPosVector-baseVector)*(1.0-positionMargin)
                    newPosA = baseVector + vector1
                    newPosB = baseVector + vector2
                    loc1    = self.createLocator((newPosA.x, newPosA.y, newPosA.z), None, jnt)
                    loc2    = self.createLocator((newPosB.x, newPosB.y, newPosB.z), None, jnt)
                    doubleParentList.append(jnt)
                    doubleLocs.append([loc1, loc2]) 
                    if side == 2:
                        rightSide.extend([loc1, loc2])
                    
                if childrenAlligned:
                    newOrder = sorted(orderList)
                    posParent = []
                    for ordered in newOrder:
                        for index, position in enumerate(linearList):
                            if position[0] != ordered:
                                continue
                            posParent.append([position[1], parentList[index][1]])
                    
                    if not beginSame == True:        
                        posParent.insert(0, [base, jnt])
                    
                    for i in range(len(posParent)-1):
                        nbase   = posParent[i][0]
                        chPos   = posParent[i+1][0]
                        nBaseVector = OpenMaya.MVector(nbase[0], nbase[1], nbase[2])
                        chPosVector = OpenMaya.MVector(chPos[0], chPos[1], chPos[2])
                        vector1 = (chPosVector-nBaseVector)*positionMargin
                        vector2 = (chPosVector-nBaseVector)*(1.0-positionMargin)
                        newPosA = nBaseVector + vector1
                        newPosB = nBaseVector + vector2
                        loc1    = self.createLocator((newPosA.x, newPosA.y, newPosA.z), None, posParent[i][1])
                        loc2    = self.createLocator((newPosB.x, newPosB.y, newPosB.z), None, posParent[i][1])
                        doubleParentList.append(posParent[i][1])
                        doubleLocs.append([loc1, loc2])                       
                        if side == 2:
                            rightSide.extend([loc1, loc2])
            else:
                loc = self.createLocator( object = jnt, name= jnt)
                singlelocs.append(loc)
                if side == 2:
                    rightSide.append(loc)

        locs = []
        singleLocs1 = []
        for idx, l in enumerate(singlelocs):
            parentObj = cmds.getAttr( l+'.parentObject' )
            if parentObj in doubleParentList:
                cmds.delete(l)
                continue
            locs.append(l)
            singleLocs1.append(l)

        bLoc = cmds.createNode( "SkinningVisualizer" )
        cmds.setAttr( "%s.overrideEnabled"%bLoc, 1 )
        cmds.setAttr( "%s.overrideDisplayType"%bLoc, 1 )
        for it, l in enumerate(doubleLocs):
            cmds.connectAttr( l[0]+'.worldMatrix[0]', bLoc+'.jointPairs[%s].worldMatrixStart'%it, f=1 )    
            cmds.connectAttr( l[1]+'.worldMatrix[0]', bLoc+'.jointPairs[%s].worldMatrixEnd'%it, f=1 )
            locs.extend( l )

        mirrorGrp = cmds.group(em=1)
        cmds.setAttr(mirrorGrp +'.scaleX', -1)
        grp = cmds.group( em=1 )     
        for l in locs:
            if l in rightSide:
                cmds.parent(l, mirrorGrp)
                cmds.setAttr(l +'.r', 0,0,0)
                cmds.setAttr(l +'.s', 1,1,1)
                continue
            cmds.parent(l, grp)
        
        cmds.parent(mirrorGrp, grp)
        

        return singleLocs1, doubleLocs, bLoc
        
    def convertVisualToSkin(self, singlePositions, groupedPositions, skinMeshes, divisions = 7, smoothValue = 4, progressBar = None):
        # skinBased On Vornoi principle:
        locs = []
        for sp in singlePositions:
            pos = cmds.xform( sp, q=1, ws=1, t=1 )
            parentObj = cmds.getAttr( sp+'.parentObject' )
            locs.append( [ pos, parentObj ] )
        
        curves = []
        for gp in groupedPositions:
            pos1 = cmds.xform( gp[0], q=1,ws=1,t=1)
            pos2 = cmds.xform( gp[1], q=1,ws=1,t=1)
            parentObj = cmds.getAttr( gp[0]+'.parentObject' )
            if divisions > 2:
                extraLocs = self.dividePoints( [pos1, pos2], divisions, parentObj )

                locs.extend( extraLocs )        
        
        sourcePos = []
        sourcePointPos = locs[:]
        skinJoints = []
        for posParent in locs:
            sourcePos.append( posParent[0] )
            skinJoints.append( posParent[1] )

        cleanSkinJoints = list( set( skinJoints ) )
        sourceKDTree    = KDTree.construct_from_data( sourcePos )

        parentGrp = cmds.listRelatives(singlePositions[0], p=1, f=1)[0].split('|')[1]
        cmds.delete(parentGrp)

        for skinMesh in skinMeshes:
            newSkinCl       = cmds.skinCluster( cleanSkinJoints, skinMesh, mi=8, tsb=1 )[ 0 ]
            meshShapeName   = cmds.listRelatives( skinMesh, s=True )[ 0 ]

            sourceInflArray = cmds.SkinWeights( [ meshShapeName, newSkinCl ],  q=True )

            allVtx          = SkinningTools().convertToVertexList( skinMesh )
            vtxAmount       = len(allVtx)
            percentage      = 95.0/ vtxAmount
            jointAmount     = len( cleanSkinJoints )
            joint           = cmds.skinCluster(newSkinCl, q=True, inf=True)    
            
            allWeights      = [0.0] * (vtxAmount * jointAmount)
            for iteration, tVertex in enumerate(allVtx):
                pos = cmds.xform(tVertex, q=1,ws=1,t=1)
                pts = sourceKDTree.query(query_point = pos, t=smoothValue)
                
                weights     = []
                distances   = []
                fullLength  = 0.0
                for positionList in sourcePointPos:
                    for index in range( smoothValue ):
                        if pts[ index ] != positionList[ 0 ]:
                            continue
                        distanceToPoint =sqrt( pow( ( pos[ 0 ] - pts[ index ][ 0 ] ), 2 ) + 
                                               pow( ( pos[ 1 ] - pts[ index ][ 1 ] ), 2 ) + 
                                               pow( ( pos[ 2 ] - pts[ index ][ 2 ] ), 2 ) )
                        
                        distanceWeight = ( 1.0/ ( 1.0 + distanceToPoint ) )
                        distances.append( [distanceWeight, positionList[ 1 ] ])
                        fullLength += distanceWeight 
              
                for indexing, dist in enumerate(distances):
                    jidx = cleanSkinJoints.index(dist[1])
                    allWeights[(iteration*jointAmount) + jidx] += ( dist[0]/fullLength )
                
                if progressBar != None:
                    progressBar.setValue(percentage*iteration)
                    qApp.processEvents()
                
            cmds.SkinWeights( [ meshShapeName, newSkinCl ] , nwt=allWeights )
 
            softVtx = []
            for vtx in allVtx:
                weights = cmds.skinPercent( newSkinCl, vtx, q=1, v=1 )
                amount = 0
                for wgt in weights:
                    if wgt > 0.0:
                        amount+=1
                if amount == 1:
                    continue
                softVtx.append(vtx)    

            cmds.select(softVtx)
            try:
                softVtx = SkinningTools().hammerVerts( softVtx )
            except:
                pass
            for i in range( smoothValue ):
                softVtx = SkinningTools().smoothAndSmoothNeighbours( softVtx, True )

        if progressBar != None:
            progressBar.setValue(100)
            qApp.processEvents()

    def addColorControls(self, layouttoAttach):
        def spComboBox():
            cb = QComboBox()
            cb.setMinimumWidth( 70 )
            cb.setMaximumWidth( 70 )
            listcb = [ "metal", "skin", "rubber", "plastic", "wood", "organic", ]
            cb.addItems( listcb )
            return cb
    
        def addButton(name, size):
            pb = QPushButton( name )
            pb.setMinimumWidth( size )
            pb.setMaximumWidth( size )
            return pb
    
        horLayout = QHBoxLayout()
        color1    = QColorButton()
        add       = addButton( "+", 20 )
        remove    = addButton( "-", 20 )
        spacer    = QSpacerItem( 20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding )
        select    = addButton( "Select", 40 )
        delete    = addButton( "X", 20 )
        
        horLayout.setContentsMargins( 0, 0, 0, 0 )
        horLayout.setSpacing( 6 )
        color1.setMinimumWidth( 50 )
        cbb =  spComboBox()
        horLayout.addWidget( color1 )
        horLayout.addWidget( add )
        horLayout.addWidget( remove )
        horLayout.addItem(   spacer )
        horLayout.addWidget( cbb )
        horLayout.addWidget( select )
        horLayout.addWidget( delete )
        
        add.clicked.connect( functools.partial( self.addSelection, horLayout ) )
        remove.clicked.connect( functools.partial( self.remSelection, horLayout ) )
        color1.colorChanged.connect( functools.partial( self.setColor, horLayout ) )
        select.clicked.connect(functools.partial( self.selectVertices, horLayout ) )
        delete.clicked.connect(functools.partial( self.deleteLayout, horLayout ) )        

        horLayout.itemText = [color1, add, remove, select, delete, cbb]
        horLayout.selectionList = []
        self.addedLayouts.append(horLayout)
        layouttoAttach.insertLayout( 0, horLayout )

    def addSelection(self, layout):
        selection = cmds.ls(sl=True)
        allVtx    = SkinningTools().convertToVertexList( selection )
        curList = layout.selectionList[:]
        curList.extend(allVtx)
        layout.selectionList = list(set(curList))
        colorList =  QColor( layout.itemText[0].color() ).getRgb()
        
        mesh = layout.selectionList[0].split(".")[0]
        iter = self.convertToIndexList(layout.selectionList)
        colors = [[colorList[0]/255.0, colorList[1]/255.0, colorList[2]/255.0]] * len(layout.selectionList)
        self.apply_api_colors(colors, iter, mesh)

        for l in self.addedLayouts:
            if l == layout:
                continue
            l.selectionList = list( set(l.selectionList).difference(allVtx) )

    def remSelection(self, layout):
        selection = cmds.ls(sl=True)
        allVtx    = SkinningTools().convertToVertexList( selection )
        curList = layout.selectionList[:]
        mesh = layout.selectionList[0].split(".")[0]
        indices = []
        removeColor = []
        for vert in allVtx:
            if not vert in curList:
                continue    
            index = int(vert.split("[")[-1].split("]")[0])
            indices.append(index)
            removeColor.append(vert)
            curList.remove(vert)
        layout.selectionList = curList
        
        self.remove_api_colors(indices, mesh)  

    def setColor(self, layout):
        colorList =  list(QColor( layout.itemText[0].color() ).getRgb())
        if colorList == [0,0,0,255]:
            mesh = layout.selectionList[0].split(".")[0]
            indices = []
            for i in layout.selectionList:
                index = int(i.split("[")[-1].split("]")[0])
                indices.append(index)
            self.remove_api_colors(indices, mesh) 
            return
        try:
            mesh = layout.selectionList[0].split(".")[0]
            iter = self.convertToIndexList(layout.selectionList)
            colors = [[colorList[0]/255.0, colorList[1]/255.0, colorList[2]/255.0]] * len(layout.selectionList)
            self.apply_api_colors(colors, iter, mesh)
        except:
            pass

    def selectVertices(self, layout):
        cmds.select( layout.selectionList, r=1)

    def clearScene(self):
        for layout in self.addedLayouts:
            self.deleteLayout(layout)

    def deleteLayout(self, layout):
        for item in layout.itemText:
            item.deleteLater()
        curList = layout.selectionList[:]
        try:
            mesh = layout.selectionList[0].split(".")[0]
            indices = self.convertToIndexList(layout.selectionList)
            self.remove_api_colors(indices, mesh)    
        except:
            pass
        layout.deleteLater()
        self.addedLayouts.remove(layout)

    def analyseSelection(self, mesh, layouttoAttach):
        
        allVtx    = SkinningTools().convertToVertexList( mesh )
        colorDict = {}
        colors = []
        for vtx in allVtx:
            color = cmds.polyColorPerVertex(vtx, q=1, rgb=1)
            if color == [0.0,0.0,0.0]:
                continue
            reColor = [float("{0:.2f}".format(color[0])), float("{0:.2f}".format(color[1])), float("{0:.2f}".format(color[2]))]
            if not str(reColor) in colorDict.keys():
                colorDict[str(reColor)] = [vtx]
                colors.append(reColor)
                continue
            colorDict[str(reColor)].append(vtx)

        for index, color in enumerate(colors):
            self.addColorControls(layouttoAttach)
            currentColor = QColor(int(color[0]*255.0), int(color[1]*255.0), int(color[2]*255.0))

            self.addedLayouts[index].itemText[0].setColor(currentColor)
            self.addedLayouts[index].selectionList = colorDict[str(color)]
            self.addedLayouts[index].itemText[0].setStyleSheet("background-color: %s;" % currentColor.name())

    def apply_api_colors(self, colors, indices, obj):
         colors = [OpenMaya.MColor(i) for i in colors]
         selectionList = OpenMaya.MSelectionList()
         selectionList.add(obj)
         nodeDagPath = selectionList.getDagPath(0)
         mfnMesh = OpenMaya.MFnMesh(nodeDagPath)
         mfnMesh.setVertexColors(colors, indices)

    def remove_api_colors(self, indices, obj):
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(obj)
        nodeDagPath = selectionList.getDagPath(0)
        mfnMesh = OpenMaya.MFnMesh(nodeDagPath)
        mfnMesh.removeVertexColors(indices)

    def convertToIndexList(self, vertList):
        indices = []
        for i in vertList:
            index = int(i.split("[")[-1].split("]")[0])
            indices.append(index)
        return indices

    def _setProgressBar(self, inValue, progressBar=None):
        if progressBar:
            progressBar.setValue( inValue )
            QApplication.processEvents()

    def strVertId(self, vert):
        return int(vert.rsplit('[', 1)[-1][:-1])

    def setHardSurfaceSkin(self, inSelection, mesh, inProgressBar = None):
        def getNeighbors(inVertices):
            return cmds.filterExpand(cmds.polyListComponentConversion(cmds.polyListComponentConversion(inVertices, tf=True), tv=True), sm=31)

        self._setProgressBar( 0, inProgressBar ) 

        meshShapeName   = cmds.listRelatives(mesh, s=1)[0]
        SkinClusterName = SkinningTools().skinCluster( mesh, True)
        infArray        = cmds.SkinWeights([meshShapeName, SkinClusterName] , q=1)
        attachedJoints  = cmds.skinCluster(SkinClusterName, q=True, inf=True)
        jointAmount     = len(attachedJoints)

        self._setProgressBar(5.0, inProgressBar)
        convertedShells =  polySelectionUtils.getConnectedVerts(mesh, inSelection)
        percentage = 69.0/len(convertedShells)
        for it, entries in convertedShells.iteritems():
            shell1 = convertedShells[it]
            shell= []
            for vertex in shell1:
                shell.append("%s.vtx[%s]"%(mesh, vertex))
            #gather locational info
            expandedVertices1 = getNeighbors(shell)
            fixedList         =  list( set( expandedVertices1 ) ^ set( shell ) )
            baseIndices = self.convertToIndexList(shell)
            amountBase  = len(baseIndices)
            if len(fixedList) == 0:
                #look at vertices in shell
                weightList = [.0] * jointAmount
                for indexing in baseIndices:
                    for i in range(jointAmount):
                        weightList[i] += infArray[(indexing*jointAmount)+i]
                transformValues = []
                for index, am in enumerate(weightList):
                    transformValues.append([attachedJoints[index], am/float(amountBase)])

                cmds.select(shell, r=1)
                cmds.skinPercent( SkinClusterName ,transformValue=transformValues )
            else:
                #look at vertices outside shell (fixedList)
                outIndices = self.convertToIndexList(fixedList)
                amountOut = len(outIndices)

                weightList = [.0] * jointAmount
                for indexing in outIndices:
                    for i in range(jointAmount):
                        weightList[i] += infArray[(indexing*jointAmount)+i]                      
                transformValues = []
                for index, am in enumerate(weightList):
                    transformValues.append([attachedJoints[index], am/float(amountOut)])
                cmds.select(shell, r=1)
                cmds.skinPercent( SkinClusterName ,transformValue=transformValues )
            
            self._setProgressBar(30.0 + (percentage*(it+1)), inProgressBar)

        cmds.select(mesh)
        cmds.skinPercent(SkinClusterName, normalize = True)
        self._setProgressBar(100.0, inProgressBar)

    def setSoftSurfaceSkin(self, inSelection, mesh, inProgressBar):
        self._setProgressBar( 0, inProgressBar ) 

        meshShapeName   = cmds.listRelatives(mesh, s=1)[0]
        SkinClusterName = SkinningTools().skinCluster( mesh, True)
        infArray        = cmds.SkinWeights([meshShapeName, SkinClusterName] , q=1)
        attachedJoints  = cmds.skinCluster(SkinClusterName, q=True, inf=True)
        jointAmount     = len(attachedJoints)

        self._setProgressBar(5.0, inProgressBar)
        convertedShells =  polySelectionUtils.getConnectedVerts(mesh, inSelection)
        percentage = 69.0/len(convertedShells)
        for it, entries in convertedShells.iteritems():
            shell1 = convertedShells[it]
            shell= []
            for vertex in shell1:
                shell.append("%s.vtx[%s]"%(mesh, vertex))

            cmds.select(shell, r=1)
            cmds.ShrinkPolygonSelectionRegion()
            curSel     = cmds.ls(sl=True)
            fixedList1 =  list( set( shell ) ^ set( curSel ) )
            cmds.skinCluster(SkinClusterName, geometry = fixedList1,  e = True, sw = 0.000001, swi = 5, omi = 0 )
            cmds.ShrinkPolygonSelectionRegion()
            curSel1    = cmds.ls(sl=True)
            fixedList2 =  list( set( curSel ) ^ set( curSel1 ) )
            cmds.skinCluster(SkinClusterName, geometry = fixedList2,  e = True, sw = 0.000001, swi = 5, omi = 0 )
            self._setProgressBar(30.0 + (percentage*(it+1)), inProgressBar)

        cmds.select(mesh)
        cmds.skinPercent(SkinClusterName, normalize = True)
        self._setProgressBar(100.0, inProgressBar)