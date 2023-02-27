#include <iostream>
#include <cmath>
#include "Helpers.h"
#include "Matrix4.h"
#include "Vec3.h"
#include "Vec4.h"
#define PI 3.14159265358979323846 


using namespace std;

/*
 * Calculate cross product of vec3 a, vec3 b and return resulting vec3.
 */
Vec3 crossProductVec3(Vec3 a, Vec3 b)
{
    Vec3 result;

    result.x = a.y * b.z - b.y * a.z;
    result.y = b.x * a.z - a.x * b.z;
    result.z = a.x * b.y - b.x * a.y;

    return result;
}

/*
 * Calculate dot product of vec3 a, vec3 b and return resulting value.
 */
double dotProductVec3(Vec3 a, Vec3 b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

/*
 * Find length (|v|) of vec3 v.
 */
double magnitudeOfVec3(Vec3 v)
{
    return sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

/*
 * Normalize the vec3 to make it unit vec3.
 */
Vec3 normalizeVec3(Vec3 v)
{
    Vec3 result;
    double d;

    d = magnitudeOfVec3(v);
    result.x = v.x / d;
    result.y = v.y / d;
    result.z = v.z / d;

    return result;
}

/*
 * Return -v (inverse of vec3 v)
 */
Vec3 inverseVec3(Vec3 v)
{
    Vec3 result;
    result.x = -v.x;
    result.y = -v.y;
    result.z = -v.z;

    return result;
}

/*
 * Add vec3 a to vec3 b and return resulting vec3 (a+b).
 */
Vec3 addVec3(Vec3 a, Vec3 b)
{
    Vec3 result;
    result.x = a.x + b.x;
    result.y = a.y + b.y;
    result.z = a.z + b.z;

    return result;
}

/*
 * Subtract vec3 b from vec3 a and return resulting vec3 (a-b).
 */
Vec3 subtractVec3(Vec3 a, Vec3 b)
{
    Vec3 result;
    result.x = a.x - b.x;
    result.y = a.y - b.y;
    result.z = a.z - b.z;

    return result;
}

/*
 * Multiply each element of vec3 with scalar.
 */
Vec3 multiplyVec3WithScalar(Vec3 v, double c)
{
    Vec3 result;
    result.x = v.x * c;
    result.y = v.y * c;
    result.z = v.z * c;

    return result;
}

/*
 * Prints elements in a vec3. Can be used for debugging purposes.
 */
void printVec3(Vec3 v)
{
    cout << "(" << v.x << "," << v.y << "," << v.z << ")" << endl;
}

/*
 * Check whether vec3 a and vec3 b are equal.
 * In case of equality, returns 1.
 * Otherwise, returns 0.
 */
int areEqualVec3(Vec3 a, Vec3 b)
{

    /* if x difference, y difference and z difference is smaller than threshold, then they are equal */
    if ((ABS((a.x - b.x)) < EPSILON) && (ABS((a.y - b.y)) < EPSILON) && (ABS((a.z - b.z)) < EPSILON))
    {
        return 1;
    }
    else
    {
        return 0;
    }
}

/*
 * Returns an identity matrix (values on the diagonal are 1, others are 0).
*/
Matrix4 getIdentityMatrix()
{
    Matrix4 result;

    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            if (i == j)
            {
                result.val[i][j] = 1.0;
            }
            else
            {
                result.val[i][j] = 0.0;
            }
        }
    }

    return result;
}

/*
 * Multiply matrices m1 (Matrix4) and m2 (Matrix4) and return the result matrix r (Matrix4).
 */
Matrix4 multiplyMatrixWithMatrix(Matrix4 m1, Matrix4 m2)
{
    Matrix4 result;
    double total;

    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            total = 0;
            for (int k = 0; k < 4; k++)
            {
                total += m1.val[i][k] * m2.val[k][j];
            }

            result.val[i][j] = total;
        }
    }

    return result;
}

/*
 * Multiply matrix m (Matrix4) with vector v (vec4) and store the result in vector r (vec4).
 */
Vec4 multiplyMatrixWithVec4(Matrix4 m, Vec4 v)
{
    double values[4];
    double total;

    for (int i = 0; i < 4; i++)
    {
        total = 0;
        for (int j = 0; j < 4; j++)
        {
            total += m.val[i][j] * v.getElementAt(j);
        }
        values[i] = total;
    }

    return Vec4(values[0], values[1], values[2], values[3], v.colorId);
}


/*
 * Multiply multiple matrices in reverse order
 */
Matrix4 multiplyMatrices(Matrix4 m[], int size){
	Matrix4 matrix = m[size-1];

	for(int i = size-2;i>=0;i--)
		matrix = multiplyMatrixWithMatrix(matrix,m[i]);
    
    return matrix;
}


/*
 * Returns translation matrix with given arguments
 */
Matrix4 getTranslationMatrix(double tx, double ty, double tz){
    Matrix4 matrix = getIdentityMatrix();

    matrix.setValue(0,3,tx);
    matrix.setValue(1,3,ty);
    matrix.setValue(2,3,tz);

    return matrix;
}

