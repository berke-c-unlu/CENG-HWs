#include <iostream>
#include <cmath>
#include <limits>
#include <vector>
#include <thread>
#include "parser.h"
#include "ppm.h"

typedef unsigned char RGB[3];

typedef enum ObjectType {
    SPHERE = 0,
    TRIANGLE = 1,
    MESH = 2
} ObjectType;

using namespace std;
parser::Vec3f operator + (const parser::Vec3f & a, const parser::Vec3f & b){
    parser::Vec3f result = {0,0,0};

    result.x = a.x + b.x;
    result.y = a.y + b.y;
    result.z = a.z + b.z;

    return result;
}

parser::Vec3f operator / (const parser::Vec3f &a, const float & s){
    parser::Vec3f result = {0,0,0};

    result.x = a.x / s;
    result.y = a.y / s;
    result.z = a.z / s;

    return result;
}

parser::Vec3f operator * (const parser::Vec3f & a, const float & s){
    parser::Vec3f result = {0,0,0};

    result.x = a.x*s;
    result.y = a.y*s;
    result.z = a.z*s;

    return result;
}

float operator * (const parser::Vec3f & a, const parser::Vec3f & b){
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

parser::Vec3f operator ^(const parser::Vec3f & a, const parser::Vec3f & b){
    parser::Vec3f result = {0,0,0};

    result.x = a.y * b.z - a.z * b.y;
    result.y = a.z * b.x - a.x * b.z;
    result.z = a.x * b.y - a.y * b.x;

    return result;
}

parser::Vec3f normalize(const parser::Vec3f & a){
    return a * (1.0/sqrt(a*a));
}

parser::Vec3f componentMult(const parser::Vec3f & a, const parser::Vec3f & b){
    parser::Vec3f result = {0,0,0};

    result.x = a.x * b.x;
    result.y = a.y * b.y;
    result.z = a.z * b.z;

    return result;   
}

float determinant(float m[3][3]){
    return m[0][0]*(m[1][1]*m[2][2] - m[1][2]*m[2][1]) + 
             m[1][0]*(m[0][2]*m[2][1] - m[0][1]*m[2][2]) + 
              m[2][0]*(m[0][1]*m[1][2] - m[1][1]*m[0][2]);
}

float size(const parser::Vec3f & vec){
    return sqrt(vec.x * vec.x + vec.y*vec.y + vec.z*vec.z);
}

void print(const parser::Vec3f & a){
    cout << "(" <<a.x << " " << a.y << " " << a.z  << ")"<< endl;
}


parser::Vec3f DiffuseShading(const parser::Vec3f & reflectance, const parser::Vec3f & w_i, const parser::Vec3f &n, const parser::Vec3f & irradiance){
    parser::Vec3f diffuse = {0,0,0};
    float dot = w_i * n;

    float cosTheta = std::fmaxf(0,dot);

    diffuse.x = reflectance.x * cosTheta * irradiance.x;
    diffuse.y = reflectance.y * cosTheta * irradiance.y;
    diffuse.z = reflectance.z * cosTheta * irradiance.z;

    return diffuse;

}

parser::Vec3f AmbientShading(const parser::Vec3f & ambientLight, const parser::Vec3f & ambientReflectance){
    parser::Vec3f result = {0,0,0};

    result = componentMult(ambientLight,ambientReflectance);

    return result;
}

parser::Vec3f SpecularShading(const parser::Vec3f & reflectance, const parser::Vec3f & w_i,const parser::Vec3f & w_o, const parser::Vec3f &n, const parser::Vec3f & irradiance, const float & phongExp){
    parser::Vec3f specular = {0,0,0};
    parser::Vec3f h = w_i + w_o;
    h = normalize(h);

    float dot = n * h;
    float cosAlpha = std::fmaxf(0,dot);
    float cosAlphaPhong = powf(cosAlpha,phongExp);
    

    specular.x = reflectance.x * cosAlphaPhong * irradiance.x;
    specular.y = reflectance.y * cosAlphaPhong * irradiance.y;
    specular.z = reflectance.z * cosAlphaPhong * irradiance.z;


    return specular; 


}

bool CheckShadow(const parser::Vec3f & x, const parser::Vec3f  w_i, parser::Vec3f n, const parser::Scene & scene); // implemented after Ray class

class Ray {
public:
    parser::Vec3f o,d;

    /* Generates ray with given origin and direction */
    Ray(parser::Vec3f o, parser::Vec3f d){
        this->o = o;
        this->d = d;
    }

    /* Generates ray at given pixel */
    Ray(const int & i, const int &j, const parser::Camera & cam){
        float su,sv;
        parser::Vec3f m,q,s;
        parser::Vec3f u,v,w;

        const float & l = cam.near_plane.x;
        const float & r = cam.near_plane.y;
        const float & b = cam.near_plane.z;
        const float & t = cam.near_plane.w;

        parser::Vec3f e = cam.position;
        float dist = cam.near_distance;

        su = (i + 0.5) * (r - l) / cam.image_width;
        sv = (j + 0.5) * (t - b) / cam.image_height;

        v = cam.up;
        w = cam.gaze * -1;
        u = v^w;


        m = e + (w * -dist);
        q = m + (u * l) + (v * t);
        s = q + (u * su) + (v * -sv);

        this->o = e;
        this->d = s + (e * -1);
    }


    float intersectWithSphere(const parser::Scene & scene, const parser::Sphere & sphere){
        parser::Vec3f centerOfSphere = scene.vertex_data[sphere.center_vertex_id - 1];
        float r = sphere.radius;

        float A,B,C;

        float delta;

        float t,t1,t2;

        parser::Vec3f o_c = this->o + (centerOfSphere * -1);

        A = (this->d * this->d);
        B = (this->d * 2) *o_c;
        C = (o_c*o_c) - r*r;

        delta = B * B - 4 * A * C;

        // no roots
        if(delta < 0) {
            return -1;
        }
        // repeated one root
        else if (delta == 0){
            t = -B / 2 * A;
        }
        // two distinct roots
        else {
            delta = sqrt(delta);
            A = 2*A;
            t1 = (-B + delta) / A;
            t2 = (-B - delta) / A;

            t1 < t2 ? t = t1 : t = t2;
        }

        return t;
    }

    float intersectWithTriangle(const parser::Scene & scene, const parser::Triangle & triangle){
        parser::Vec3f a = scene.vertex_data[triangle.indices.v0_id-1];
        parser::Vec3f b = scene.vertex_data[triangle.indices.v1_id-1];
        parser::Vec3f c = scene.vertex_data[triangle.indices.v2_id-1];

        float A[3][3] = {{a.x - b.x, a.x - c.x, this->d.x},
                         {a.y - b.y, a.y - c.y, this->d.y},
                         {a.z - b.z, a.z - c.z, this->d.z}};

        float betaMatrix[3][3] = {{a.x - this->o.x, a.x - c.x, this->d.x},
                                  {a.y - this->o.y, a.y - c.y, this->d.y},
                                  {a.z - this->o.z, a.z - c.z, this->d.z}};

        float gammaMatrix[3][3] = {{a.x - b.x, a.x - this->o.x, this->d.x},
                                   {a.y - b.y, a.y - this->o.y, this->d.y},
                                   {a.z - b.z, a.z - this->o.z, this->d.z}};

        float tMatrix[3][3] = {{a.x - b.x, a.x - c.x, a.x - this->o.x},
                               {a.y - b.y, a.y - c.y, a.y - this->o.y},
                               {a.z - b.z, a.z - c.z, a.z - this->o.z}};
        
        float detA = determinant(A);
        float beta = determinant(betaMatrix) / detA;
        float gamma = determinant(gammaMatrix) / detA;
        float t = determinant(tMatrix) / detA;

        if(t > 0.001 && t <= 1e16 && beta + gamma <= 1.0f && beta >= 0.0f && gamma >= 0.0f){
            //intersect
            return t;
        }
        return -1;
    }

    float intersectWithMesh(const parser::Scene & scene, const parser::Mesh & mesh, int* faceId){
        float minT = 100000;
        bool intersect = false;
        for(int f=0;f<mesh.faces.size();f++){
            parser::Face face = mesh.faces[f];
            
            parser::Vec3f a = scene.vertex_data[face.v0_id-1];
            parser::Vec3f b = scene.vertex_data[face.v1_id-1];
            parser::Vec3f c = scene.vertex_data[face.v2_id-1];

            float A[3][3] = {{a.x - b.x, a.x - c.x, this->d.x},
                {a.y - b.y, a.y - c.y, this->d.y},
                {a.z - b.z, a.z - c.z, this->d.z}};

            float betaMatrix[3][3] = {{a.x - this->o.x, a.x - c.x, this->d.x},
                                    {a.y - this->o.y, a.y - c.y, this->d.y},
                                    {a.z - this->o.z, a.z - c.z, this->d.z}};

            float gammaMatrix[3][3] = {{a.x - b.x, a.x - this->o.x, this->d.x},
                                    {a.y - b.y, a.y - this->o.y, this->d.y},
                                    {a.z - b.z, a.z - this->o.z, this->d.z}};

            float tMatrix[3][3] = {{a.x - b.x, a.x - c.x, a.x - this->o.x},
                                {a.y - b.y, a.y - c.y, a.y - this->o.y},
                                {a.z - b.z, a.z - c.z, a.z - this->o.z}};
            
            float detA = determinant(A); 
            float beta = determinant(betaMatrix) / detA;
            float gamma = determinant(gammaMatrix) / detA;
            float t = determinant(tMatrix) / detA;

            if(t > 0.001  && t <= 1e16 && beta + gamma <= 1.0f + scene.shadow_ray_epsilon && beta >= 0.0f - scene.shadow_ray_epsilon && gamma >= 0.0f - scene.shadow_ray_epsilon && t<minT){
                //intersect
                intersect = true;
                minT = t;
                *faceId = f;
            }
        }
        if(intersect) 
            return minT;
        return -1;
    }

    parser::Vec3f computeColor(const parser::Scene & scene, const parser::Vec3f & camPosition, int depth){
        parser::Vec3f color = {0,0,0};
        if(depth<0){
            return color;
        }

        float t = -1;
        float minT = 1000000;
        int minI = -1;

        color.x = scene.background_color.x;
        color.y = scene.background_color.y;
        color.z = scene.background_color.z;

        ObjectType type;
        
        for(int i=0;i<scene.spheres.size();i++){
            t = this->intersectWithSphere(scene,scene.spheres[i]);
            if(t>=0 && t<minT){
                minT = t;
                minI = i;
                type = SPHERE;
            }
        }
        
        for(int i=0;i<scene.triangles.size();i++){
            t = this->intersectWithTriangle(scene,scene.triangles[i]);
            if(t>=0 && t<minT){
                minT = t;
                minI = i;
                type = TRIANGLE;
            }
        }
        int faceId = -1;
        for(int i=0;i<scene.meshes.size();i++){
            int id=-1;
            t = this->intersectWithMesh(scene,scene.meshes[i],&id);
            if(t>=0 && t<minT){
                minT = t;
                minI = i;
                type = MESH;
                faceId = id;
            }
        }
        
        if(minI != -1){
            color = lighting(scene,type,minI,minT,camPosition,faceId,depth);
        }
        else if(depth < scene.max_recursion_depth){
            color.x = 0;
            color.y = 0;
            color.z = 0;    
        }
        
        return color;
        
    }

    parser::Vec3f lighting(const parser::Scene & scene, const ObjectType & objectType, const int & objectID, const float & t, const parser::Vec3f & camPosition, int faceId, int depth){
        parser::Vec3f ambientLight = scene.ambient_light;
        std::vector<parser::PointLight> pointLights = scene.point_lights;
        int lightsLen = pointLights.size();

        parser::Vec3f diffuseLighting = {0,0,0};
        parser::Vec3f phong = {0,0,0};
        parser::Vec3f ambientLighting = {0,0,0};
        parser::Vec3f mirrorLighting = {0,0,0};

        // intersect point
        parser::Vec3f x = this->o + (this->d * t);


        // vector from intersect point to camera
        parser::Vec3f w_o = camPosition + (x * -1);

        if(objectType == SPHERE){

            /* Sphere variables */
            parser::Sphere sphere = scene.spheres[objectID];
            float r = sphere.radius;
            parser::Vec3f center = scene.vertex_data[sphere.center_vertex_id - 1];
            parser::Material material = scene.materials[sphere.material_id - 1];
            // normal vector of sphere
            parser::Vec3f n = x + (center * -1);

            // material information
            parser::Vec3f ambientReflectance = material.ambient;
            parser::Vec3f diffuseReflectance = material.diffuse;
            parser::Vec3f specularReflectance = material.specular;
            parser::Vec3f mirrorReflectance = material.mirror;
            float phongExp = material.phong_exponent;

            // Ambient Calculation
            ambientLighting = AmbientShading(ambientLight,ambientReflectance);

            for(int i = 0 ; i < lightsLen; i++){

                // light position
                parser::Vec3f lightPoint = pointLights[i].position;

                // vector from intersect point to light
                parser::Vec3f w_i = lightPoint + (x * -1);

                // check if it is in shadow
                if(CheckShadow(x,w_i,n,scene))
                    continue;

                // distance square to find irradiance
                float distanceSqr = w_i * w_i;
                
                parser::Vec3f irradiance =  pointLights[i].intensity / distanceSqr;
                
                // normalize vectors
                w_i = normalize(w_i);
                w_o = normalize(w_o);
                n = normalize(n);

                // find diffuse shading and specular shading
                parser::Vec3f currentDiffuse = DiffuseShading(diffuseReflectance,w_i,n,irradiance);
                parser::Vec3f currentPhong = SpecularShading(specularReflectance,w_i,w_o,n,irradiance,phongExp);

                phong = phong + currentPhong;
                diffuseLighting = diffuseLighting + currentDiffuse;
            } 
            
            // mirror calculation
            if(depth>=0 && material.is_mirror){
                n = normalize(n);
                w_o = normalize(w_o);
                float dot = w_o * n;
                float cosTheta = std::fmaxf(0,dot);
                parser::Vec3f w_r = (w_o * -1) + (n*(cosTheta)) * 2;
                w_r = normalize(w_r);
                Ray reflectiveRay(x +  n * scene.shadow_ray_epsilon,w_r);
                mirrorLighting = componentMult(reflectiveRay.computeColor(scene,x,depth-1),mirrorReflectance);
            }
        }

        else if(objectType == TRIANGLE){
            
            /* Triangle variables */
            parser::Triangle triangle = scene.triangles[objectID];
            parser::Material material = scene.materials[triangle.material_id - 1];

            // normal vector of face (this can be found in the parsing part, will be handled later)
            parser::Vec3f n = triangle.indices.n;

            // material information
            parser::Vec3f ambientReflectance = material.ambient;
            parser::Vec3f diffuseReflectance = material.diffuse;
            parser::Vec3f specularReflectance = material.specular;
            parser::Vec3f mirrorReflectance = material.mirror;
            float phongExp = material.phong_exponent;
            
            // Ambient Calculation
            ambientLighting = AmbientShading(ambientLight,ambientReflectance);

            for(int i = 0 ; i < lightsLen; i++){
                
                // light position
                parser::Vec3f lightPoint = pointLights[i].position;
                
                // vector from intersect point to light
                parser::Vec3f w_i = lightPoint + (x * -1);

                // check if it is in shadow
                if(CheckShadow(x,w_i,n,scene))
                    continue;

                // distance square to find irradiance
                float distanceSqr = w_i * w_i;

                parser::Vec3f irradiance = pointLights[i].intensity / distanceSqr;
                
                // normalize vectors
                w_i = normalize(w_i);
                w_o = normalize(w_o);
                n = normalize(n);

                // find diffuse shading and specular shading
                parser::Vec3f currentDiffuse = DiffuseShading(diffuseReflectance,w_i,n,irradiance);
                parser::Vec3f currentPhong = SpecularShading(specularReflectance,w_i,w_o,n,irradiance,phongExp);
                
                diffuseLighting = diffuseLighting + currentDiffuse;
                phong = phong + currentPhong;
            }
        
            // mirror calculation
            if(depth>=0 && material.is_mirror){
                n = normalize(n);
                w_o = normalize(w_o);
                float dot = w_o * n;
                float cosTheta = std::fmaxf(0,dot);
                parser::Vec3f w_r = (w_o * -1) + (n*(cosTheta)) * 2;
                w_r = normalize(w_r);
                Ray reflectiveRay(x +  n * scene.shadow_ray_epsilon,w_r);
                mirrorLighting = componentMult(reflectiveRay.computeColor(scene,x,depth-1),mirrorReflectance);
            }
        }

        // mesh
        else{

            /* Mesh variables */
            parser::Mesh mesh = scene.meshes[objectID];
            parser::Face face = mesh.faces[faceId];
            parser::Material material = scene.materials[mesh.material_id - 1];
            // normal vector of face
            //parser::Vec3f n = (b + (a*-1)) ^ (c + (a*-1));
            parser::Vec3f n = face.n;

            // material information
            parser::Vec3f ambientReflectance = material.ambient;
            parser::Vec3f diffuseReflectance = material.diffuse;
            parser::Vec3f specularReflectance = material.specular;
            parser::Vec3f mirrorReflectance = material.mirror;
            float phongExp = material.phong_exponent;

            // Ambient Calculation
            ambientLighting = AmbientShading(ambientLight,ambientReflectance);

            for(int i = 0 ; i < lightsLen; i++){

                // light position
                parser::Vec3f lightPoint = pointLights[i].position;
                
                // vector from intersect point to light
                parser::Vec3f w_i = lightPoint + (x * -1);

                // check if it is in shadow
                if(CheckShadow(x,w_i,n,scene))
                   continue;
                
                // distance square to find irradiance
                float distanceSqr = w_i * w_i;

                parser::Vec3f irradiance = pointLights[i].intensity / distanceSqr;

                // normalize vectors
                w_i = normalize(w_i);
                w_o = normalize(w_o);
                n = normalize(n);

                // find diffuse shading and specular shading
                parser::Vec3f currentDiffuse = DiffuseShading(diffuseReflectance,w_i,n,irradiance);
                parser::Vec3f currentPhong = SpecularShading(specularReflectance,w_i,w_o,n,irradiance,phongExp);
                
                diffuseLighting = diffuseLighting + currentDiffuse;
                phong = phong + currentPhong;
            }
            
            // Mirror Calculation
            if(depth>=0 && material.is_mirror){
                n = normalize(n);
                w_o = normalize(w_o);
                float dot = w_o * n;
                float cosTheta = std::fmaxf(0,dot);
                parser::Vec3f w_r = (w_o * -1) + (n*(cosTheta)) * 2;
                w_r = normalize(w_r);
                Ray reflectiveRay(x +  n * scene.shadow_ray_epsilon,w_r);
                mirrorLighting = componentMult(reflectiveRay.computeColor(scene,x,depth-1),mirrorReflectance);
            }
        }
        
        
        return diffuseLighting + ambientLighting + phong + mirrorLighting;
    }

};

bool CheckShadow(const parser::Vec3f & x, const parser::Vec3f  w_i, parser::Vec3f n, const parser::Scene & scene){
    float epsilon = scene.shadow_ray_epsilon;
    parser::Vec3f d = normalize(w_i);
    float maxT = w_i.x / d.x;
    n = normalize(n);
    Ray shadowRay(x + n*epsilon,d);
    float t = -1;
    for(int i=0;i<scene.spheres.size();i++){
        t = shadowRay.intersectWithSphere(scene,scene.spheres[i]);
        if(t> epsilon && t < maxT){
            return true;
        }
    }
    for(int i=0;i<scene.triangles.size();i++){
        t = shadowRay.intersectWithTriangle(scene,scene.triangles[i]);
        if(t> epsilon && t < maxT){
            return true;
        }
    }
    for(int i=0;i<scene.meshes.size();i++){
        int id;
        t = shadowRay.intersectWithMesh(scene,scene.meshes[i],&id);
        if(t> epsilon && t < maxT){
            return true;
        }
    }
    return false;
}


void render(unsigned char *image,const parser::Scene & scene, const parser::Camera & cam, int minx, int miny, int maxx,int maxy){

        int width = cam.image_width;
        int height = cam.image_height;
        int pixelIndex = (miny)*(width)*3;
        for(int r = miny ; r < maxy; r++) {
            for(int c = 0; c < width; c++){
                Ray ray(c,r,cam); // r,k or k,r??
                parser::Vec3f rayColor = ray.computeColor(scene,cam.position,scene.max_recursion_depth);

                rayColor.x > 255 ? image[pixelIndex]     = 255 : image[pixelIndex]     = round(rayColor.x);
                rayColor.y > 255 ? image[pixelIndex + 1] = 255 : image[pixelIndex + 1] = round(rayColor.y);
                rayColor.z > 255 ? image[pixelIndex + 2] = 255 : image[pixelIndex + 2] = round(rayColor.z);

                
                pixelIndex += 3;
            }
        }
}

int main(int argc, char* argv[])
{
    // Sample usage for reading an XML scene file
    parser::Scene scene;
    if(argc < 2){
        cout << "Usage: ./raytracer file-path" << endl;
        return 0;
    }

    string file(argv[1]);
    scene.loadFromXml(file);

    
    int cameraCount = scene.cameras.size();
    for(int i = 0 ; i < cameraCount; i++){

        parser::Camera currentCam = scene.cameras[i];      
        int width = currentCam.image_width;
        int height = currentCam.image_height;
        unsigned char* image = new unsigned char [width * height * 3];  
        const char num = 49+i;

        string name = currentCam.image_name;
        auto nameSize = name.length();

        char* ppmName = new char[nameSize+1];

        for(int i = 0 ; i < nameSize; i++){
            ppmName[i] = name[i];
        }
        ppmName[nameSize] = '\0';

        for(int r=0;r<height;r++){
            for(int c=0;c<width*3;c+=3){
                image[r*width*3+c] = scene.background_color.x;
                image[r*width*3+c+1] = scene.background_color.y;
                image[r*width*3+c+2] = scene.background_color.z;
            }
        }
        
        int patchHeight = height / 8;
        thread t1(render,image,scene,currentCam,0,0,width,patchHeight);
        thread t2(render,image,scene,currentCam,0,patchHeight,width,2*patchHeight);
        thread t3(render,image,scene,currentCam,0,2*patchHeight,width,3*patchHeight);
        thread t4(render,image,scene,currentCam,0,3*patchHeight,width,4*patchHeight);
        thread t5(render,image,scene,currentCam,0,4*patchHeight,width,5*patchHeight);
        thread t6(render,image,scene,currentCam,0,5*patchHeight,width,6*patchHeight);
        thread t7(render,image,scene,currentCam,0,6*patchHeight,width,7*patchHeight);
        thread t8(render,image,scene,currentCam,0,7*patchHeight,width,8*patchHeight);

        //thread t2(render,image,scene,currentCam,0,0,currentCam.image_width,currentCam.image_height);
        
        //render(image,sceberserker
        t1.join();
        t2.join();
        t3.join();
        t4.join();
        t5.join();
        t6.join();
        t7.join();
        t8.join();


        write_ppm(ppmName, image, width, height);

        

    }


}