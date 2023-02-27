#ifndef __TRANSLATION_H__
#define __TRANSLATION_H__

#include <iostream>
#include "Matrix4.h"
#include "Helpers.h"

using namespace std;

class Translation
{
public:
    int translationId;
    double tx, ty, tz;

    Translation();
    Translation(int translationId, double tx, double ty, double tz);
    //Matrix4 calculateMatrix();
    friend ostream &operator<<(ostream &os, const Translation &t);
};

#endif