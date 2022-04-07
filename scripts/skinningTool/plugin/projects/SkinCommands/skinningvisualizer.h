#pragma once

#include <limits>

//#define INFINITY INT_MAX

#include <vector>
#include <maya/MPxLocatorNode.h>
#include <maya/MFloatMatrix.h>
#include <maya/MVectorArray.h>
#include <maya/MDoubleArray.h>
#include <maya/MPxDrawOverride.h>



struct Float3
{
	float x;
	float y;
	float z;
	
	Float3() ;
	Float3(float x, float y, float z);
};



struct Line
{
	Line(MVector start, MVector end);
	MVector start;
	MVector end;
};



struct BestNPoints
{
	unsigned int largestBestIdx ;
	MVectorArray nearestPoints;
	MVectorArray referencePoints;
	MDoubleArray bestDistances;
	
	BestNPoints();
	BestNPoints(int pointsToFind);
	void Measure(const MVector& reference, const MVector& newPoint);
};



class SkinningVisualizer : public MPxLocatorNode
{
public:
	static void* sCreator(){return new SkinningVisualizer;}
	static MStatus sInitialize();

	virtual void draw(M3dView& ioView, const MDagPath& inPath, M3dView::DisplayStyle inStyle, M3dView::DisplayStatus inStatus) override;
	virtual bool isTransparent() const override;

	static MObject sDrawIt;
	static MObject sDrawInFront;
	static MObject sTransparency;
	static MObject sRadius;
	static MObject sSegments;
	static MObject sControlColor;
	static MObject sClickedColor;
	static MObject sDiscColor;
	static MObject sAmountConnected;
	static MObject sScreenSpaceDiscs;
	static MObject sCullSpaceDiscs;
	static MObject sPairs;
	static MObject sMatStart;
	static MObject sMatEnd;
};


#if MAYAVERSION > 2014
class SkinningVisualizerViewport2 : public MHWRender::MPxDrawOverride
{
public:
	static MHWRender::MPxDrawOverride* sCreator(const MObject& obj);

	virtual MHWRender::DrawAPI supportedDrawAPIs() const override { return MHWRender::kAllDevices; }
	virtual bool hasUIDrawables() const override { return true; }

	virtual MBoundingBox boundingBox(
		const MDagPath& objPath,
		const MDagPath& cameraPath) const override{return MBoundingBox();}

	virtual MUserData* prepareForDraw(const MDagPath& objPath, const MDagPath& cameraPath, const MHWRender::MFrameContext& frameContext, MUserData* oldData) override;
	virtual void addUIDrawables(const MDagPath& objPath, MHWRender::MUIDrawManager& drawManager, const MHWRender::MFrameContext& frameContext, const MUserData* data) override;

private:
    SkinningVisualizerViewport2(const MObject& obj) : MPxDrawOverride(obj, NULL) {}
    virtual ~SkinningVisualizerViewport2() {}
};
#endif
