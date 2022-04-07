#include "skinningvisualizer.h"



#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>
#include <maya/MStatus.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MPlugArray.h>
#include <maya/MFnDagNode.h>
#include <maya/MDagPath.h>
#include <maya/MFnCamera.h>
#include <maya/MFloatMatrix.h>
#include <maya/MVectorArray.h>



#define PI 3.14159265359
#define TAU (2 * PI)



Float3::Float3() : 
	x(0.0f),
	y(0.0f),
	z(0.0f)
{
}



Float3::Float3(float x, float y, float z) :
	x(x),
	y(y),
	z(z)
{
}



MObject SkinningVisualizer::sDrawIt;
MObject SkinningVisualizer::sDrawInFront;
MObject SkinningVisualizer::sTransparency;
MObject SkinningVisualizer::sRadius;
MObject SkinningVisualizer::sSegments;
MObject SkinningVisualizer::sControlColor;
MObject SkinningVisualizer::sClickedColor;
MObject SkinningVisualizer::sDiscColor;
MObject SkinningVisualizer::sAmountConnected;
MObject SkinningVisualizer::sScreenSpaceDiscs;
MObject SkinningVisualizer::sCullSpaceDiscs;
MObject SkinningVisualizer::sPairs;
MObject SkinningVisualizer::sMatStart;
MObject SkinningVisualizer::sMatEnd;



bool DrawIt(const MObject& node)
{
	return MPlug(node, SkinningVisualizer::sDrawIt).asBool();
}

bool DrawInFront(const MObject& node)
{
	return MPlug(node, SkinningVisualizer::sDrawInFront).asBool();
}


float Transparency(const MObject& node)
{
	return MPlug(node, SkinningVisualizer::sTransparency).asFloat();
}



float Radius(const MObject& node)
{
	return MPlug(node, SkinningVisualizer::sRadius).asFloat();
}



int Segments(const MObject& node)
{
	return MPlug(node, SkinningVisualizer::sSegments).asInt();
}



int AmountConnected(const MObject& node)
{
	return MPlug(node, SkinningVisualizer::sAmountConnected).asInt();
}

Float3 ControlColor(const MObject& node)
{
	MFnNumericData data(MPlug(node, SkinningVisualizer::sControlColor).asMObject());
	Float3 result;
	data.getData3Float(result.x, result.y, result.z);
	return result;
}



Float3 ClickedColor(const MObject& node)
{
	MFnNumericData data(MPlug(node, SkinningVisualizer::sClickedColor).asMObject());
	Float3 result;
	data.getData3Float(result.x, result.y, result.z);
	return result;
}



Float3 DiscColor(const MObject& node)
{
	MFnNumericData data(MPlug(node, SkinningVisualizer::sDiscColor).asMObject());
	Float3 result;
	data.getData3Float(result.x, result.y, result.z);
	return result;
}

Line::Line(MVector start, MVector end):
	start(start), end(end)
{}

bool ScreenSpaceDiscs(const MObject& node)
{
	return MPlug(node, SkinningVisualizer::sScreenSpaceDiscs).asBool();
}



bool CullSpaceDiscs(const MObject& node)
{
	return MPlug(node, SkinningVisualizer::sCullSpaceDiscs).asBool();
}



