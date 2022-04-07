from maya import OpenMaya, OpenMayaAnim, OpenMayaMPx 
'''
@NOTE: legacy python plugin for smoothing weight values as C++ plugin is used! 
'''

kPluginCmdName = "PLaverageVtxWeight"

class AverageVtxWeightCmd(MPxCommand):

	def __init__(self):
		MPxCommand.__init__(self)
		self.index     = ''
		self.value     = None
		self.fnSkin    = None
		self.component = None
		self.influenceIndices = None

		self.argSkinCluster = ''

		self.dagPath = MDagPath()
		self.oldWeights = MDoubleArray()

	def parseArgs(self, args):
		argData = MArgDatabase( self.syntax(), args )
		if argData.isFlagSet("sc"):
			self.argSkinCluster = argData.flagArgumentString("sc", 0)
		if argData.isFlagSet("i"):
			self.index 			= argData.flagArgumentString("i", 0)
		if argData.isFlagSet("w"):
			self.value 			= argData.flagArgumentDouble("w", 0)

	def isUndoable(self):
		return True

	def getSkinCluster(self):
		selectionList = MSelectionList()
		MGlobal.getSelectionListByName(self.argSkinCluster, selectionList)
		skinObj     = MObject()
		selectionList.getDependNode(0, skinObj)
		self.fnSkin = MFnSkinCluster(skinObj)
		return self.fnSkin
	
	def getMesh(self):
		selectionList = MSelectionList()
		MGlobal.getSelectionListByName(self.index, selectionList)
		meshPath       = MDagPath()
		meshComponents = MObject()
		selectionList.getDagPath(0, meshPath, meshComponents)
		return meshPath, meshComponents

	def doIt(self, args):
		try:
			self.parseArgs( args )
		except Exception, e:
			print '[' + kPluginCmdName + '] invalid flag syntax\n'
			return

		self.getSkinCluster()
		if not self.fnSkin:
			MGlobal.displayError("Select a mesh that contains a skinCluster.")
			return

		self.redoIt()

	def undoIt(self):
		self.fnSkin.setWeights(self.dagPath, 
							self.component, 
							self.influenceIndices, 
							self.oldWeights, 
							False)

	def redoIt(self):
		#current working component
		self.dagPath, self.component = self.getMesh()

		surroundingWghts    = MDoubleArray()
		surroundingVtxArray = MIntArray()
		infCount            = MScriptUtil()
		influence           = infCount.asUintPtr()

		# get vertices for averaging
		mitVtx = MItMeshVertex(self.dagPath, self.component)
		mitVtx.getConnectedVertices(surroundingVtxArray)
		
		# get surrounding vertices 
		surrComponents = MFnSingleIndexedComponent().create(MFn.kMeshVertComponent)
		MFnSingleIndexedComponent(surrComponents).addElements(surroundingVtxArray)

		# read weights
		self.fnSkin.getWeights(self.dagPath, self.component, self.oldWeights, influence)
		self.fnSkin.getWeights(self.dagPath, surrComponents, surroundingWghts, influence)
		influenceCount = MScriptUtil.getUint(influence)

		# get counts
		surroundingVtxCount    = surroundingVtxArray.length()
		surroudingWeightsCount = surroundingWghts.length()

		# reset variable
		self.influenceIndices = MIntArray()
		newWeights = MDoubleArray(influenceCount, 0.0)

		invValue = 1.0 - self.value

		# average all the surrounding vertex weights and multiply with blend value
		for i in xrange(influenceCount):
			self.influenceIndices.append(i)
			for j in xrange(i, surroudingWeightsCount, influenceCount):
			  	newWeights[i] += surroundingWghts[j]
		
		for i in xrange(influenceCount):
			newWeights[i] = ((newWeights[i] / surroundingVtxCount) - self.oldWeights[i]) * self.value + self.oldWeights[i]
		
		# set the weights
		self.fnSkin.setWeights(self.dagPath, 
							self.component, 
							self.influenceIndices, 
							newWeights, 
							False,
							self.oldWeights)
		
def cmdCreator():
	return asMPxPtr(AverageVtxWeightCmd())

def syntaxCreator():
	syntax = MSyntax()
	syntax.addFlag("sc", "skinCluster", MSyntax.kString  )
	syntax.addFlag("i",  "index", 		MSyntax.kString  )
	syntax.addFlag("w",  "weight", 		MSyntax.kDouble  )
	return syntax

def initializePlugin(mobject):
	mplugin = MFnPlugin(mobject, "PerryLeijten", "1.0", "Any")
	try:
		mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)
	except Exception, e:
		sys.stderr.write('Failed to register command:  %s\n' %kPluginCmdName)
		sys.stderr.write('%s\n' %e)

def uninitializePlugin(mobject):
	mplugin = MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand(kPluginCmdName)
	except Exception, e:
		sys.stderr.write('Failed to de-register command:  %s\n' %kPluginCmdName)
		sys.stderr.write('%s\n' %e)

	