/*
 * Returns rotation matrix with given arguments
 */
Matrix4 getRotationMatrix(double angle, double ux, double uy, double uz){
    // Assumed to rotate around x axis
    Matrix4 result;

    Vec3 u(ux,uy,uz,-1);
    // Matrix for aligning arbitrary u axis to x axis
    Matrix4 M = getAligningMatrix(u);

    // Rotation matrix around x-axis
    Matrix4 R;

    R.setValue(0,0,1); // top left

    R.setValue(1,1,cos(angle*PI/180));
    R.setValue(1,2,-sin(angle*PI/180));
    R.setValue(2,1,sin(angle*PI/180));
    R.setValue(2,2,cos(angle*PI/180));

    R.setValue(3,3,1); // bottom right

    // Matrix for inverse of aligning
    Matrix4 M_inverse = getAligningMatrix(u,1);

    // result = M_inverse * R(angle) * M
    result = multiplyMatrixWithMatrix(M_inverse,R);
    result = multiplyMatrixWithMatrix(result,M);

    return result;
}

/*
 * Returns scaling matrix with given arguments
 */
Matrix4 getScalingMatrix(double sx, double sy, double sz){
    Matrix4 matrix;
    
    matrix.setValue(0,0,sx);
    matrix.setValue(1,1,sy);
    matrix.setValue(2,2,sz);
    matrix.setValue(3,3,1);
    
    return matrix;
}

/*
 * Returns aligning uvw to xyz matrix, given u
 * inverse = 0 by default
 */
Matrix4 getAligningMatrix(Vec3 u, int inverse){
    Matrix4 matrix;
    // create an orthonormal basis u v w:
    Vec3 v,w;
    u = normalizeVec3(u);
    // finding v vector, to find v: find smallest component of u and set it to zero and swap the other while negating one
    int index;
    double val = 2.;
    for(int i=0;i<3;i++){
        if(u.getElementAt(i) < val){
            val = u.getElementAt(i);
            index = i;
        }
    }
    switch (index)
    {
        case 0:
            v.x = 0;
            v.y = -u.z;
            v.z = u.y;
            break;
        case 1:
            v.x = -u.z;
            v.y = 0;
            v.z = u.x;
            break;
        case 2:
            v.x = -u.y;
            v.y = u.x;
            v.z = 0;
            break;
        default:
            break;
    }
    // finding w vector
    w = crossProductVec3(u,v);
    // normalization 
    v = normalizeVec3(v);
    w = normalizeVec3(w);

    if(!inverse){
        matrix.setValue(0,0,u.x);
        matrix.setValue(0,1,u.y);
        matrix.setValue(0,2,u.z);

        matrix.setValue(1,0,v.x);
        matrix.setValue(1,1,v.y);
        matrix.setValue(1,2,v.z);

        matrix.setValue(2,0,w.x);
        matrix.setValue(2,1,w.y);
        matrix.setValue(2,2,w.z);

        matrix.setValue(3,3,1);
    }
    else{
        matrix.setValue(0,0,u.x);
        matrix.setValue(1,0,u.y);
        matrix.setValue(2,0,u.z);

        matrix.setValue(0,1,v.x);
        matrix.setValue(1,1,v.y);
        matrix.setValue(2,1,v.z);

        matrix.setValue(0,2,w.x);
        matrix.setValue(1,2,w.y);
        matrix.setValue(2,2,w.z);

        matrix.setValue(3,3,1);
    }
    return matrix;
}

/*
 * Returns aligning uvw to xyz matrix, given uvw
 * inverse = 0 by default
 */
Matrix4 getAligningMatrix(Vec3 u, Vec3 v, Vec3 w, int inverse){
    Matrix4 matrix;
    if(!inverse){
        matrix.setValue(0,0,u.x);
        matrix.setValue(0,1,u.y);
        matrix.setValue(0,2,u.z);

        matrix.setValue(1,0,v.x);
        matrix.setValue(1,1,v.y);
        matrix.setValue(1,2,v.z);

        matrix.setValue(2,0,w.x);
        matrix.setValue(2,1,w.y);
        matrix.setValue(2,2,w.z);

        matrix.setValue(3,3,1);
    }
    else{
        matrix.setValue(0,0,u.x);
        matrix.setValue(1,0,u.y);
        matrix.setValue(2,0,u.z);

        matrix.setValue(0,0,v.x);
        matrix.setValue(1,0,v.y);
        matrix.setValue(2,0,v.z);

        matrix.setValue(0,0,w.x);
        matrix.setValue(1,0,w.y);
        matrix.setValue(2,0,w.z);

        matrix.setValue(3,3,1);
    }
    return matrix;
}

/*
 * Returns viewport matrix with given arguments
 */
Matrix4 createViewportMatrix(int nx, int ny){
    Matrix4 matrix;

    matrix.setValue(0,0,nx/2);
	matrix.setValue(0,3,((nx-1)/2));

	matrix.setValue(1,1,ny/2);
	matrix.setValue(1,3,((ny-1)/2));

	matrix.setValue(2,2,0.5);
	matrix.setValue(2,3,0.5);

    return matrix;
}