MStatus SkinningVisualizer::sInitialize()
{
	MStatus stat;

	MFnNumericAttribute numFn;

	sDrawIt = numFn.create( "drawIt", "dwi", MFnNumericData::kBoolean, 1,&stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setStorable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setWritable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = addAttribute( sDrawIt ); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sDrawInFront = numFn.create( "drawInFront", "dif", MFnNumericData::kBoolean, 1,&stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setStorable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setWritable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = addAttribute( sDrawInFront ); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sTransparency = numFn.create( "transparency", "ts", MFnNumericData::kFloat, 1.0 ,&stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
    stat = numFn.setStorable(true); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setMin( 0.0 ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setMax( 1.0 ); CHECK_MSTATUS_AND_RETURN_IT(stat);
    stat = addAttribute( sTransparency); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sRadius = numFn.create( "radius", "r", MFnNumericData::kFloat, 1.0,&stat ); CHECK_MSTATUS_AND_RETURN_IT(stat);
    stat = numFn.setStorable(true); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setKeyable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
    stat = addAttribute( sRadius); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sSegments = numFn.create( "segments", "seg", MFnNumericData::kInt, 12 ,&stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setKeyable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setMin( 3 ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setStorable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = addAttribute( sSegments ); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sAmountConnected = numFn.create( "amountConnected", "acc", MFnNumericData::kInt, 4, &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setKeyable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setMin( 2 ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setStorable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = addAttribute( sAmountConnected ); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sControlColor = numFn.createColor( "controlColor", "ctrc", &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
    stat = numFn.setStorable(true); CHECK_MSTATUS_AND_RETURN_IT(stat);
    stat = addAttribute( sControlColor  ); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sClickedColor = numFn.createColor( "clickedColor", "clkc", &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
    stat = numFn.setStorable(true); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = addAttribute( sClickedColor ); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sDiscColor = numFn.createColor( "discColor", "dskc", &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
    stat = numFn.setStorable(true); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = addAttribute( sDiscColor ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	
	sScreenSpaceDiscs = numFn.create( "screenSpaceDiscs", "ssd", MFnNumericData::kBoolean, 1, &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setStorable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setWritable( true ); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = addAttribute( sScreenSpaceDiscs ); CHECK_MSTATUS_AND_RETURN_IT(stat);

	sCullSpaceDiscs = numFn.create( "cullSpaceDiscs", "csd", MFnNumericData::kBoolean, 0, &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setStorable(true); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = numFn.setWritable(true); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = addAttribute(sCullSpaceDiscs); CHECK_MSTATUS_AND_RETURN_IT(stat);

	// joint layout
	MFnCompoundAttribute comp;
	sPairs = comp.create("jointPairs", "jpr", &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = comp.setArray(true); CHECK_MSTATUS_AND_RETURN_IT(stat);

	MFnMatrixAttribute mat;
	sMatStart = mat.create("worldMatrixStart", "wms", MFnMatrixAttribute::kDouble, &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = comp.addChild(sMatStart); CHECK_MSTATUS_AND_RETURN_IT(stat);
	sMatEnd = mat.create("worldMatrixEnd", "wme", MFnMatrixAttribute::kDouble, &stat); CHECK_MSTATUS_AND_RETURN_IT(stat);
	stat = comp.addChild(sMatEnd); CHECK_MSTATUS_AND_RETURN_IT(stat);

	addAttribute(sPairs);

	return stat;
}



void JointWorldPositions(const MObject& node, std::vector<Line>& outData)
{
	MPlug pairs(node, SkinningVisualizer::sPairs);
	MIntArray indices;
	pairs.getExistingArrayAttributeIndices(indices);
	for(unsigned int i = 0; i < indices.length(); ++i)
	{
		MPlug pair = pairs.elementByLogicalIndex(indices[i]);
		MFnMatrixData startData(pair.child(0).asMObject());
		MFnMatrixData endData(pair.child(1).asMObject());
		MMatrix startMatrix = startData.matrix();
		MMatrix endMatrix = endData.matrix();
		MVector start(startMatrix(3, 0), startMatrix(3, 1), startMatrix(3, 2));
		MVector end(endMatrix(3, 0), endMatrix(3, 1), endMatrix(3, 2));
		outData.push_back(Line(start, end));
	}
}



MObject FirstSelectedObject()
{
	MSelectionList selected;
	MGlobal::getActiveSelectionList(selected);
	MObject obj;
	selected.getDependNode(0, obj); // allow for more then just the first selected object???
	return obj;
}



int SelectedBoneIndex(MObject node)
{
	MObject selected = FirstSelectedObject();

	MPlug pairs(node, SkinningVisualizer::sPairs);
	MIntArray indices;
	pairs.getExistingArrayAttributeIndices(indices);
	for(unsigned int i = 0 ;i < indices.length(); ++i)
	{
		MPlug pair = pairs.elementByLogicalIndex(indices[i]);
		
		MPlugArray inputs;
		pair.child(0).connectedTo(inputs, true, false);
		for(unsigned int j  = 0 ; j < inputs.length(); ++j)
		{
			MObject inputNode = inputs[j].node();
			if(inputNode == selected)
			{
				return i;
			}
		}
		
		pair.child(1).connectedTo(inputs, true, false);
		for(unsigned int j  = 0 ; j < inputs.length(); ++j)
		{
			MObject inputNode = inputs[j].node();
			if(inputNode == selected)
			{
				return i;
			}
		}
	}

	return -1;
}



MVector WorldSpaceCameraPos()
{
	MDagPath camera;
	M3dView::active3dView().getCamera(camera);
	MFnCamera fnCamera(camera);
	MFnDagNode dagPathCam( fnCamera.parent(0) );
	MDagPath camDagNode;
	dagPathCam.getPath(camDagNode);
	MMatrix worldCamPos = camDagNode.inclusiveMatrix();
	return MVector(worldCamPos( 3, 0 ), worldCamPos( 3, 1 ), worldCamPos( 3, 2 ));
}



void GLLookAt(MVector at, MVector eye)
{
	MVector forward = (at - eye).normal();
	MVector up = eye ^ at;
	MVector right = up.normal() ^ forward;
	up = forward ^ right;

	float m[16] = {(float)right.x, (float)right.y, (float)right.z, 0.0f,
		(float)up.x, (float)up.y, (float)up.z, 0.0f,
		(float)forward.x, (float)forward.y, (float)forward.z, 0.0f,
		0.0f, 0.0f, 0.0f, 1.0f};
	glMultMatrixf(m);
}



void GLDrawDisc(int numDivisions, float radius)
{
	glBegin(GL_TRIANGLE_FAN);
	glVertex2d(0.0f, 0.0f);
	for(int i = 0; i <= numDivisions; i++)
	{
		float x = radius * (float)cos(i *  TAU / (float)numDivisions);
		float y = radius * (float)sin(i * TAU / (float)numDivisions);
		glVertex2d(x, y);
	}
	glEnd();
}



float Min(float a, float b)
{
	if(a < b)
		return a;
	return b;
}



int Min(int a, int b)
{
	if(a < b)
		return a;
	return b;
}



int Max(int a, int b)
{
	if(a > b)
		return a;
	return b;
}



void GLMultMMatrix(MMatrix inverse)
{
	float m[16] = {
	(float)inverse(0,0), (float)inverse(0,1), (float)inverse(0,2), (float)inverse(0,3),
	(float)inverse(1,0), (float)inverse(1,1), (float)inverse(1,2), (float)inverse(1,3),
	(float)inverse(2,0), (float)inverse(2,1), (float)inverse(2,2), (float)inverse(2,3),
	(float)inverse(3,0), (float)inverse(3,1), (float)inverse(3,2), (float)inverse(3,3)};
	glMultMatrixf(m);
}



BestNPoints::BestNPoints() : 
	nearestPoints((unsigned int)0),
	referencePoints((unsigned int)0),
	largestBestIdx((unsigned int)0),
	bestDistances(0, DBL_MAX)
{
}



BestNPoints::BestNPoints(int pointsToFind) : 
	nearestPoints(Max(1, pointsToFind)),
	referencePoints(Max(1, pointsToFind)),
	largestBestIdx((unsigned int)0),
	bestDistances(Max(1, pointsToFind), DBL_MAX)
{
}



void BestNPoints::Measure(const MVector& reference, const MVector& newPoint)
{
	// Get distance from point to point
	float distance = (float)(newPoint - reference).length();

	bool dirty = false;

	// If the given point is already in the list but this distance is better, update the distance
	for(unsigned int i = 0 ; i < nearestPoints.length() ; ++i)
	{
		if(nearestPoints[i] == newPoint && distance < bestDistances[i])
		{
			bestDistances[i] = distance;
			referencePoints[i] = reference;
			dirty = true;
			break;
		}
	}

	if(!dirty && distance < bestDistances[largestBestIdx])
	{
		// If point is closer, store it
		nearestPoints[largestBestIdx] = newPoint;
		referencePoints[largestBestIdx] = reference;
		bestDistances[largestBestIdx] = distance;

		dirty = true;
	}

	if(!dirty)
		return;

	// Find the worst result so far (so we can replace it when finding a better candidate)
	double largestBestDist = bestDistances[0];
	largestBestIdx = 0;
	for(unsigned int i =1 ; i < nearestPoints.length(); ++i)
	{
		if(bestDistances[i] > largestBestDist)
		{
			largestBestDist = bestDistances[i];
			largestBestIdx = i;
		}
	}
}



void NearestPointsToSelectedBone(int selectedBone, const std::vector<Line>& jointPositions, BestNPoints& outData)
{
	if(selectedBone == -1)
		return;
	
	// For each bone
	for(size_t i = 0 ; i < jointPositions.size(); ++i)
	{
		if(i == selectedBone)
			continue;
		
		// Get distance from point to point, store best candidates
		outData.Measure(jointPositions[i].start, jointPositions[selectedBone].start);
		outData.Measure(jointPositions[i].start, jointPositions[selectedBone].end);
		outData.Measure(jointPositions[i].end, jointPositions[selectedBone].start);
		outData.Measure(jointPositions[i].end, jointPositions[selectedBone].end);
	}
}



void SkinningVisualizer::draw(M3dView& ioView, const MDagPath& inPath, M3dView::DisplayStyle inStyle, M3dView::DisplayStatus inStatus)
{
	if(!DrawIt(thisMObject()))
		return;

	std::vector<Line> jointPositions;
	JointWorldPositions(thisMObject(), jointPositions);
	
	MVector cameraPosition = WorldSpaceCameraPos();
	
	/* Set world space */
	glPushMatrix();
	GLMultMMatrix(inPath.inclusiveMatrixInverse());
	
	/* Draw bones and helper discs */
	glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT | GL_ENABLE_BIT);
	glDisable(GL_CULL_FACE);
	
	glDisable(GL_DEPTH_TEST);
	// glDisable(GL_DEPTH_TEST);//draw in front
	glLineWidth(2.0f);
	Float3 clickedColor = ClickedColor(thisMObject());
	Float3 controlColor = ControlColor(thisMObject());
	float alpha = Transparency(thisMObject());
	int selectedBone = SelectedBoneIndex(thisMObject());
	for(size_t i = 0 ; i < jointPositions.size(); ++i)
	{
		const Line& line = jointPositions[i];
		if(i == selectedBone)
		{
			glColor4f(clickedColor.x, clickedColor.y, clickedColor.z, alpha);
		}
		else
		{
			glColor4f(controlColor.x, controlColor.y, controlColor.z, alpha);
		}

		// Draw disc for start, facing the camera
		glPushMatrix();
		glTranslatef((float)line.start.x, (float)line.start.y, (float)line.start.z);
		GLLookAt(line.start, cameraPosition);
		float radius = Min((float)(line.start - cameraPosition).length() * 0.01f, 1.0f);
		GLDrawDisc(12, radius);
		glPopMatrix();
		
		// Draw disc for end, facing the camera
		glPushMatrix();
		glTranslatef((float)line.end.x, (float)line.end.y, (float)line.end.z);
		GLLookAt(line.end, cameraPosition);
		radius = Min((float)(line.end - cameraPosition).length() * 0.01f, 1.0f);
		GLDrawDisc(12, radius);
		glPopMatrix();
		
		// Draw dashed line
		glEnable(GL_LINE_STIPPLE);
		glBegin(GL_LINES);
		glVertex3d(line.start.x, line.start.y, line.start.z);
		glVertex3d(line.end.x, line.end.y, line.end.z);
		glEnd();
		glDisable(GL_LINE_STIPPLE);
	}
	
	/* Draw n-nearest planes of selected bone */
	if (!DrawInFront(thisMObject())){
		glEnable(GL_DEPTH_TEST);
	}

	if(selectedBone != -1)
	{
		int a = AmountConnected(thisMObject());
		int b = (int)(jointPositions.size() * 2 - 2);
		int c = Min(a, b);
		BestNPoints bestPoints(c);
		NearestPointsToSelectedBone(selectedBone, jointPositions, bestPoints);
		
		float radius = Radius(thisMObject());
		Float3 discColor = DiscColor(thisMObject());

		
		for(unsigned int i = 0 ; i < bestPoints.nearestPoints.length(); ++i)
		{
			if(bestPoints.bestDistances[i] == INFINITY)
				continue;
			glColor4f(discColor.x, discColor.y, discColor.z, alpha);
			glBegin(GL_LINES);
			glVertex3d(bestPoints.nearestPoints[i].x, bestPoints.nearestPoints[i].y, bestPoints.nearestPoints[i].z);
			glVertex3d(bestPoints.referencePoints[i].x, bestPoints.referencePoints[i].y, bestPoints.referencePoints[i].z);
			glEnd();
			
			glPushMatrix();
			MVector center = (bestPoints.nearestPoints[i] + bestPoints.referencePoints[i]) * 0.5f;
			glTranslatef((float)center.x, (float)center.y, (float)center.z);
			GLLookAt(bestPoints.nearestPoints[i], bestPoints.referencePoints[i]);
			float newRadius = 1.0f;
			if (ScreenSpaceDiscs(thisMObject())){
				newRadius = Min((float)(center - cameraPosition).length() * 0.01f, 1.0f);
			}
			if (CullSpaceDiscs(thisMObject())){
				glEnable(GL_CULL_FACE);
			}
			
			GLDrawDisc(Segments(thisMObject()), radius * newRadius);

			glPopMatrix();
		}
		
	}
	
	if (DrawInFront(thisMObject())){
		glEnable(GL_DEPTH_TEST);
	}
	/* Restore world space*/
	glPopMatrix();
	glPopAttrib();
}

bool SkinningVisualizer::isTransparent() const
{
	return Transparency(thisMObject()) > 0.0f;
}

#if MAYAVERSION > 2014
using namespace MHWRender;
MPxDrawOverride* SkinningVisualizerViewport2::sCreator(const MObject& obj)
{
	return new SkinningVisualizerViewport2(obj);
}

class SkinningVisualizerViewport2Data : public MUserData
{
public:
	bool drawIt;
	bool drawInFront;
	std::vector<Line> jointPositions;
	Float3 clickedColor;
	Float3 controlColor;
	float alpha;
	int selectedBone;
	BestNPoints bestPoints;
	float radius;
	Float3 discColor;
	int segments;
	bool screenSpaceDiscs;
	bool cullSpaceDiscs;

	SkinningVisualizerViewport2Data() : MUserData(true) {}
};

MUserData* SkinningVisualizerViewport2::prepareForDraw(const MDagPath& objPath, const MDagPath& cameraPath, const MHWRender::MFrameContext& frameContext, MUserData* oldData)
{
	SkinningVisualizerViewport2Data* data = dynamic_cast<SkinningVisualizerViewport2Data*>(oldData);
	
	if(!data)
		data = new SkinningVisualizerViewport2Data;
	
	MObject node = objPath.node();
	data->drawIt = DrawIt(node);
	data->drawInFront = DrawInFront(node);
	JointWorldPositions(node, data->jointPositions);
	data->clickedColor = ClickedColor(node);
	data->controlColor = ControlColor(node);
	data->discColor = DiscColor(node);
	data->alpha = Transparency(node);
	data->radius = Radius(node);
	data->segments = Segments(node);
	data->screenSpaceDiscs= ScreenSpaceDiscs(node);
	data->cullSpaceDiscs= CullSpaceDiscs(node);
	data->selectedBone = SelectedBoneIndex(node);
	data->bestPoints = BestNPoints(Min(AmountConnected(node), (int)(data->jointPositions.size() * 2 - 2)));
	NearestPointsToSelectedBone(data->selectedBone, data->jointPositions, data->bestPoints);

	return data;
}

void SkinningVisualizerViewport2::addUIDrawables(const MDagPath& objPath, MHWRender::MUIDrawManager& drawManager, const MHWRender::MFrameContext& frameContext, const MUserData* inData)
{
	const SkinningVisualizerViewport2Data* data = dynamic_cast<const SkinningVisualizerViewport2Data*>(inData);
	
	if(!data->drawIt)
		return;

	drawManager.beginDrawable();
#endif
#if MAYAVERSION > 2015
	drawManager.beginDrawInXray(); // draw in front
#endif
#if MAYAVERSION > 2014
	MVector cameraPosition = WorldSpaceCameraPos();
	
	// Draw bones and helper discs
	drawManager.setLineWidth(2.0f);
	for(size_t i = 0 ; i < data->jointPositions.size(); ++i)
	{
		const Line& line = data->jointPositions[i];
		if(i == data->selectedBone)
		{
			drawManager.setColor(MColor(data->clickedColor.x, data->clickedColor.y, data->clickedColor.z, data->alpha));
		}
		else
		{
			drawManager.setColor(MColor(data->controlColor.x, data->controlColor.y, data->controlColor.z, data->alpha));
		}

		// Draw disc for start, facing the camera
		float radius = Min((float)(line.start - cameraPosition).length() * 0.01f, 1.0f);
		drawManager.circle(MPoint(line.start.x, line.start.y, line.start.z), (line.start - cameraPosition).normal(), radius, true);
		
		// Draw disc for end, facing the camera
		radius = Min((float)(line.end - cameraPosition).length() * 0.01f, 1.0f);
		drawManager.circle(MPoint(line.end.x, line.end.y, line.end.z), (line.end - cameraPosition).normal(), radius, true);
		
		// Draw dashed line
		drawManager.setLineStyle(MHWRender::MUIDrawManager::kDashed);
		drawManager.line(MPoint(line.start.x, line.start.y, line.start.z), MPoint(line.end.x, line.end.y, line.end.z));
		drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
	}
#endif
#if MAYAVERSION > 2015
	drawManager.endDrawInXray(); // end draw in front
#endif
#if MAYAVERSION > 2014	
	// Draw n-nearest planes of selected bone
	if(data->selectedBone != -1)
	{
		BestNPoints bestPoints = data->bestPoints;
		
		for(unsigned int i = 0 ; i < bestPoints.nearestPoints.length(); ++i)
		{
			if(bestPoints.bestDistances[i] == INFINITY)
				continue;
#endif
#if MAYAVERSION > 2015
	if(data->drawInFront)
		drawManager.beginDrawInXray(); // draw in front
#endif
#if MAYAVERSION > 2014	
			drawManager.setColor(MColor(data->discColor.x, data->discColor.y, data->discColor.z, data->alpha));
			drawManager.line(MPoint(bestPoints.nearestPoints[i].x, bestPoints.nearestPoints[i].y, bestPoints.nearestPoints[i].z),
				MPoint(bestPoints.referencePoints[i].x, bestPoints.referencePoints[i].y, bestPoints.referencePoints[i].z));
			
			MVector center = (bestPoints.nearestPoints[i] + bestPoints.referencePoints[i]) * 0.5f;
			float newRadius = 1.0f;
			if (data->screenSpaceDiscs){
				newRadius = Min((float)(center - cameraPosition).length() * 0.01f, 1.0f);
			}
			if (!data->cullSpaceDiscs){
				// if culling is off draw 2 sides
				drawManager.circle(MPoint(center.x, center.y, center.z), (bestPoints.nearestPoints[i] - bestPoints.referencePoints[i]).normal()*-1, data->radius * newRadius, true);
			}
			drawManager.circle(MPoint(center.x, center.y, center.z), (bestPoints.nearestPoints[i] - bestPoints.referencePoints[i]).normal(), data->radius * newRadius, true);
#endif
#if MAYAVERSION > 2015
	if(data->drawInFront)
		drawManager.endDrawInXray(); // draw in front
#endif
#if MAYAVERSION > 2014	
		}
	}

	drawManager.endDrawable();

}
#endif
