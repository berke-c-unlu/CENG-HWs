#include "Rotation.h"
#include <iostream>
#include <iomanip>
#define PI 3.14159265358979323846 

using namespace std;

Rotation::Rotation() {}

Rotation::Rotation(int rotationId, double angle, double x, double y, double z)
{
    this->rotationId = rotationId;
    this->angle = angle;
    this->ux = x;
    this->uy = y;
    this->uz = z;
}
/*
Matrix4 Rotation::calculateMatrix(){
    // Assumed to rotate around x axis
    // We need to arrange aliging first
    Matrix4 matrix;

    matrix.setValue(0,0,1); // top left

    matrix.setValue(1,1,cos(this->angle*PI/180));
    matrix.setValue(1,2,-sin(this->angle*PI/180));
    matrix.setValue(2,1,sin(this->angle*PI/180));
    matrix.setValue(2,2,cos(this->angle*PI/180));

    matrix.setValue(3,3,1); // bottom right

    return matrix;
}*/


ostream &operator<<(ostream &os, const Rotation &r)
{
    os << fixed << setprecision(3) << "Rotation " << r.rotationId << " => [angle=" << r.angle << ", " << r.ux << ", " << r.uy << ", " << r.uz << "]";

    return os;
}