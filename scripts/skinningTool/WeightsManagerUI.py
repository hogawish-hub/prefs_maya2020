# -*- coding: utf-8 -*-
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
from maya           import cmds
from skinningTools  import SkinningTools
from remapper  import JointRemapper

import xml.etree.cElementTree as ET
import os, shutil, tempfile

from qtUtil import *

class WeightsManager(object):
    def __init__(self):
        super(WeightsManager, self).__init__()
        self.rempapper = JointRemapper()
        self.importSettings = None
        self.progressBar = None
        self.mayaVersion = int(str(cmds.about(apiVersion=True))[:-2])
        self.usedXmlFile = None

    def __checkXML(self, XmlFile):
        if not self.usedXmlFile == None:
            return
        if os.path.isfile(XmlFile):
            e = ET.parse(XmlFile).getroot()
        else:
            e = ET.fromstring(XmlFile)
        self.usedXmlFile = e

    def _forceExtraData(self, inObject, XmlFile):
        self.__checkXML(XmlFile)
        shape = self.usedXmlFile.find("shape")
        faceCountsSize = len(cmds.ls(inObject+'.f[*]', fl=1))
        faceVertices=''
        vertexCountSize = 0
        connectedVertexElementList = ""
        
        weights = self.usedXmlFile.findall("weights")
        percentage = 49.0 / len(weights)
        # add joint positions
        for iter, jnt in enumerate(weights):
            jntName = jnt.get("source")
            pos = cmds.xform(jntName, q=1, ws=1, t=1)
            jnt.set("jntPos", "%.3f %.3f %.3f"%(pos[0], pos[1], pos[2]))
            if self.progressBar != None:
                self.progressBar.setValue(percentage*iter)
                qApp.processEvents()

        # add uv coords
        base = self.usedXmlFile.find("shape")
        base.set("BB", "%s"%[ int(round(elem)) for elem in cmds.exactWorldBoundingBox(inObject) ])
        verts = base.findall("point")
        percentage = 49.0 / len(verts)
        for iter, aPoint in enumerate(verts):
            alluvs      = cmds.polyListComponentConversion("%s.vtx[%s]"%(inObject, aPoint.get("index")), tuv=True)
            if alluvs == None or len(alluvs) == 0:
                # don't try to add uv's when we don't have them
                continue
            singleUV    = cmds.filterExpand(alluvs, sm=35)[0]
            uvcoord     = cmds.polyEditUV(singleUV, q=True, u=True,v=True)        
            aPoint.set("uv", "%.3f %.3f"%(uvcoord[0], uvcoord[1]))
            if self.progressBar != None:
                self.progressBar.setValue(50 + (percentage*iter))
                qApp.processEvents()

        if self.mayaVersion < 2016:
        # add connected vertices no mather wich maya version and no need for cv flag anymore
            for face in range(faceCountsSize):
                expandedVertices  =SkinningTools().convertToVertexList( inObject+'.f[%s]'%face )
                faceVertices += "%s "%len(expandedVertices)
                for vert in sorted(expandedVertices):
                    connectedVertexElementList += "%s "%vert.split("[")[-1].split("]")[0]
                    vertexCountSize+=1

            polygonCountsChild = ET.SubElement(shape, "polygonCounts")
            polygonCountsChild.set("size", str(faceCountsSize))
            polygonCountsChild.set("polygonCounts", faceVertices)
            polygonConnectsChild = ET.SubElement(shape, "polygonConnects")
            polygonConnectsChild.set("size", str(vertexCountSize))
            polygonConnectsChild.set("polygonConnects", connectedVertexElementList)

        tree = ET.ElementTree(self.usedXmlFile)
        tree.write(XmlFile)
        self.clearXmlData()
        

    def writeSkinBinary(self, inObject, weightdirectory, progressBar = None):
        #@TODO: map prebind pose to calc from? both while savind and importing?
        self.progressBar = progressBar
        skinClusterName = SkinningTools().skinCluster(inObject, True)
        if not skinClusterName:
            cmds.warning("no skinCluster found attached to %s!"%inObject)
            return None
        if self.mayaVersion < 2016:        
            cmds.deformerWeights ("%s.xml"%inObject, p = weightdirectory, ex=True, deformer=skinClusterName)
        else:
            cmds.deformerWeights ("%s.xml"%inObject, p = weightdirectory, vc =True, ex=True, deformer=skinClusterName)

        xmlFile = os.path.join(weightdirectory, "%s.xml"%inObject)
        self._forceExtraData(inObject, xmlFile)
        if self.progressBar != None:
            self.progressBar.setValue(100)
            qApp.processEvents()

        return xmlFile

    def clearXmlData(self):
        if self.usedXmlFile != None:
            self.usedXmlFile.clear()
            self.usedXmlFile = None

    def _getJointInfoFromXML(self, XmlFile):
        self.__checkXML(XmlFile)
        usedJoints= []
        jointPos = []
        for elem in self.usedXmlFile.iter("weights"):
            usedJoints.append(elem.get('source'))
            positions = elem.get('jntPos').split(" ")
            nPos = [float(positions[0]), float(positions[1]),float(positions[2])]
            jointPos.append(nPos)
        return usedJoints, jointPos
    
    def _getShapeInfoFromXML(self, XmlFile):
        self.__checkXML(XmlFile)
        for i in self.usedXmlFile.iter("shape"):
            shapeName = i.get("name")
            return shapeName

    def _getBBInfoFromXML(self, XmlFile):
        self.__checkXML(XmlFile)
        for i in self.usedXmlFile.iter("shape"):
            BBox = i.get("BB")
            return BBox

    def _getVertexInfoFromXML(self, XmlFile):
        self.__checkXML(XmlFile)
        for i in self.usedXmlFile.iter("shape"):
            vertLength = int(i.get("size"))
            return vertLength

    def _getUVPosInfoFromXML(self, XmlFile):
        self.__checkXML(XmlFile)
        positions = []
        for elem in self.usedXmlFile.iter("shape"):
            for point in elem.iter("point"):
                vertPos = point.get("uv").split(" ")
                positions.append([float(vertPos[0]), float(vertPos[1])])
        return positions
    
    def _getVertexPosInfoFromXML(self, XmlFile):
        self.__checkXML(XmlFile)
        positions = []
        for elem in self.usedXmlFile.iter("shape"):
            for point in elem.iter("point"):
                vertPos = point.get("value").split(" ")[1:]
                positions.append([float(vertPos[0]), float(vertPos[1]), float(vertPos[2])])
        return positions

    def _constructWeightList(self, XmlFile):
        jnts = self._getJointInfoFromXML(XmlFile)[0]
        vertexAmount = self._getVertexInfoFromXML(XmlFile)

        amountJnts = len(jnts)
        listSize = amountJnts * vertexAmount
        weightList = [0.0] * listSize

        percentage = 99.0 / amountJnts
        self.__checkXML(XmlFile)
        for idx, elem in enumerate(self.usedXmlFile.iter("weights")):
            for point in elem.iter("point"):
                curIndex = int(point.get("index")) 
                curVal = float(point.get("value")) 

                listIndex = (curIndex * amountJnts) + idx
                weightList[listIndex] = curVal

            if self.progressBar != None:
                self.progressBar.setValue(idx* percentage)
                qApp.processEvents()
        return weightList

    def analyseXml(self, XmlFile):
        # @TODO: remap missing shape names as well?
        # @TODO: what to do if shapnames cannot be mapped?
        # @TODO: if joints dont match, open remapper, find matching joints and make temp xml with data to fix loading of weights

        joints, jointsPositions = self._getJointInfoFromXML(XmlFile)
        jointsExist = True
        for jnt in joints:
            if not cmds.objExists(jnt):
                jointsExist = False
                break

        if jointsExist:
            return False
        vertexAmount = self._getVertexInfoFromXML(XmlFile)

        weightList = self._constructWeightList(XmlFile)

        weightsInfo = (weightList, vertexAmount, joints, jointsPositions)
        return weightsInfo

    def _generateImportTempXML(self, jointMap):
        # generate a temporary xml that holds new joint info generated from remapper to import weights as fast as possible
        temp_folder = tempfile.gettempdir()
        
        dirictory, file = os.path.split(self.importSettings[0])
        
        newXml= os.path.join(temp_folder,file )
        shutil.copy(self.importSettings[0], newXml)
        
        self.__checkXML(XmlFile)
        for idx, weights in enumerate(self.usedXmlFile.findall('weights')):
            origJntName = weights.get('source')
            newName = jointMap[origJntName][0]
            weights.set('source', newName)


        cmds.deformerWeights (file, p = temp_folder, im=True, m="index", deformer=self.importSettings[2])


    def setWeightsByVertexId(self, selection, XmlFile, progressBar= None): 
        if type(selection) == str():
            selection = [selection]
        for iteration, inObject in enumerate(selection):
            skinClusterName = SkinningTools().skinCluster(inObject, True)
            
            WeightInfo = self.analyseXml(XmlFile)
            if WeightInfo == False:
                if skinClusterName == None:
                    xmlJoints, __ = self._getJointInfoFromXML(XmlFile)
                    skinClusterName = cmds.skinCluster(inObject, xmlJoints, tsb=True)[0]

                self.progressBar = progressBar    
                weightdirectory, fileName =  os.path.split(XmlFile)
                cmds.deformerWeights (fileName, p = weightdirectory, im=True, m="index", deformer=skinClusterName)
                cmds.skinPercent(skinClusterName,inObject, normalize=1 )
            else:
                self.progressBar = progressBar
                allJoints = cmds.ls(type = "joint")
                if skinClusterName != None:
                    cmds.skinCluster(inObject ,e =1, ub=1)

                skinCluster = cmds.skinCluster(inObject, allJoints, tsb=True)[0]
                self.rempapper.preStoreSkinCluster(WeightInfo)
                self.rempapper.loadSkincluster(inObject)
                cmds.skinPercent(skinCluster,inObject, normalize=1 )

        if progressBar != None:
            progressBar.setValue(100)
            qApp.processEvents()

        self.clearXmlData()

    def setWeightsByPosition(self,selection, XmlFile,amountValue = 1, progressBar= None):
        ## 2 
        if type(selection) == str():
            selection = [selection]
        for iteration, inObject in enumerate(selection):
            skinClusterName = SkinningTools().skinCluster(inObject, True)
            
            WeightInfo = self.analyseXml(XmlFile)
            vertPos = self._getVertexPosInfoFromXML(XmlFile)
            if WeightInfo == False:
                xmlJoints, __ = self._getJointInfoFromXML(XmlFile)
                if skinClusterName == None:
                    skinClusterName = cmds.skinCluster(inObject, xmlJoints, tsb=True)[0]

                weightdirectory, fileName =  os.path.split(XmlFile)
                if self.mayaVersion > 2015: 
                    operation = "linear"
                    if amountValue > 1:
                        operation = "barycentric"
                    cmds.deformerWeights (fileName, p = weightdirectory, im=True, m=operation, deformer=skinClusterName)
                else:
                    self.rempapper.setData(inObject, vertPos, progressBar, amountValue, xmlJoints)
                    self.rempapper.remapWeights( skinClusterName, self._constructWeightList(XmlFile))
                cmds.skinPercent(skinClusterName,inObject, normalize=1 )

            else:
                self.progressBar = progressBar
                allJoints = cmds.ls(type = "joint")
                if skinClusterName != None:
                    cmds.skinCluster(inObject ,e =1, ub=1)

                skinCluster = cmds.skinCluster(inObject, allJoints, tsb=True)[0]
                # fix skinweight info before goint into jointremapper
                
                self.rempapper.preStoreSkinCluster(WeightInfo)
                self.importSettings = (XmlFile, "index", skinCluster)
                self.rempapper.loadSkincluster(inObject, vertPos, progressBar, amountValue)
                cmds.skinPercent(skinCluster,inObject, normalize=1 )

        if progressBar != None:
            progressBar.setValue(100)
            qApp.processEvents()

        self.clearXmlData()

    def setWeigthsByUv(self,selection, XmlFile, amountValue = 1, progressBar= None):
        ## 4 
        if type(selection) == str():
            selection = [selection]
        for iteration, inObject in enumerate(selection):
            skinClusterName = SkinningTools().skinCluster(inObject, True)
            
            WeightInfo = self.analyseXml(XmlFile)
            UVPos = self._getUVPosInfoFromXML(XmlFile)
            if WeightInfo == False:
                xmlJoints, __ = self._getJointInfoFromXML(XmlFile)
                if skinClusterName == None:
                    skinClusterName = cmds.skinCluster(inObject, xmlJoints, tsb=True)[0]

                weightdirectory, fileName =  os.path.split(XmlFile)
                self.rempapper.setData(inObject, UVPos, progressBar, amountValue, xmlJoints)
                self.rempapper.remapWeights( skinClusterName, self._constructWeightList(XmlFile))
                cmds.skinPercent(skinClusterName,inObject, normalize=1 )

            else:
                self.progressBar = progressBar
                allJoints = cmds.ls(type = "joint")
                if skinClusterName != None:
                    cmds.skinCluster(inObject ,e =1, ub=1)
                    
                skinCluster = cmds.skinCluster(inObject, allJoints, tsb=True)[0]
                # fix skinweight info before goint into jointremapper
                
                self.rempapper.preStoreSkinCluster(WeightInfo)
                self.importSettings = (XmlFile, "index", skinCluster)
                self.rempapper.loadSkincluster(inObject, UVPos, progressBar, amountValue)
                cmds.skinPercent(skinCluster,inObject, normalize=1 )

        if progressBar != None:
            progressBar.setValue(100)
            qApp.processEvents()

        self.clearXmlData()
