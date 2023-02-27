#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <cmath>

#include "Scene.h"
#include "Camera.h"
#include "Color.h"
#include "Mesh.h"
#include "Rotation.h"
#include "Scaling.h"
#include "Translation.h"
#include "Triangle.h"
#include "Vec3.h"
#include "tinyxml2.h"
#include "Helpers.h"
#include "Matrix4.h"

using namespace tinyxml2;
using namespace std;

/*
	Transformations, clipping, culling, rasterization are done here.
	You may define helper functions.
*/

/*			HELPERS 		*/

Matrix4 Scene::getModelingMatrix(Mesh* mesh){
	int numberOfTransformations = mesh->numberOfTransformations;
	Matrix4 matrices[numberOfTransformations];
	for(int j=0;j<numberOfTransformations;j++){
		
		char type = mesh->transformationTypes[j];
		int id = mesh->transformationIds[j];
		// get transformation matrix
		switch (type){
			case 't':
				matrices[j] = getTranslationMatrix(translations[id-1]->tx,translations[id-1]->ty,translations[id-1]->tz);
				break;
			case 'r':
				matrices[j] = getRotationMatrix(rotations[id-1]->angle,rotations[id-1]->ux,rotations[id-1]->uy,rotations[id-1]->uz);
				break;
			case 's':
				matrices[j] = getScalingMatrix(scalings[id-1]->sx,scalings[id-1]->sy,scalings[id-1]->sz);
				break;
			default:
				matrices[j] = getIdentityMatrix();
				break;
		}
	}

	if(numberOfTransformations == 0)
		return getIdentityMatrix();

	//modelingMatrix = multiplyMatrices(matrices,numberOfTransformations);
	// multiply matrices in reverse order
	Matrix4 modelingMatrix = matrices[numberOfTransformations-1];

	for(int m = numberOfTransformations-2;m>=0;m--)
		modelingMatrix = multiplyMatrixWithMatrix(modelingMatrix,matrices[m]);

	return modelingMatrix;

} 

Matrix4 Scene::getCameraMatrix(Camera *camera){
	Matrix4 cameraMatrix;
	Vec3 eye = camera->pos;
	Vec3 u = camera->u;
	Vec3 v = camera->v;
	Vec3 w = camera->w;

	// Translate eye to the world origin 0,0,0 
	Matrix4 T = getTranslationMatrix(-eye.x,-eye.y,-eye.z);

	// Align camera's uvw to xyz
	Matrix4 A = getAligningMatrix(u,v,w);

	Matrix4 result = multiplyMatrixWithMatrix(A,T);

	return result;

}

Matrix4 Scene::getProjectionMatrix(Camera *camera){
	Matrix4 matrix;

	/* Camera Information */
	double t = camera->top;
	double b = camera->bottom;
	double l = camera->left;
	double r = camera->right;
	double f = camera->far;
	double n = camera->near;

	if(camera->projectionType){ // perspective projection, from slide 26 in viewing transformations
		matrix.setValue(0, 0, (2*n)/(r - l));
		matrix.setValue(0, 2, (r + l)/(r - l));

		matrix.setValue(1, 1, (2*n)/(t - b));
		matrix.setValue(1, 2, (t + b)/(t - b));

		matrix.setValue(2, 2, -(f + n)/(f - n));
		matrix.setValue(2, 3, -(2*f*n)/(f - n));

		matrix.setValue(3, 2, -1);
	}
	else { // orthogonal projection, from slide 14 in viewing transformations

		// diagonal entries
		matrix.setValue(0,0,2/(r - l));
		matrix.setValue(1,1,2/(t - b));
		matrix.setValue(2,2,-2/(f - n));
		matrix.setValue(3,3,1);

		// last column entries
		matrix.setValue(0,3,-(r + l)/(r - l));
		matrix.setValue(1,3,-(t + b)/(t - b));
		matrix.setValue(2,3,-(f + n)/(f - n));
	}

	return matrix;
}

Matrix4 Scene::getViewportMatrix(Camera *camera){
	Matrix4 matrix;

	/* Camera Information */
	int nx = camera->horRes;
	int ny = camera->verRes;

	matrix = createViewportMatrix(nx,ny);

	return matrix;
}

void Scene::drawPoint(int x, int y, Color color, Camera * cam){
	if(x < 0) x = 0;
	if(y < 0) y = 0;
	if(x >= cam->horRes) x = cam->horRes-1;
	if(y >= cam->verRes) y = cam->verRes-1;

	image[x][y] = color;
}

