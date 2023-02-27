#ifndef __MATRIX4_H__
#define __MATRIX4_H__

#include <iostream>

using namespace std;

class Matrix4
{
public:
    double val[4][4];

    Matrix4();
    Matrix4(double val[4][4]);
    Matrix4(const Matrix4 &other);
    void setValue(int i, int j, double value);
    friend ostream &operator<<(ostream &os, const Matrix4 &m);
    void operator=(const Matrix4 &other);
};

#endif