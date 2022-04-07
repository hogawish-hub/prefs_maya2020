#include <vector>


#undef NT_PLUGIN
#define MNoVersionString
#include <maya/MFnPlugin.h>
#undef MNoVersionString
#define NT_PLUGIN

#ifdef WIN32
#define _WINSOCKAPI_
#include <windows.h>
#endif
#ifndef MACOS
#include <GL/gl.h>
#else
#include <OpenGL/gl.h>
#endif

#include <maya/MObject.h>
#include "utils.hpp"
#include "skinweights.h"
#include "averagevtxweight.h"
//#include "skinningvisualizer.h"
//#include <maya/MDrawRegistry.h>

//static bool sUseLegacyDraw = (getenv("MAYA_ENABLE_VP2_PLUGIN_LOCATOR_LEGACY_DRAW") != NULL);


int __id = 0x65738500;
std::vector<int> ids;
int id()
{
	ids.push_back(__id);
	return __id++;
}

std::vector<MString> cmds;


#define REGISTERCOMMAND(COMMAND) cmds.push_back(#COMMAND); stat = plugin.registerCommand(#COMMAND, COMMAND::sCreator, COMMAND::sNewSyntax); THROWSTAT

#define REGISTERNODE(NODE) stat = plugin.registerNode(#NODE, id(), NODE::sCreator, NODE::sInitialize); THROWSTAT
#define REGISTERNODETYPE(NODE, TYPE) stat = plugin.registerNode(#NODE, id(), NODE::creator, NODE::initialize, TYPE); THROWSTAT


static const MString SkinningVisualizer_classification = "drawdb/geometry/skinningVisualizer"; 


MStatus initializePlugin(MObject pluginObj)
{
	MFnPlugin plugin(pluginObj, "Trevor van Hoof & Perry Leijten", "1.0", "any");
	MStatus stat;
	
	REGISTERCOMMAND(AverageVtxWeight);
	REGISTERCOMMAND(SkinWeights);
	
	//plugin.registerNode("SkinningVisualizer", id(), SkinningVisualizer::sCreator, SkinningVisualizer::sInitialize, MPxNode::kLocatorNode, &SkinningVisualizer_classification);
//#if MAYAVERSION > 2015
//    stat = MHWRender::MDrawRegistry::registerDrawOverrideCreator(SkinningVisualizer_classification, "SkinningVisualizer", SkinningVisualizerViewport2::sCreator);
//#endif
	return stat;
}


MStatus uninitializePlugin(MObject pluginObj)
{
	MFnPlugin plugin(pluginObj);
	MStatus stat;

	size_t i = ids.size();
	while (i > 0)
	{
		--i;
		stat = plugin.deregisterNode(ids[i]);
		THROWSTAT;
	}

//	stat = MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(SkinningVisualizer_classification, "SkinningVisualizer");
//	THROWSTAT;
	
	i = cmds.size();
	while (i > 0)
	{
		--i;
		stat = plugin.deregisterCommand(cmds[i]);
		THROWSTAT;
	}

	return stat;
}