void Scene::drawTriangle(Vec4 p1, Vec4 p2, Vec4 p3, Color c1, Color c2, Color c3, Camera * cam){
	//solid rasterization
	double x1 = p1.x;
	double y1 = p1.y;
	double x2 = p2.x;
	double y2 = p2.y;
	double x3 = p3.x;
	double y3 = p3.y;
	// find min y and max y
	double minY = y1;
	double maxY = y1;
	if(y2 < minY){
		minY = y2;
	}
	if(y3 < minY){
		minY = y3;
	}
	if(y2 > maxY){
		maxY = y2;
	}
	if(y3 > maxY){
		maxY = y3;
	}
	// find min x and max x
	double minX = x1;
	double maxX = x1;
	if(x2 < minX){
		minX = x2;
	}
	if(x3 < minX){
		minX = x3;
	}
	if(x2 > maxX){
		maxX = x2;
	}
	if(x3 > maxX){
		maxX = x3;
	}
	// for each y in the range ymin to ymax
	for(int y = minY; y <= maxY; y++){
		// for each x in the range xmin to xmax
		for(int x = minX; x <= maxX; x++){
			// compute barycentric coordinates
			double alpha = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3));
			double beta = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3));
			double gamma = 1 - alpha - beta;
			// if alpha, beta, and gamma are all positive
			if(alpha >= 0 && beta >= 0 && gamma >= 0){
				Color c = c1*alpha + c2*beta + c3*gamma;
				drawPoint(x,y,c, cam);
			}
		}
	}
}

void Scene::drawLine(Vec4 p1, Vec4 p2, Color c1, Color c2, Camera * cam){
	int x1 = p1.x;
	int y1 = p1.y;
	int x2 = p2.x;
	int y2 = p2.y;

	int dx = x2 - x1;
	int dy = y2 - y1;

	int steps = abs(dx) > abs(dy) ? abs(dx) : abs(dy);
	Color dc = (c2 - c1)/(double) steps;
	double xIncrement = dx / (double) steps;
	double yIncrement = dy / (double) steps;

	double x = x1;
	double y = y1;

	Color c = c1;
	for(int i = 0; i <= steps; i++){
		drawPoint(x,y,c, cam);
		x += xIncrement;
		y += yIncrement;
		c = c + dc;
	}
}

// returns true if the triangle is visible
bool Scene::doBackFaceCulling(Vec4 v0, Vec4 v1, Vec4 v2, Camera * camera){
	double normal_v = calculateNormalOfTriangle(v0, v1, v2, camera);

	if(normal_v > 0)
		return false;
	return true;
}


double Scene::calculateNormalOfTriangle(Vec4 vec0, Vec4 vec1, Vec4 vec2, Camera * cam){
	Vec3 v0(vec0.x, vec0.y, vec0.z, vec0.colorId);
	Vec3 v1(vec1.x, vec1.y, vec1.z, vec1.colorId);
	Vec3 v2(vec2.x, vec2.y, vec2.z, vec2.colorId);

	Vec3 v01 = subtractVec3(v0, v1);
	Vec3 v02 = subtractVec3(v0, v2);

	Vec3 normal = normalizeVec3(crossProductVec3(v01, v02));

	Vec3 v = inverseVec3(v0);

	return dotProductVec3(normal, v);
}


bool Scene::doClippingForOneLine(Vec4 & v1, Vec4 & v2, Color & c1, Color & c2){
	int xmin = -1;
	int ymin = -1;
	int zmin = -1;
	int xmax = 1;
	int ymax = 1;
	int zmax = 1;

	double dx = v2.x - v1.x;
	double dy = v2.y - v1.y;
	double dz = v2.z - v1.z;
	Color dc = c2 - c1;

	double tE = 0;
	double tL = 1;
	bool visible = false;

	if (isVisible(dx, xmin - v1.x, tE, tL)  && 
		isVisible(-dx, v1.x - xmax, tE, tL) && 
		isVisible(dy, ymin - v1.y, tE, tL)  &&
		isVisible(-dy, v1.y - ymax, tE, tL) &&
		isVisible(dz, zmin - v1.z, tE, tL)  &&
		isVisible(-dz, v1.z - zmax, tE, tL) ){
		
		visible = true;

		if(tL < 1){
			v2.x = v1.x + tL * dx;
			v2.y = v1.y + tL * dy;
			v2.z = v1.z + tL * dz;
			c2 = c1 + dc * tL;
		}

		if(tE > 0){
			v1.x += tE * dx;
			v1.y += tE * dy;
			v1.z += tE * dz;
			c1 = c1 + dc * tE;
		}
	}

	return visible;

}


