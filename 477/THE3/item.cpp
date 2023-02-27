#include "item.h"

using namespace std;

Item::Item(){

}


Item::Item(int x, int y, float a,float s, glm::vec3 c) {
    posX = x;
    posY = y;
    targetY = y;
    angle = a;
    color = c;
    scale = s;
}

void Item::incrAngle() {
    angle += 0.5;
}

void Item::setPos(int x, int y) {
    posX = x;
    posY = y;
}

bool Item::isClicked() {
    return clicked;
}

bool Item::isSliding() {
    return sliding;
}

bool Item::isExpanding() {
    return expanding;
}

glm::mat4 Item::getModelingMatrix(int Width, int Height){

    if(expanding){
        scale *= 1.01;
        modelingMat = glm::mat4(1.0f);
        glm::mat4 T = glm::translate(modelingMat, glm::vec3(-10.f +  (posX+0.5f) * (20.f/Width), 10.f  - (posY+0.5) * (20.f/Height), 0.0f));
        glm::mat4 R = glm::rotate(modelingMat, glm::radians(angle), glm::vec3(0.0f, 1.f, 0.f));
        glm::mat4 S = glm::scale(modelingMat, glm::vec3(scale, scale, scale));
        modelingMat = T * S * R;
    }
    else if(sliding){
        down += 0.05;
        modelingMat = glm::mat4(1.0f);
        glm::mat4 T = glm::translate(modelingMat, glm::vec3(-10.f +  (posX+0.5f) * (20.f/Width), 10.f  - (posY+0.5) * (20.f/Height) - down, 0.0f));
        glm::mat4 R = glm::rotate(modelingMat, glm::radians(angle), glm::vec3(0.0f, 1.f, 0.f));
        glm::mat4 S = glm::scale(modelingMat, glm::vec3(scale, scale, scale));
        modelingMat = T * S * R;
    }
    else{
        modelingMat = glm::mat4(1.0f);
        glm::mat4 T = glm::translate(modelingMat, glm::vec3(-10.f +  (posX+0.5f) * (20.f/Width), 10.f  - (posY+0.5) * (20.f/Height), 0.0f));
        glm::mat4 R = glm::rotate(modelingMat, glm::radians(angle), glm::vec3(0.0f, 1.f, 0.f));
        glm::mat4 S = glm::scale(modelingMat, glm::vec3(scale, scale, scale));
        modelingMat = T * S * R;
    }
    return modelingMat;
}
