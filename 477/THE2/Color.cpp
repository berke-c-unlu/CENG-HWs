#include "Color.h"
#include <iostream>
#include <iomanip>

using namespace std;

Color::Color() {}

Color::Color(double r, double g, double b)
{
    this->r = r;
    this->g = g;
    this->b = b;
}

Color::Color(const Color &other)
{
    this->r = other.r;
    this->g = other.g;
    this->b = other.b;
}

ostream& operator<<(ostream& os, const Color& c)
{
    os << fixed << setprecision(0) << "rgb(" << c.r << ", " << c.g << ", " << c.b << ")";
    return os;
}

Color Color::operator-(const Color& other)
{
    Color result;
    result.r = this->r - other.r;
    result.g = this->g - other.g;
    result.b = this->b - other.b;
    return result;
}

Color Color::operator/(const int& divide)
{
    Color result;
    result.r = this->r / divide;
    result.g = this->g / divide;
    result.b = this->b / divide;
    return result;
}

Color Color::operator+(const Color& other)
{
    Color result;
    result.r = this->r + other.r;
    result.g = this->g + other.g;
    result.b = this->b + other.b;
    return result;
}

Color Color::operator*(const double& multiply)
{
    Color result;
    result.r = this->r * multiply;
    result.g = this->g * multiply;
    result.b = this->b * multiply;
    return result;
}