// Makes perspective divide for a point
void Scene::perspectiveDivideForPoint(Vec4 & v){
	v.x = v.x / v.t;
	v.y = v.y / v.t;
	v.z = v.z / v.t;
	v.t = 1.0;
}

// Wireframe mode perspective division
void Scene::perspectiveDivision(Vec4 & v1_line1, Vec4 & v2_line1, Vec4 & v2_line2, Vec4 & v3_line2, Vec4 & v3_line3, Vec4 & v1_line3){
	perspectiveDivideForPoint(v1_line1);
	perspectiveDivideForPoint(v2_line1);
	perspectiveDivideForPoint(v2_line2);
	perspectiveDivideForPoint(v3_line2);
	perspectiveDivideForPoint(v3_line3);
	perspectiveDivideForPoint(v1_line3);
}

// Solid mode perspective division
void Scene::perspectiveDivision(Vec4 & v1, Vec4 & v2, Vec4 & v3){
	perspectiveDivideForPoint(v1);
	perspectiveDivideForPoint(v2);
	perspectiveDivideForPoint(v3);
}

void Scene::viewportTransformationForPoint(Vec4 & v, const Matrix4 & viewportMatrix){
	v = multiplyMatrixWithVec4(viewportMatrix, v);
}

// Solid mode viewport transformation
void Scene::viewportTransformation(Vec4 & v1_line1, Vec4 & v2_line1, Vec4 & v2_line2, Vec4 & v3_line2, Vec4 & v3_line3, Vec4 & v1_line3, const Matrix4 & viewportMatrix){
	viewportTransformationForPoint(v1_line1, viewportMatrix);
	viewportTransformationForPoint(v2_line1, viewportMatrix);
	viewportTransformationForPoint(v2_line2, viewportMatrix);
	viewportTransformationForPoint(v3_line2, viewportMatrix);
	viewportTransformationForPoint(v3_line3, viewportMatrix);
	viewportTransformationForPoint(v1_line3, viewportMatrix);
}

// Wireframe mode viewport transformation
void Scene::viewportTransformation(Vec4 & v1, Vec4 & v2, Vec4 & v3, const Matrix4 & viewortMatrix){
	viewportTransformationForPoint(v1, viewortMatrix);
	viewportTransformationForPoint(v2, viewortMatrix);
	viewportTransformationForPoint(v3, viewortMatrix);
}

bool Scene::isVisible(const double & den ,const double & num , double & tE , double & tL){
	double t;

	// potentially entering
	if(den > 0){
		t = num / den;
		if(t > tL){
			return false;
		}
		else if(t > tE){
			tE = t;
		}
	}

	// potentially leaving
	else if(den < 0){
		t = num / den;
		if(t < tE){
			return false;
		}
		else if(t < tL){
			tL = t;
		}
	}

	// line parallel to the edge
	else if(num > 0){
		return false;
	}
	return true;
}

