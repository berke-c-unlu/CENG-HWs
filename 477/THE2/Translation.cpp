#include "Translation.h"
#include <iostream>
#include <iomanip>


using namespace std;

Translation::Translation()
{
    this->translationId = -1;
    this->tx = 0.0;
    this->ty = 0.0;
    this->tz = 0.0;

    // Calculate translation matrix


}

Translation::Translation(int translationId, double tx, double ty, double tz)
{
    this->translationId = translationId;
    this->tx = tx;
    this->ty = ty;
    this->tz = tz;
}
/*
Matrix4 Translation::calculateMatrix(){
    Matrix4 matrix = getIdentityMatrix();

    matrix.setValue(0,3,this->tx);
    matrix.setValue(1,3,this->ty);
    matrix.setValue(2,3,this->tz);

    return matrix;
}*/
ostream &operator<<(ostream &os, const Translation &t)
{
    os << fixed << setprecision(3) << "Translation " << t.translationId << " => [" << t.tx << ", " << t.ty << ", " << t.tz << "]";

    return os;
}