#
#    ngSkinTools
#    Copyright (c) 2009-2017 Viktoras Makauskas.
#    All rights reserved.
#    
#    Get more information at 
#        http://www.ngskintools.com
#    
#    --------------------------------------------------------------------------
#
#    The coded instructions, statements, computer programs, and/or related
#    material (collectively the "Data") in these files are subject to the terms 
#    and conditions defined by EULA.
#         
#    A copy of EULA can be found in file 'LICENSE.txt', which is part 
#    of this source code package.
#    

from maya import cmds
from ngSkinTools.utils import Utils

class SelectHelper:
    @staticmethod  
    def getSelectionDagPaths(hilite):
        '''
        similar functionality to cmds.ls, but returns transform nodes where shapes might be selected,
        and does not return components.
        '''
        
        from maya import OpenMaya as om
        
        selection = om.MSelectionList();
        if hilite:
            om.MGlobal.getHiliteList(selection)
        else:
            om.MGlobal.getActiveSelectionList(selection)
            
        result = []
        for i in Utils.mIter(om.MItSelectionList(selection)):
            path = om.MDagPath()
            i.getDagPath(path)
            
            selectionPath = path.fullPathName()
            
            # if it's a shape node, extend upwards
            if path.node().hasFn(om.MFn.kShape):
                parentPath = om.MDagPath()
                om.MFnDagNode(om.MFnDagNode(path).parent(0)).getPath(parentPath)
                selectionPath = parentPath.fullPathName()
                
            if not selectionPath in result:
                result.append(selectionPath)
                
        return result
        
        
    @staticmethod
    def replaceHighlight(newHiglightItems):
        selection = SelectHelper.getSelectionDagPaths(False)
        hilite = SelectHelper.getSelectionDagPaths(True)
        
        
        # include selected objects that were in previous hilite
        newHilite = [i for i in hilite if i in selection]
        newHilite.extend(newHiglightItems)
        
        # make sure we can hilite stuff...
        newHilite = [i for i in newHilite if cmds.objExists(i)]
        
        
        
        # remove previous hilite
        if len(hilite) > 0:
            cmds.hilite(hilite, u=True)
            
        # set new hilite
        if len(newHilite) > 0: 
            cmds.hilite(newHilite, r=True)