void Scene::forwardRenderingPipeline(Camera *camera) {
	/* Scene variables */
	int meshNumber = meshes.size();

	/* Viewing Transformations */

	// Camera Transformation Matrix
	Matrix4 cameraMatrix = getCameraMatrix(camera);

	// Projection Transformation Matrix
	Matrix4 projectionMatrix = getProjectionMatrix(camera);

	// Viewport Transformation
	Matrix4 viewingMatrix = getViewportMatrix(camera);

	
	for(int i=0;i<meshNumber;i++){
		Mesh * mesh = meshes[i];

		/* Modeling Transformations */
		Matrix4 modelingMatrix = getModelingMatrix(mesh);
		Matrix4 finalMatrix;
		// Multiply all matrices, M_projection * M_camera * M_modeling
		finalMatrix = multiplyMatrixWithMatrix(projectionMatrix,cameraMatrix);
		finalMatrix = multiplyMatrixWithMatrix(finalMatrix,modelingMatrix);
		
		// Apply transformations to all points in the mesh
		vector<Vec4> points;
		for(int i=0;i<vertices.size();i++){
			Vec4 point(vertices[i]->x,vertices[i]->y,vertices[i]->z,1,vertices[i]->colorId);
			point = multiplyMatrixWithVec4(finalMatrix,point);
			points.push_back(point);
		}

		vector<Color> colors;
		for(int j = 0; j < colorsOfVertices.size(); j++){
			Color color(colorsOfVertices[j]->r,colorsOfVertices[j]->g,colorsOfVertices[j]->b);
			colors.push_back(color);
		}

		int triangleNumber = mesh->triangles.size();

		// For every triangle in the mesh
		for(int j = 0; j < triangleNumber; j++){
			// get the indexes of the points of the triangle
			int v1_index = mesh->triangles[j].getFirstVertexId();
			int v2_index = mesh->triangles[j].getSecondVertexId();
			int v3_index = mesh->triangles[j].getThirdVertexId();

			// get the points of the triangle
			Vec4 v1 = points[v1_index - 1]; 
			Vec4 v2 = points[v2_index - 1];
			Vec4 v3 = points[v3_index - 1];

			// Do culling before clipping since we don't need to draw invisible triangles or lines
			// If the triangle is backfacing and culling is enabled then continue to the next triangle
			bool cullingCondition = !doBackFaceCulling(v1,v2,v3,camera) && cullingEnabled;
			if(cullingCondition){
				continue;
			}


			// If wireframe mode is on
			if(mesh->type == 0){
				// Create colors and vertices for each line
				// Since we give them clipping as pass by reference arguments
				Color c1_line1 = colors[v1_index - 1];
				Color c2_line1 = colors[v2_index - 1];

				Color c2_line2 = colors[v2_index - 1];
				Color c3_line2 = colors[v3_index - 1];

				Color c3_line3 = colors[v3_index - 1];
				Color c1_line3 = colors[v1_index - 1];

				Vec4 v1_line1 = v1;
				Vec4 v2_line1 = v2;

				Vec4 v2_line2 = v2;
				Vec4 v3_line2 = v3;

				Vec4 v3_line3 = v3;
				Vec4 v1_line3 = v1;

				// Do perspective division
				// If perspective projection
				if(camera->projectionType){
					perspectiveDivision(v1_line1,v2_line1,v2_line2,v3_line2,v3_line3,v1_line3);
				}
				// do clipping for every line

				bool line_1_visible = doClippingForOneLine(v1_line1,v2_line1,c1_line1,c2_line1);
				bool line_2_visible = doClippingForOneLine(v2_line2,v3_line2,c2_line2,c3_line2);
				bool line_3_visible = doClippingForOneLine(v3_line3,v1_line3,c3_line3,c1_line3);


				// Do viewport transformation 
				viewportTransformation(v1_line1,v2_line1,v2_line2,v3_line2,v3_line3,v1_line3,viewingMatrix);

				// Draw lines
				// Rasterization
				if(line_1_visible){
					drawLine(v1_line1,v2_line1,c1_line1,c2_line1,camera);
				}
				if(line_2_visible){
					drawLine(v2_line2,v3_line2,c2_line2,c3_line2,camera);
				}
				if(line_3_visible){
					drawLine(v3_line3,v1_line3,c3_line3,c1_line3,camera);
				}
			}

			// Else solid mode is on
			else {
				// There is no clipping
				Color c1 = colors[v1_index - 1];
				Color c2 = colors[v2_index - 1];
				Color c3 = colors[v3_index - 1];

				// Do perspective division for every point
				// If perspective projection
				if(camera->projectionType){
					perspectiveDivision(v1,v2,v3);
				}

				// Do viewport transformation for every point
				viewportTransformation(v1,v2,v3,viewingMatrix);

				// Draw triangle
				// Rasterization
				drawTriangle(v1,v2,v3,c1,c2,c3, camera);
			}
		}
	}
}

