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
import remapDialog, skinningTools 
from kdtree import KDTree
from maya import OpenMayaUI, cmds
from math import pow, sqrt

from qtUtil import *

class JointRemapper(object):
    def __init__(self):
        super(JointRemapper, self).__init__()
        self.weightsMap = None
        self.model = None
        self.storedSkinInformation = None
        self.origVerts = None
        self.progressBar = None
        self.nearest= 1
        self.joints=None
        self.remapdict = {}

    def show(self, inJnts, outJnts):
        def mayaMainWindow():
            from skinningTool import SkinningToolsUI
            mainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
            return SkinningToolsUI.wrapinstance(long(mainWindowPtr))
    
        mayaWindow = mayaMainWindow()
        window = remapDialog.RemapDialog(mayaWindow, self.setRemmapedDict)
        window.setBestGuess(True)
        window.addBase(sorted(inJnts))
        window.addTarget(sorted(outJnts))
        
        window.resize( 500, 700 )
        window.show()
        return window
    
    def setRemmapedDict(self, remapValues):
        self.remapdict = remapValues
        print "origFile", self.remapdict

    def printMapDict(self, inMap):
        origWeights, origVertsAmount, origJoints = self.weightsMap
        newJoints = self.joints 
        
        name = "DEFAULT__CONNECTION__JOINT"
        if cmds.objExists(name) and not name in newJoints:
            newJoints.append(name)
            skinningTools.SkinningTools().addUnlockedZeroInfl([name], self.model)

        origAmountJnts = len(origJoints)
        newAmountJnts = len(newJoints)
        listSize = newAmountJnts * origVertsAmount
        newWeights = [0.0] * listSize
        for vert in xrange(origVertsAmount):
            for index, joint in enumerate(origJoints):
                joints = inMap[joint]
                for jnt in joints:
                    getIndex = newJoints.index(jnt)# get the index based on dict
                    
                    origValue = origWeights[(vert*origAmountJnts) + index]
                    newWeights[(vert * newAmountJnts) + getIndex] = origValue
        
        skinClusterName = skinningTools.SkinningTools().skinCluster(self.model, True)
        shape = cmds.listRelatives(self.model, s=1)[0]
        if self.origVerts == None:
            skinWeights = cmds.SkinWeights([shape, skinClusterName] , nwt=newWeights)
        else:
            self.remapWeights( skinClusterName, newWeights)
    
    def setData(self,  object, origVerts, progressBar, nearest, inJnts):
        self.model = object
        self.origVerts = origVerts
        self.progressBar = progressBar
        self.nearest= nearest
        self.joints = inJnts

    def remapJoints(self, weightMap, newJoints, inModel,  origVerts = None):
        self.model = inModel
        self.weightsMap = weightMap
        self.joints = newJoints
        self.origVerts= origVerts
        ToRemap = False

        for jnt in weightMap:
            if jnt in newJoints:
                continue
            ToRemap = True
    
        if not ToRemap:
            return weightsList
        
        self.Remapper = self.show(weightMap[-1], newJoints)    
        
        self.Remapper.setCloseCommand(self.printMapDict)
        
    def storeSkinCluster(self, inObject):
        
        meshShapeName = cmds.listRelatives(inObject, s=True)[0]
        vertices = skinningTools.SkinningTools().convertToVertexList(inObject)   
        skinCluster = skinningTools.SkinningTools().skinCluster(inObject, False)
        infjnts  = cmds.skinCluster(skinCluster, q=True, inf=True)
        self.originalPositions = []
        for jnt in infjnts:
            pos = cmds.xform(jnt, q=1, ws=1, t=1)
            self.originalPositions.append([jnt, pos])
        if skinCluster:
            self.storedSkinInformation = (cmds.SkinWeights([meshShapeName , skinCluster],  q=True), len(vertices), infjnts)   
            return True
        return False

    def preStoreSkinCluster(self, inWeightInfo):
        # use this when no object can be specified (i.e. when used from weights manager)
        # weightinfo : weight infoList, infJnts, jointPosList
        weightInfoList = inWeightInfo[0]
        vertexAmount = inWeightInfo[1]
        infjnts = inWeightInfo[2]
        origPosJnts = []
        for index, jnt in enumerate(infjnts):
            origPosJnts.append([jnt, inWeightInfo[3][index]])
        self.originalPositions =origPosJnts
        self.storedSkinInformation = (weightInfoList, vertexAmount, infjnts)   
        return True

    def _findClosestObjects(self, sourceTree, targetVertex, sourcePointPos,sourcePoints, sourceUV):
        pos = cmds.xform(targetVertex, q=1, ws=1, t=1)
        if sourceUV:
            alluvs = cmds.polyListComponentConversion(targetVertex, tuv=True)
            singleUV = cmds.filterExpand(alluvs, sm=35)[0]
            pos = cmds.polyEditUV(singleUV, q=True, u=True,v=True)

        pts = sourceTree.query(query_point = pos, t=self.nearest)
        
        weights = []
        distanceWeightsArray = []
        totalDistanceWeights = 0
        
        for index in xrange(self.nearest):
            key = sourcePoints.keys()[sourcePoints.values().index(pts[index])]
            length = self._measureLength(pos, pts[index])

            distanceWeight = ( 1.0/ ( 1.0 + length ) )
            distanceWeightsArray.append( distanceWeight )
            totalDistanceWeights += distanceWeight 
            
            weights.append( sourcePointPos[key] )
        return weights, distanceWeightsArray, totalDistanceWeights

    def _measureLength(self, pt1, pt2):
        if len(pt1) > 2:
            length = sqrt( pow( ( pt1[ 0 ] - pt2[ 0 ] ), 2 ) + 
                           pow( ( pt1[ 1 ] - pt2[ 1 ] ), 2 ) + 
                           pow( ( pt1[ 2 ] - pt2[ 2 ] ), 2 ) )
        else:
            length = sqrt( pow( ( pt1[ 0 ] - pt2[ 0 ] ), 2 ) + 
                           pow( ( pt1[ 1 ] - pt2[ 1 ] ), 2 ) )
        return length 
    
    def _createWeightsList(self, jointAmount, weights, distanceWeightsArray, totalDistanceWeights):
        newWeights = [0.0] * jointAmount
        for index in xrange(self.nearest ):
            for i,  wght in enumerate( weights[ index ] ):
                valDiv = ( distanceWeightsArray[ index ] / totalDistanceWeights ) * wght
                if valDiv == 0.0 or wght < 0.000001:
                    continue
                newWeights[i] += valDiv
        return newWeights

    def remapWeights(self, skinClusterName, inRemappedWeights):
        allVertexes = skinningTools.SkinningTools().convertToVertexList(self.model)
        jointAmount = len(self.joints)

        sourcePoint = []
        sourcePoints    = {}
        sourcePointPos = {}

        sourceUV = False
        for index, vert in enumerate(self.origVerts):   
            if len(vert) == 2:
                sourceUV = True 
            sourcePoint.append(vert)
            sourcePoints[index] = vert
            sourcePointPos[index] = inRemappedWeights[(index * jointAmount) : ((index+1) * jointAmount)]
            
        sourceKDTree = KDTree.construct_from_data(sourcePoint)   
        numberOfVertices = len(allVertexes)
        
        joint   = cmds.skinCluster(skinClusterName, q=True, inf=True)  
        
        percentage = 96.0/numberOfVertices
        weightlist = []
        
        for iteration, targetVertex in enumerate(allVertexes):
            pos = cmds.xform(targetVertex, q=1, ws=1, t=1)
            if sourceUV:
                alluvs = cmds.polyListComponentConversion(targetVertex, tuv=True)
                singleUV = cmds.filterExpand(alluvs, sm=35)[0]
                pos = cmds.polyEditUV(singleUV, q=True, u=True,v=True)

            pts = sourceKDTree.query(query_point = pos, t=self.nearest)
            
            weights, distanceWeightsArray, totalDistanceWeights = self._findClosestObjects( sourceKDTree, targetVertex, sourcePointPos,sourcePoints, sourceUV)
            newWeights= self._createWeightsList(jointAmount, weights, distanceWeightsArray, totalDistanceWeights)

            divider = sum(newWeights)
            
            weightsCreation = []
            for jnt in self.joints:
                for count, skinJoint in enumerate( joint ):
                    if jnt != skinJoint or divider == 0.0:
                        continue
                    weightsCreation.append((newWeights[count]/divider))
            weightlist.extend(weightsCreation)

            if self.progressBar != None:
                self.progressBar.setValue(percentage*iteration)
                qApp.processEvents()
        
        newWeights =[0.0] *  (numberOfVertices* len(joint))
        index = 0
        for vertex in allVertexes:
            number = int(vertex.split('.vtx[')[-1].split(']')[0])
            for jointIndex in xrange(jointAmount):
                weightindex = (number*jointAmount) + jointIndex
                newWeights[weightindex] = weightlist[index]
                index +=1
  
        shape = cmds.listRelatives(self.model, s=1)[0]
        cmds.SkinWeights([shape, skinClusterName] , nwt=newWeights)
        if self.progressBar != None:
            self.progressBar.setValue(100)
            qApp.processEvents()
    
    def loadSkincluster(self, inObject, origVerts = None, progressBar = None, nearest = 1):
        self.progressBar = progressBar
        self.nearest = 1
        if self.storedSkinInformation == None:
            cmds.error("no skinning info stored! please store information first")
        
        meshShapeName = cmds.listRelatives(inObject, s=True)[0]
        vertices =  skinningTools.SkinningTools().convertToVertexList(meshShapeName)
        
        remapWeights = False
        if len(vertices) != self.storedSkinInformation[1]:
            remapWeights = True
            self.nearest = 3
            cmds.warning("object mesh is different from stored, might give wrong results")
            
        skinCluster = skinningTools.SkinningTools().skinCluster(inObject, True)

        remapNeeded = False
        remappedJoints = None
        if skinCluster == None:
            jointsExist = True
            for jnt in self.storedSkinInformation[2]:
                if not cmds.objExists(jnt):
                    jointsExist = False
                    break

            if not jointsExist:
                cmds.warning("not all stored joints are present, skinning to all availableJoints")
                allJoints = cmds.ls(type = "joint")
                skinCluster = cmds.skinCluster(inObject, allJoints, tsb=True)[0]
                remapNeeded = True
                remappedJoints = allJoints
            else:
                skinCluster = cmds.skinCluster(inObject, self.storedSkinInformation[2], tsb=True)[0]
                remapNeeded = False
        else:

            influencingJoints = cmds.skinCluster(skinCluster, q=1, inf=1)
            if self.storedSkinInformation[2] != influencingJoints:
                remapNeeded = True
                remappedJoints = influencingJoints

        self.newPositions = []
        if not remapNeeded and remapWeights == False:
            cmds.SkinWeights([meshShapeName, skinCluster] , nwt=self.storedSkinInformation[0])
        elif not remapNeeded and remapWeights == True:
            self.setData( inObject, origVerts, progressBar, self.nearest, self.storedSkinInformation[2])
            self.remapWeights( skinCluster, self.storedSkinInformation[0])
        else:
            for jnt in remappedJoints:
                pos = cmds.xform(jnt, q=1, ws=1, t=1)
                self.newPositions.append([jnt, pos])
            self.remapJoints(self.storedSkinInformation, remappedJoints, inObject,  origVerts)

        self.storedSkinInformation = None
        return True


