#ifndef _SCENE_H_
#define _SCENE_H_

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

#include "Camera.h"
#include "Color.h"
#include "Mesh.h"
#include "Rotation.h"
#include "Scaling.h"
#include "Translation.h"
#include "Triangle.h"
#include "Vec3.h"
#include "Vec4.h"
#include "Matrix4.h"

using namespace std;

class Scene
{
public:
	Color backgroundColor;
	bool cullingEnabled;

	vector< vector<Color> > image;
	vector< Camera* > cameras;
	vector< Vec3* > vertices;
	vector< Color* > colorsOfVertices;
	vector< Scaling* > scalings;
	vector< Rotation* > rotations;
	vector< Translation* > translations;
	vector< Mesh* > meshes;

	Scene(const char *xmlPath);

	void initializeImage(Camera* camera);
	void forwardRenderingPipeline(Camera* camera);
	int makeBetweenZeroAnd255(double value);
	void writeImageToPPMFile(Camera* camera);
	void convertPPMToPNG(string ppmFileName, int osType);


// helper functions
private:
	Matrix4 getModelingMatrix(Mesh *mesh);
	Matrix4 getCameraMatrix(Camera *camera);
	Matrix4 getViewportMatrix(Camera *camera);
	Matrix4 getProjectionMatrix(Camera *camera);

	double calculateNormalOfTriangle(Vec4 v0, Vec4 v1, Vec4 v2, Camera * camera);
	bool doBackFaceCulling(Vec4 v0, Vec4 v1, Vec4 v2, Camera * camera);

	bool doClippingForOneLine(Vec4 & v1, Vec4 & v2, Color & c1, Color & c2);
	bool isVisible(const double & den ,const double & num , double & tE , double & tL);
	
	void drawPoint(int x,int y , Color color, Camera * cam);
	void drawTriangle(Vec4 p1, Vec4 p2, Vec4 p3, Color c1, Color c2, Color c3, Camera * cam);
	void drawLine(Vec4 p1, Vec4 p2, Color c1, Color c2, Camera * cam);

	void perspectiveDivideForPoint(Vec4 & v);
	void perspectiveDivision(Vec4 & v1, Vec4 & v2, Vec4 & v3);
	void perspectiveDivision(Vec4 & v1_line1, Vec4 & v2_line1, Vec4 & v2_line2, Vec4 & v3_line2, Vec4 & v3_line3, Vec4 & v1_line3);
	
	void viewportTransformationForPoint(Vec4 & v, const Matrix4 & viewportMatrix);
	void viewportTransformation(Vec4 & v1, Vec4 & v2, Vec4 & v3, const Matrix4 & viewportMatrix);
	void viewportTransformation(Vec4 & v1_line1, Vec4 & v2_line1, Vec4 & v2_line2, Vec4 & v3_line2, Vec4 & v3_line3, Vec4 & v1_line3, const Matrix4 & viewportMatrix);

};

#endif
