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

def polySkeleton(radius = 5):
    currentUnit = cmds.currentUnit(q=True, l=True)
    if currentUnit != 'cm':
        cmds.currentUnit(l='cm')
        
    selection = cmds.ls(type="joint")
    allGeo = []
    for joint in selection:
        sphere = cmds.polySphere()[0]
        point = cmds.pointConstraint(joint, sphere, mo=False)
        cmds.delete(point)
        cmds.setAttr(sphere+'.scaleX', radius)
        cmds.setAttr(sphere+'.scaleY', radius)
        cmds.setAttr(sphere+'.scaleZ', radius)                        
        allGeo.append(sphere)
        
        children = cmds.listRelatives(joint, type="joint")
        if children == None:
            pass
        else:
            for child in children:
                cone = cmds.polyCone()[0]
                cmds.setAttr(cone+'.translateY', 1)
                cmds.makeIdentity(cone, apply=True)
                cmds.move(0, 0, 0, cone +".scalePivot", cone +".rotatePivot", absolute=True)
                point = cmds.pointConstraint(joint,cone,mo=False)
                aim = cmds.aimConstraint(child, cone, aimVector=(0,1,0), upVector=(0,0,1), worldUpType= "scene")
                cmds.delete(point, aim)
                cmds.setAttr(cone+'.scaleX', radius)
                cmds.setAttr(cone+'.scaleY', radius)
                cmds.setAttr(cone+'.scaleZ', radius)                        
                getPos = cmds.xform(child, q=True,ws=True, t=True)
                cmds.xform(cone+'.vtx[20]', ws=True, t=getPos)
                allGeo.append(cone)
    cmds.polyUnite(allGeo)
    cmds.DeleteHistory(allGeo)
    cmds.currentUnit(l=currentUnit)
    
def showUI():
    
    cmds.window(t='skelBuilder')
    cmds.columnLayout( adjustableColumn=True )
    slider = cmds.floatSliderGrp('skelFloatSlider',field=True , min=0.1, max=10, value=5, step=.1 )
    cmds.button(l='buildSkeleton', c='from skinningTool import skeletonGeo;from maya import cmds; rad = cmds.floatSliderGrp(\'%s\', q=True, v=True); skeletonGeo.polySkeleton(rad)'%slider)
    cmds.showWindow()
