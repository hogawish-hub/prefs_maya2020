from maya import OpenMaya, OpenMayaAnim, OpenMayaMPx, mel, cmds
import sys
'''
@NOTE: legacy python plugin for skincluster interaction as C++ plugin is used! 
'''

kPluginCmdName = 'PLskinWeights'

class SkinCommands(MPxCommand):
    def __init__(self):
        MPxCommand.__init__(self)
        
        self.argSkinCluster = ''
        self.argMeshShapeName = ''
        self.argDataList = ''
        self.oldWeights = ''

        self.getFlagSkinWeights = True
        self.setFlagSkinWeights = False
        self.flagNormalise = True


    def parseArgs(self, args):
        argData = MArgDatabase( self.syntax(), args )
        if argData.isFlagSet('sc'):
            self.argSkinCluster = argData.flagArgumentString('sc', 0)
        if argData.isFlagSet('mn'):
            self.argMeshShapeName = argData.flagArgumentString('mn', 0)
        if argData.isFlagSet('wl'):
            self.argDataList = argData.flagArgumentString('wl', 0)            

        if argData.isFlagSet('gw'):
            self.getFlagSkinWeights = argData.flagArgumentInt('gw', 0)
        if argData.isFlagSet('sw'):
            self.setFlagSkinWeights = argData.flagArgumentInt('sw', 0)
        if argData.isFlagSet('sn'):
            self.flagNormalise = argData.flagArgumentInt('sn', 0)

    def isUndoable(self):
        return True

    def doIt(self, args):
        self.parseArgs( args )
        try:
            self.parseArgs( args )
        except Exception, e:
            print '[' + kPluginCmdName + '] invalid flag syntax\n'
            return
        self.redoIt()

    def redoIt(self):
        out =  self.getSkinWeights(self.argSkinCluster, self.argMeshShapeName)
        if self.getFlagSkinWeights:
            self.setResult( out )
        
        if self.setFlagSkinWeights:
            self.oldWeights = str(out)
            self.setSkinWeights(self.argSkinCluster, self.argMeshShapeName, self.argDataList)

    def undoIt(self):
        if self.oldWeights != '':
            self.setSkinWeights(self.argSkinCluster, self.argMeshShapeName, self.oldWeights)


    def getSkinCluster(self, skinClusterName):
        selectionList = MSelectionList()
        MGlobal.getSelectionListByName(skinClusterName, selectionList)
        skinObj = MObject()
        selectionList.getDependNode(0, skinObj)
        skin = MFnSkinCluster(skinObj)
        return skin
    
    def getMesh(self, meshShapeName):
        selectionList = MSelectionList()
        MGlobal.getSelectionListByName(meshShapeName+'.vtx[*]', selectionList)
        meshPath = MDagPath()
        meshComponents = MObject()
        selectionList.getDagPath(0, meshPath, meshComponents)
        return meshPath, meshComponents

    def getSkinWeights(self, skinClusterName, meshShapeName):
        #get skin cluster
        skin = self.getSkinCluster(skinClusterName)
        #get mesh
        meshPath, meshComponents = self.getMesh(meshShapeName)

        infArray = MIntArray()
        pathArray = MDagPathArray()
        skin.influenceObjects(pathArray)
        infCount = pathArray.length()
        for j in range(infCount):
            infArray.append(skin.indexForInfluenceObject(pathArray[j]))

        # find vert count on mesh
        vertCount = 0
        polyIter = MItMeshVertex(meshPath, meshComponents)
        vertCount = polyIter.count()

        valCount = infCount * vertCount
        valArray = MDoubleArray(valCount)

        # get array of values
        skin.getWeights(meshPath, meshComponents, infArray, valArray)
        return valArray

    def setSkinWeights(self, skinClusterName, meshShapeName, data):
        #get skin cluster
        skin = self.getSkinCluster(skinClusterName)
        #get mesh
        meshPath, meshComponents = self.getMesh(meshShapeName)

        infArray = MIntArray()
        pathArray = MDagPathArray()
        skin.influenceObjects(pathArray)
        infCount = pathArray.length()
        for j in range(infCount):
            infArray.append(skin.indexForInfluenceObject(pathArray[j]))
        
        dataArr = MDoubleArray()
        for v in data[1:-1].split(','):
            dataArr.append(float(v))
        skin.setWeights(meshPath, meshComponents, infArray, dataArr, False)


def cmdCreator():
    return asMPxPtr( SkinCommands() )

def syntaxCreator():

    syntax = MSyntax()

    syntax.addFlag( 'sc', 'skinCluster', MSyntax.kString  )
    syntax.addFlag( 'mn', 'meshShapeName', MSyntax.kString  )
    syntax.addFlag( 'wl', 'weightList', MSyntax.kString )

    syntax.addFlag( 'gw', 'getWeights', MSyntax.kDouble )
    syntax.addFlag( 'sw', 'setWeights', MSyntax.kDouble )
    syntax.addFlag( 'sn', 'shouldNormalise', MSyntax.kDouble )
    return syntax
 
def initializePlugin(mobject):
    mplugin = MFnPlugin(mobject, "PerryLeijten", "1.0", "Any")
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator, syntaxCreator)
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise
 
def uninitializePlugin(mobject):
    mplugin = MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )
        raise
