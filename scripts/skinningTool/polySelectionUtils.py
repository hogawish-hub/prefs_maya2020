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
import maya.OpenMaya as oldOpenMaya
import collections 
from maya import mel, cmds

M_SCRIPT_UTIL = oldOpenMaya.MScriptUtil()
            
def getConnectedVerts( mesh, vtxSelectionSet):
    '''
    http://www.janpijpers.com/finding-vertex-groups-in-maya/
    '''
    
    ## Creates a selection list (doesnt actually get anything yet) 
    selList = oldOpenMaya.MSelectionList()
    ## Adds the mesh to the list 
    selList.add(mesh)
    ## Old style maya create an object 
    mObject = oldOpenMaya.MObject()
    ## Get the dependancy node and put it into the mObject
    selList.getDependNode(0, mObject)

    ## Create a vertex itterator loop. 
    iterVertLoop = oldOpenMaya.MItMeshVertex(mObject)
    
    ## Empty set to keep track of who we talked to. 
    talkedToNeighbours = set() 
    
    districtDict =  collections.defaultdict(list) ## < OUR BIG NOTEBOOK!!!
    districtNr = 0 ## Our starting district. 
            
    ## For every index in our provided set. Get the connecting / neigbouring vertecies. 
    for currentIndex in vtxSelectionSet:
        
        ## An empty set that holds all house numbers. 
        districtHouses = set() 
        ## If our current index does is not in the talked to list. 
        ## We can process it. 
        if not currentIndex in talkedToNeighbours:
            ## this nr is part of our list and not seen before. 
            ## so we add it to the district
            districtHouses.add( currentIndex )
            currentNeighbours = getNeighbours(iterVertLoop, currentIndex)
            
            while currentNeighbours:
                newNeighbours = set() 
                for neighbour in currentNeighbours:
                    if neighbour in vtxSelectionSet and not neighbour in talkedToNeighbours:
                        talkedToNeighbours.add(neighbour)
                        districtHouses.add(neighbour)
                        newNeighbours = newNeighbours.union(getNeighbours(iterVertLoop, neighbour))
                        
                currentNeighbours = newNeighbours
            districtDict[districtNr] = districtHouses ## << Write down data in our big notebook 
            districtNr += 1 ## << goto the next page on our notebook. 
            
        ## Walk back to our original neighbour.  
        iterVertLoop.setIndex(currentIndex,M_SCRIPT_UTIL.asIntPtr())
        ## Go to the next neigbour. 
        iterVertLoop.next()

    return districtDict

def getNeighbours( mVtxItter, index):
    mVtxItter.setIndex( index, M_SCRIPT_UTIL.asIntPtr()) 
    intArray = oldOpenMaya.MIntArray()
    mVtxItter.getConnectedVertices(intArray)
    return set(int(x) for x in intArray)

def growLatticePoints(points):
    base =points[0].split('.')[0]
    allPoints = cmds.filterExpand("%s.pt[*]"%base, sm=46)

    extras = []
    for j in points:
        extras.append(j)
        a = int(j.split("[")[1].split("]")[0])
        b = int(j.split("[")[2].split("]")[0])
        c = int(j.split("[")[3].split("]")[0])
        for i in [-1, 1]:
            growa = "%s.pt[%s][%s][%s]"%(base, a+i, b, c)
            growb = "%s.pt[%s][%s][%s]"%(base, a, b+i, c)
            growc = "%s.pt[%s][%s][%s]"%(base, a, b, c+i)
            if growa in allPoints:
                extras.append(growa)
            if growb in allPoints:
                extras.append(growb)     
            if growc in allPoints:
                extras.append(growc)
    return extras