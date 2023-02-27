#include <cstdio>
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <string>
#include <map>
#include <fstream>
#include <iostream>
#include <sstream>
#include <vector>
#include <GL/glew.h>   // The GL Header File
#include <GL/gl.h>   // The GL Header File
#include <GLFW/glfw3.h> // The GLFW header
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

class Item {
    public:
        int posX;
        int posY;
        int targetY;
        float angle=0;
        float scale;
        float down=0;
        glm::vec3 color;
        float objHeight, objWidth;
        bool sliding = false;
        bool clicked = false;
        bool expanding = false;
        bool visible=true;
        glm::mat4 modelingMat;




        Item();
        Item(int x, int y, float a,float s, glm::vec3 c);
        void incrAngle();
        void setPos(int x, int y);
        bool isClicked();
        bool isSliding();
        bool isExpanding();

        glm::mat4 getModelingMatrix(int Width, int Height);
};