class MeshRemapper(object):
    def __init__(self):
        super(MeshRemapper, self).__init__()
        self.xmlList = {}
        self.amount = 1
        self.useUv = False        
        self.progressBar = None
        self.closeCommand  = None

    def show(self, inShapes, outShapes):
        def mayaMainWindow():
            from skinningTool import SkinningToolsUI
            mainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
            return SkinningToolsUI.wrapinstance(long(mainWindowPtr))
    
        mayaWindow = mayaMainWindow()
        window = remapDialog.RemapDialog(mayaWindow, self.setRemmapedDict)
        window.setBestGuess(True)
        window.addBase(sorted(inShapes))
        window.addTarget(sorted(outShapes))
        
        window.resize( 500, 700 )
        window.show()
        return window
        
    def onClose(self, inMap):
        if self.closeCommand == None:
            return

        for key, value in inMap.iteritems():
            for object in value:
                parent = cmds.listRelatives(object, parent=1)
                self.closeCommand(parent, self.xmlList[key], self.amount, self.useUv, self.progressBar)

    def setRemmapedDict(self, remapValues):
        self.remapdict = remapValues
        print "origFile", self.remapdict

    def setData(self, xmlList, amount, useUv, progressBar):
        self.xmlList = xmlList
        self.amount  = amount
        self.useUv   = useUv
        self.progressBar = progressBar

    def relinkMeshdata(self, inShapes, outShapes, CloseCommand):
        self.closeCommand = CloseCommand
        
        self.remap = self.show(inShapes, outShapes)
        self.remap.setCloseCommand(self.onClose)
        