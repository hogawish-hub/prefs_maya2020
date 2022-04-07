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
# @TODO: still not working in all cases, needs refactor!!
# @TODO : check if possible to create swiss army knife from opengl to viewport2.0
# @TODO: use skinbinder technique to also generate proxy mesh

from maya import cmds, mel
from maya.api import OpenMaya
from maya.OpenMaya import *
from skinningTools import SkinningTools;
from random import randrange

from qtUtil import *

def apply_api_colors(colors, indices, obj):
    nColors = [ ]#= [OpenMaya.MColor(i) for i in colors]
    for color in colors:
        ncol= OpenMaya.MColor(color)
        nColors.append(ncol)
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(obj)
    nodeDagPath = selectionList.getDagPath(0)
    mfnMesh = OpenMaya.MFnMesh(nodeDagPath)
    mfnMesh.setVertexColors(nColors, indices)

def convertToIndexList( vertList):
    indices = []
    for i in vertList:
        index = int(i.split("[")[-1].split("]")[0])
        indices.append(index)
    return indices

def setColor( vertices ):
    mesh = vertices[0].split(".")[0]
    colorList =  [randrange(255), randrange(255),randrange(255), 255]
    iter = convertToIndexList(vertices)
    colors = [[randrange(10.0)/10.0, randrange(10.0)/10.0,randrange(10.0)/10.0, 1.0]] * len(vertices)
    apply_api_colors(colors, iter, mesh)

def extractFacesByVertices(vertices, internal=False):
    vertices = cmds.filterExpand(vertices, sm=31)

    dup = cmds.duplicate(vertices[0].rsplit('.',1)[0])[0]
    try:
        cmds.parent(dup, w=True)
    except:
        pass
    dup = '|' + dup
    for i in range(len(vertices)):
        vertices[i] = dup + '.' + vertices[i].rsplit('.',1)[-1]
    cmds.polyTriangulate(dup)
    if not vertices:
        cmds.delete(dup)
        return None
    faces = cmds.polyListComponentConversion(vertices, tf=True, internal=internal)
    if not faces:
        cmds.delete(dup)
        return None
    if not internal:
        vertices = cmds.filterExpand(cmds.polyListComponentConversion(faces, tv=True), sm=31)
    faces = cmds.filterExpand(faces, sm=34)
    if not faces:
        cmds.delete(dup)
        return None
    vertexPositions = MFloatPointArray()
    vertexMap = {}
    i = 0
    for vertex in vertices:
        vertexPositions.append(MFloatPoint(*cmds.xform(vertex, q=True, ws=True, t=True)))
        vertexMap[vertex.rsplit('[',1)[-1].split(']',1)[0]] = i
        i += 1

    ids = MIntArray()
    counts = MIntArray()
    for face in faces:
        faceVertices = cmds.filterExpand(cmds.polyListComponentConversion(face, tv=True), sm=31)
        counts.append(len(faceVertices))
        for vertex in faceVertices:
            ids.append(vertexMap[vertex.rsplit('[',1)[-1].split(']',1)[0]])

    m = MFnMesh()
    m.create(vertexPositions.length(), counts.length(), vertexPositions, counts, ids)

    path = m.fullPathName()
    cmds.delete(dup)
    if cmds.ls(path, type='mesh'):
        path = cmds.listRelatives(path, parent=True, f=True)
    return path

def cutCharacterFromSkin( objects, internal=False, fast =True,  progressBar = None):    
    amountInObj = len(objects)
    if amountInObj == 0:
        polys = cmds.ls(type = "mesh")
        for i in polys:
            tranform = cmds.listRelatives(i, parent=1)[0]   
            objects.append(transform)


    allGrp = []
    skinPercentage = 99.9/(len(objects))
    for iteration, convObj in enumerate(objects):
        
        skinClusterName = SkinningTools.skinCluster( convObj, silent=True )
        if skinClusterName == None:
            continue
        objectShape = cmds.listRelatives(convObj, s=1)[0]
        infAray = cmds.SkinWeights([objectShape, skinClusterName ],  q=True)

        expandedList = SkinningTools().convertToVertexList(convObj)
        amountVerts = len(expandedList )
        
        objList = []    
        if fast:
            attachedJoints = cmds.skinCluster(skinClusterName, q=1, inf=1)
            amountAttached = len(attachedJoints )

            jointDict = dict.fromkeys(attachedJoints)

            for key, value in jointDict.iteritems():
                jointDict[key] = []
               
            for index, vertex in enumerate(expandedList):
                valueList = []
                for id in range(amountAttached):
                    valueList.append(infAray[index*amountAttached + id])
                
                jointDict[attachedJoints[valueList.index(max(valueList))]].append(vertex)    
            
            for key, value in jointDict.iteritems():
                if len(jointDict[key]) == 0:
                    continue
                obj = extractFacesByVertices(jointDict[key], internal=False)

                if obj == None:
                    continue
                newObj = cmds.rename(obj[0], key+"_%s_Proxy"%convObj)
                if type(newObj) == list:
                    newObj = newObj[0]
                positionJnt = cmds.xform(key, q=1, ws=1, t=1)
                cmds.xform(newObj, piv=positionJnt, ws=True)
                cmds.parentConstraint(key,newObj, mo=1)
                cmds.scaleConstraint(key, newObj, mo=1)
                objList.append(newObj)
        else:
            attachedJoints = cmds.skinCluster(skinClusterName, q=1, wi=1)
            for bone in attachedJoints:
                cmds.select(cl=True)
                mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
                mel.eval('doMenuComponentSelection("%s", "%s");'%(convObj, "vertex"))
                cmds.skinCluster( skinClusterName , e=True , siv=bone )
                selected = cmds.ls(sl=True, fl=True)
                if selected == None or len(selected) == 0:
                    continue
                culled = []
                for vert in selected:
                    wgt = cmds.skinPercent( skinClusterName, vert, transform=bone, query=True )
                    if wgt < 0.3:
                        continue
                    culled.append(vert)
                if len(culled) == 0:
                    continue
                obj = extractFacesByVertices(culled)

                if obj == None:
                    continue
                newObj = cmds.rename(obj[0], bone+"_%s_Proxy"%convObj)
                if type(newObj) == list:
                    newObj = newObj[0]
                positionJnt = cmds.xform(bone, q=1, ws=1, t=1)
                cmds.xform(newObj, piv=positionJnt, ws=True)
                cmds.parentConstraint(bone,newObj, mo=1)
                cmds.scaleConstraint(bone, newObj, mo=1)
                objList.append(newObj)
       
        meshes = cmds.ls(objList, type='mesh', l=True) or []
        meshes.extend(cmds.listRelatives(objList, ad=True, type='mesh', f=True) or [])
        cmds.sets(meshes, edit=True, forceElement="initialShadingGroup")
        for mesh in meshes:
            cmds.polyNormal(mesh, normalMode=2, userNormalMode=0, ch=False)
            cmds.polySoftEdge(mesh, angle=65, ch=False)

        objGrp = cmds.group(objList, n="LowRez_%s"%convObj)
        allGrp.append(objGrp)
        if progressBar:
            progressBar.setValue((iteration+1)*skinPercentage)
            qApp.processEvents()
    finalGrp = cmds.group(allGrp, n="lowRez")
    if progressBar:
        progressBar.setValue(100)
        qApp.processEvents()

    return finalGrp