/*
	Parses XML file
*/
Scene::Scene(const char *xmlPath)
{
	const char *str;
	XMLDocument xmlDoc;
	XMLElement *pElement;

	xmlDoc.LoadFile(xmlPath);

	XMLNode *pRoot = xmlDoc.FirstChild();

	// read background color
	pElement = pRoot->FirstChildElement("BackgroundColor");
	str = pElement->GetText();
	sscanf(str, "%lf %lf %lf", &backgroundColor.r, &backgroundColor.g, &backgroundColor.b);

	// read culling
	pElement = pRoot->FirstChildElement("Culling");
	if (pElement != NULL) {
		str = pElement->GetText();
		
		if (strcmp(str, "enabled") == 0) {
			cullingEnabled = true;
		}
		else {
			cullingEnabled = false;
		}
	}

	// read cameras
	pElement = pRoot->FirstChildElement("Cameras");
	XMLElement *pCamera = pElement->FirstChildElement("Camera");
	XMLElement *camElement;
	while (pCamera != NULL)
	{
		Camera *cam = new Camera();

		pCamera->QueryIntAttribute("id", &cam->cameraId);

		// read projection type
		str = pCamera->Attribute("type");

		if (strcmp(str, "orthographic") == 0) {
			cam->projectionType = 0;
		}
		else {
			cam->projectionType = 1;
		}

		camElement = pCamera->FirstChildElement("Position");
		str = camElement->GetText();
		sscanf(str, "%lf %lf %lf", &cam->pos.x, &cam->pos.y, &cam->pos.z);

		camElement = pCamera->FirstChildElement("Gaze");
		str = camElement->GetText();
		sscanf(str, "%lf %lf %lf", &cam->gaze.x, &cam->gaze.y, &cam->gaze.z);

		camElement = pCamera->FirstChildElement("Up");
		str = camElement->GetText();
		sscanf(str, "%lf %lf %lf", &cam->v.x, &cam->v.y, &cam->v.z);

		cam->gaze = normalizeVec3(cam->gaze);
		cam->u = crossProductVec3(cam->gaze, cam->v);
		cam->u = normalizeVec3(cam->u);

		cam->w = inverseVec3(cam->gaze);
		cam->v = crossProductVec3(cam->u, cam->gaze);
		cam->v = normalizeVec3(cam->v);

		camElement = pCamera->FirstChildElement("ImagePlane");
		str = camElement->GetText();
		sscanf(str, "%lf %lf %lf %lf %lf %lf %d %d",
			   &cam->left, &cam->right, &cam->bottom, &cam->top,
			   &cam->near, &cam->far, &cam->horRes, &cam->verRes);

		camElement = pCamera->FirstChildElement("OutputName");
		str = camElement->GetText();
		cam->outputFileName = string(str);

		cameras.push_back(cam);

		pCamera = pCamera->NextSiblingElement("Camera");
	}

	// read vertices
	pElement = pRoot->FirstChildElement("Vertices");
	XMLElement *pVertex = pElement->FirstChildElement("Vertex");
	int vertexId = 1;

	while (pVertex != NULL)
	{
		Vec3 *vertex = new Vec3();
		Color *color = new Color();

		vertex->colorId = vertexId;

		str = pVertex->Attribute("position");
		sscanf(str, "%lf %lf %lf", &vertex->x, &vertex->y, &vertex->z);

		str = pVertex->Attribute("color");
		sscanf(str, "%lf %lf %lf", &color->r, &color->g, &color->b);

		vertices.push_back(vertex);
		colorsOfVertices.push_back(color);

		pVertex = pVertex->NextSiblingElement("Vertex");

		vertexId++;
	}

	// read translations
	pElement = pRoot->FirstChildElement("Translations");
	XMLElement *pTranslation = pElement->FirstChildElement("Translation");
	while (pTranslation != NULL)
	{
		Translation *translation = new Translation();

		pTranslation->QueryIntAttribute("id", &translation->translationId);

		str = pTranslation->Attribute("value");
		sscanf(str, "%lf %lf %lf", &translation->tx, &translation->ty, &translation->tz);

		translations.push_back(translation);

		pTranslation = pTranslation->NextSiblingElement("Translation");
	}

	// read scalings
	pElement = pRoot->FirstChildElement("Scalings");
	XMLElement *pScaling = pElement->FirstChildElement("Scaling");
	while (pScaling != NULL)
	{
		Scaling *scaling = new Scaling();

		pScaling->QueryIntAttribute("id", &scaling->scalingId);
		str = pScaling->Attribute("value");
		sscanf(str, "%lf %lf %lf", &scaling->sx, &scaling->sy, &scaling->sz);

		scalings.push_back(scaling);

		pScaling = pScaling->NextSiblingElement("Scaling");
	}

	// read rotations
	pElement = pRoot->FirstChildElement("Rotations");
	XMLElement *pRotation = pElement->FirstChildElement("Rotation");
	while (pRotation != NULL)
	{
		Rotation *rotation = new Rotation();

		pRotation->QueryIntAttribute("id", &rotation->rotationId);
		str = pRotation->Attribute("value");
		sscanf(str, "%lf %lf %lf %lf", &rotation->angle, &rotation->ux, &rotation->uy, &rotation->uz);

		rotations.push_back(rotation);

		pRotation = pRotation->NextSiblingElement("Rotation");
	}

	// read meshes
	pElement = pRoot->FirstChildElement("Meshes");

	XMLElement *pMesh = pElement->FirstChildElement("Mesh");
	XMLElement *meshElement;
	while (pMesh != NULL)
	{
		Mesh *mesh = new Mesh();

		pMesh->QueryIntAttribute("id", &mesh->meshId);

		// read projection type
		str = pMesh->Attribute("type");

		if (strcmp(str, "wireframe") == 0) {
			mesh->type = 0;
		}
		else {
			mesh->type = 1;
		}

		// read mesh transformations
		XMLElement *pTransformations = pMesh->FirstChildElement("Transformations");
		XMLElement *pTransformation = pTransformations->FirstChildElement("Transformation");

		while (pTransformation != NULL)
		{
			char transformationType;
			int transformationId;

			str = pTransformation->GetText();
			sscanf(str, "%c %d", &transformationType, &transformationId);

			mesh->transformationTypes.push_back(transformationType);
			mesh->transformationIds.push_back(transformationId);

			pTransformation = pTransformation->NextSiblingElement("Transformation");
		}

		mesh->numberOfTransformations = mesh->transformationIds.size();

		// read mesh faces
		char *row;
		char *clone_str;
		int v1, v2, v3;
		XMLElement *pFaces = pMesh->FirstChildElement("Faces");
        str = pFaces->GetText();
		clone_str = strdup(str);

		row = strtok(clone_str, "\n");
		while (row != NULL)
		{
			int result = sscanf(row, "%d %d %d", &v1, &v2, &v3);
			
			if (result != EOF) {
				mesh->triangles.push_back(Triangle(v1, v2, v3));
			}
			row = strtok(NULL, "\n");
		}
		mesh->numberOfTriangles = mesh->triangles.size();
		meshes.push_back(mesh);

		pMesh = pMesh->NextSiblingElement("Mesh");
	}
}

/*
	Initializes image with background color
*/
void Scene::initializeImage(Camera *camera)
{
	if (this->image.empty())
	{
		for (int i = 0; i < camera->horRes; i++)
		{
			vector<Color> rowOfColors;

			for (int j = 0; j < camera->verRes; j++)
			{
				rowOfColors.push_back(this->backgroundColor);
			}

			this->image.push_back(rowOfColors);
		}
	}
	else
	{
		for (int i = 0; i < camera->horRes; i++)
		{
			for (int j = 0; j < camera->verRes; j++)
			{
				this->image[i][j].r = this->backgroundColor.r;
				this->image[i][j].g = this->backgroundColor.g;
				this->image[i][j].b = this->backgroundColor.b;
			}
		}
	}
}

/*
	If given value is less than 0, converts value to 0.
	If given value is more than 255, converts value to 255.
	Otherwise returns value itself.
*/
int Scene::makeBetweenZeroAnd255(double value)
{
	if (value >= 255.0)
		return 255;
	if (value <= 0.0)
		return 0;
	return (int)(value);
}

/*
	Writes contents of image (Color**) into a PPM file.
*/
void Scene::writeImageToPPMFile(Camera *camera)
{
	ofstream fout;

	fout.open(camera->outputFileName.c_str());

	fout << "P3" << endl;
	fout << "# " << camera->outputFileName << endl;
	fout << camera->horRes << " " << camera->verRes << endl;
	fout << "255" << endl;

	for (int j = camera->verRes - 1; j >= 0; j--)
	{
		for (int i = 0; i < camera->horRes; i++)
		{
			fout << makeBetweenZeroAnd255(this->image[i][j].r) << " "
				 << makeBetweenZeroAnd255(this->image[i][j].g) << " "
				 << makeBetweenZeroAnd255(this->image[i][j].b) << " ";
		}
		fout << endl;
	}
	fout.close();
}

/*
	Converts PPM image in given path to PNG file, by calling ImageMagick's 'convert' command.
	os_type == 1 		-> Ubuntu
	os_type == 2 		-> Windows
	os_type == other	-> No conversion
*/
void Scene::convertPPMToPNG(string ppmFileName, int osType=0)
{
	string command;

	// call command on Ubuntu
	if (osType == 1)
	{
		command = "convert " + ppmFileName + " " + ppmFileName + ".png";
		system(command.c_str());
	}

	// call command on Windows
	else if (osType == 2)
	{
		command = "magick convert " + ppmFileName + " " + ppmFileName + ".png";
		system(command.c_str());
	}

	// default action - don't do conversion
	else
	{
	}
}
