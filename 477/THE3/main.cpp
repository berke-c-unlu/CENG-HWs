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
#include <ft2build.h>
#include "item.h"
#include FT_FREETYPE_H

#define BUFFER_OFFSET(i) ((char*)NULL + (i))

using namespace std;

GLuint gProgram[3];
GLint gIntensityLoc;
float gIntensity = 50;
int gWidth = 640, gHeight = 600;
int Width, Height; // grid width and height
float scalingFactor;
vector<vector<Item>> grid;
vector<vector<bool>> grid_match;
int clickedX, clickedY;
// five colors
vector<glm::vec3> colors{glm::vec3(0.5f,0.f,0.f), glm::vec3(0.f,0.5f,0.f), glm::vec3(0.f,0.f,0.5f), glm::vec3(0.5f,0.5f,0.f), glm::vec3(0.5f,0.f,0.5f)};

bool expanding = false;
bool sliding = false;
bool restart = false;
int clickCount = 0;
int score = 0;
int afterScore = 0;


struct Vertex
{
    Vertex(GLfloat inX, GLfloat inY, GLfloat inZ) : x(inX), y(inY), z(inZ) { }
    GLfloat x, y, z;
};

struct Texture
{
    Texture(GLfloat inU, GLfloat inV) : u(inU), v(inV) { }
    GLfloat u, v;
};

struct Normal
{
    Normal(GLfloat inX, GLfloat inY, GLfloat inZ) : x(inX), y(inY), z(inZ) { }
    GLfloat x, y, z;
};

struct Face
{
	Face(int v[], int t[], int n[]) {
		vIndex[0] = v[0];
		vIndex[1] = v[1];
		vIndex[2] = v[2];
		tIndex[0] = t[0];
		tIndex[1] = t[1];
		tIndex[2] = t[2];
		nIndex[0] = n[0];
		nIndex[1] = n[1];
		nIndex[2] = n[2];
	}
    GLuint vIndex[3], tIndex[3], nIndex[3];
};

vector<Vertex> gVertices;
vector<Texture> gTextures;
vector<Normal> gNormals;
vector<Face> gFaces;

GLuint gVertexAttribBuffer, gTextVBO, gIndexBuffer;
GLint gInVertexLoc, gInNormalLoc;
int gVertexDataSizeInBytes, gNormalDataSizeInBytes;

/// Holds all state information relevant to a character as loaded using FreeType
struct Character {
    GLuint TextureID;   // ID handle of the glyph texture
    glm::ivec2 Size;    // Size of glyph
    glm::ivec2 Bearing;  // Offset from baseline to left/top of glyph
    GLuint Advance;    // Horizontal offset to advance to next glyph
};

std::map<GLchar, Character> Characters;


bool ParseObj(const string& fileName)
{
    fstream myfile;

    // Open the input 
    myfile.open(fileName.c_str(), std::ios::in);

    if (myfile.is_open())
    {
        string curLine;

        while (getline(myfile, curLine))
        {
            stringstream str(curLine);
            GLfloat c1, c2, c3;
            GLuint index[9];
            string tmp;

            if (curLine.length() >= 2)
            {
                if (curLine[0] == '#') // comment
                {
                    continue;
                }
                else if (curLine[0] == 'v')
                {
                    if (curLine[1] == 't') // texture
                    {
                        str >> tmp; // consume "vt"
                        str >> c1 >> c2;
                        gTextures.push_back(Texture(c1, c2));
                    }
                    else if (curLine[1] == 'n') // normal
                    {
                        str >> tmp; // consume "vn"
                        str >> c1 >> c2 >> c3;
                        gNormals.push_back(Normal(c1, c2, c3));
                    }
                    else // vertex
                    {
                        str >> tmp; // consume "v"
                        str >> c1 >> c2 >> c3;
                        gVertices.push_back(Vertex(c1, c2, c3));
                    }
                }
                else if (curLine[0] == 'f') // face
                {
                    str >> tmp; // consume "f"
					char c;
					int vIndex[3],  nIndex[3], tIndex[3];
					str >> vIndex[0]; str >> c >> c; // consume "//"
					str >> nIndex[0]; 
					str >> vIndex[1]; str >> c >> c; // consume "//"
					str >> nIndex[1]; 
					str >> vIndex[2]; str >> c >> c; // consume "//"
					str >> nIndex[2]; 

					assert(vIndex[0] == nIndex[0] &&
						   vIndex[1] == nIndex[1] &&
						   vIndex[2] == nIndex[2]); // a limitation for now

					// make indices start from 0
					for (int c = 0; c < 3; ++c)
					{
						vIndex[c] -= 1;
						nIndex[c] -= 1;
						tIndex[c] -= 1;
					}

                    gFaces.push_back(Face(vIndex, tIndex, nIndex));
                }
                else
                {
                    cout << "Ignoring unidentified line in obj file: " << curLine << endl;
                }
            }

            //data += curLine;
            if (!myfile.eof())
            {
                //data += "\n";
            }
        }

        myfile.close();
    }
    else
    {
        return false;
    }

	/*
	for (int i = 0; i < gVertices.size(); ++i)
	{
		Vector3 n;

		for (int j = 0; j < gFaces.size(); ++j)
		{
			for (int k = 0; k < 3; ++k)
			{
				if (gFaces[j].vIndex[k] == i)
				{
					// face j contains vertex i
					Vector3 a(gVertices[gFaces[j].vIndex[0]].x, 
							  gVertices[gFaces[j].vIndex[0]].y,
							  gVertices[gFaces[j].vIndex[0]].z);

					Vector3 b(gVertices[gFaces[j].vIndex[1]].x, 
							  gVertices[gFaces[j].vIndex[1]].y,
							  gVertices[gFaces[j].vIndex[1]].z);

					Vector3 c(gVertices[gFaces[j].vIndex[2]].x, 
							  gVertices[gFaces[j].vIndex[2]].y,
							  gVertices[gFaces[j].vIndex[2]].z);

					Vector3 ab = b - a;
					Vector3 ac = c - a;
					Vector3 normalFromThisFace = (ab.cross(ac)).getNormalized();
					n += normalFromThisFace;
				}

			}
		}

		n.normalize();

		gNormals.push_back(Normal(n.x, n.y, n.z));
	}
	*/

	assert(gVertices.size() == gNormals.size());

    return true;
}

bool ReadDataFromFile(
    const string& fileName, ///< [in]  Name of the shader file
    string&       data)     ///< [out] The contents of the file
{
    fstream myfile;

    // Open the input 
    myfile.open(fileName.c_str(), std::ios::in);

    if (myfile.is_open())
    {
        string curLine;

        while (getline(myfile, curLine))
        {
            data += curLine;
            if (!myfile.eof())
            {
                data += "\n";
            }
        }

        myfile.close();
    }
    else
    {
        return false;
    }

    return true;
}

void createVS(GLuint& program, const string& filename)
{
    string shaderSource;

    if (!ReadDataFromFile(filename, shaderSource))
    {
        cout << "Cannot find file name: " + filename << endl;
        exit(-1);
    }

    GLint length = shaderSource.length();
    const GLchar* shader = (const GLchar*) shaderSource.c_str();

    GLuint vs = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vs, 1, &shader, &length);
    glCompileShader(vs);

    char output[1024] = {0};
    glGetShaderInfoLog(vs, 1024, &length, output);
    printf("VS compile log: %s\n", output);

    glAttachShader(program, vs);
}

void createFS(GLuint& program, const string& filename)
{
    string shaderSource;

    if (!ReadDataFromFile(filename, shaderSource))
    {
        cout << "Cannot find file name: " + filename << endl;
        exit(-1);
    }

    GLint length = shaderSource.length();
    const GLchar* shader = (const GLchar*) shaderSource.c_str();

    GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fs, 1, &shader, &length);
    glCompileShader(fs);

    char output[1024] = {0};
    glGetShaderInfoLog(fs, 1024, &length, output);
    printf("FS compile log: %s\n", output);

    glAttachShader(program, fs);
}

void initShaders()
{
    gProgram[0] = glCreateProgram();
    gProgram[1] = glCreateProgram();
    gProgram[2] = glCreateProgram();

    createVS(gProgram[0], "vert0.glsl");
    createFS(gProgram[0], "frag0.glsl");

    createVS(gProgram[1], "vert1.glsl");
    createFS(gProgram[1], "frag1.glsl");

    createVS(gProgram[2], "vert_text.glsl");
    createFS(gProgram[2], "frag_text.glsl");

    glBindAttribLocation(gProgram[0], 0, "inVertex");
    glBindAttribLocation(gProgram[0], 1, "inNormal");
    glBindAttribLocation(gProgram[1], 0, "inVertex");
    glBindAttribLocation(gProgram[1], 1, "inNormal");
    glBindAttribLocation(gProgram[2], 2, "vertex");

    glLinkProgram(gProgram[0]);
    glLinkProgram(gProgram[1]);
    glLinkProgram(gProgram[2]);

    // glUseProgram(gProgram[1]);
    // glUniform1f(glGetUniformLocation(gProgram[1], "intensity"),gIntensity);

    glUseProgram(gProgram[0]);
    gIntensityLoc = glGetUniformLocation(gProgram[0], "intensity");

    cout << "gIntensityLoc = " << gIntensityLoc << endl;
    glUniform1f(gIntensityLoc, gIntensity);
}

void initVBO()
{
    glEnableVertexAttribArray(0);
    glEnableVertexAttribArray(1);
    assert(glGetError() == GL_NONE);

    glGenBuffers(1, &gVertexAttribBuffer);
    glGenBuffers(1, &gIndexBuffer);

    assert(gVertexAttribBuffer > 0 && gIndexBuffer > 0);

    glBindBuffer(GL_ARRAY_BUFFER, gVertexAttribBuffer);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gIndexBuffer);

    gVertexDataSizeInBytes = gVertices.size() * 3 * sizeof(GLfloat);
    gNormalDataSizeInBytes = gNormals.size() * 3 * sizeof(GLfloat);
    int indexDataSizeInBytes = gFaces.size() * 3 * sizeof(GLuint);
    GLfloat* vertexData = new GLfloat [gVertices.size() * 3];
    GLfloat* normalData = new GLfloat [gNormals.size() * 3];
    GLuint* indexData = new GLuint [gFaces.size() * 3];

    float minX = 1e6, maxX = -1e6;
    float minY = 1e6, maxY = -1e6;
    float minZ = 1e6, maxZ = -1e6;

    for (int i = 0; i < gVertices.size(); ++i)
    {
        vertexData[3*i] = gVertices[i].x;
        vertexData[3*i+1] = gVertices[i].y;
        vertexData[3*i+2] = gVertices[i].z;

        minX = std::min(minX, gVertices[i].x);
        maxX = std::max(maxX, gVertices[i].x);
        minY = std::min(minY, gVertices[i].y);
        maxY = std::max(maxY, gVertices[i].y);
        minZ = std::min(minZ, gVertices[i].z);
        maxZ = std::max(maxZ, gVertices[i].z);
    }


    float objWidth = abs(maxX - minX);
    float objHeight = abs(maxY - minY);

    float offsetx = (20/(float)Width) * 0.125;
    float offsety = (20/(float)Height) * 0.125;

    float cellWidth = 20/(float)Width - 2*offsetx;
    float cellHeight = 20/(float)Height - 2*offsety;

    if(cellWidth < cellHeight){
        scalingFactor = cellWidth/objWidth;
    }
    else{
        scalingFactor = cellHeight/objHeight;
    }

    objHeight *= scalingFactor;
    objWidth *= scalingFactor;

    for (int i = 0; i < gNormals.size(); ++i)
    {
        normalData[3*i] = gNormals[i].x;
        normalData[3*i+1] = gNormals[i].y;
        normalData[3*i+2] = gNormals[i].z;
    }

    for (int i = 0; i < gFaces.size(); ++i)
    {
        indexData[3*i] = gFaces[i].vIndex[0];
        indexData[3*i+1] = gFaces[i].vIndex[1];
        indexData[3*i+2] = gFaces[i].vIndex[2];
    }


    glBufferData(GL_ARRAY_BUFFER, gVertexDataSizeInBytes + gNormalDataSizeInBytes, 0, GL_STATIC_DRAW);
    glBufferSubData(GL_ARRAY_BUFFER, 0, gVertexDataSizeInBytes, vertexData);
    glBufferSubData(GL_ARRAY_BUFFER, gVertexDataSizeInBytes, gNormalDataSizeInBytes, normalData);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indexDataSizeInBytes, indexData, GL_STATIC_DRAW);

    // done copying; can free now
    delete[] vertexData;
    delete[] normalData;
    delete[] indexData;

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(gVertexDataSizeInBytes));

}

void initFonts(int windowWidth, int windowHeight)
{
    // Set OpenGL options
    //glEnable(GL_CULL_FACE);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    glm::mat4 projection = glm::ortho(0.0f, static_cast<GLfloat>(windowWidth), 0.0f, static_cast<GLfloat>(windowHeight));
    glUseProgram(gProgram[2]);
    glUniformMatrix4fv(glGetUniformLocation(gProgram[2], "projection"), 1, GL_FALSE, glm::value_ptr(projection));

    // FreeType
    FT_Library ft;
    // All functions return a value different than 0 whenever an error occurred
    if (FT_Init_FreeType(&ft))
    {
        std::cout << "ERROR::FREETYPE: Could not init FreeType Library" << std::endl;
    }

    // Load font as face
    FT_Face face;
    if (FT_New_Face(ft, "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", 0, &face))
    {
        std::cout << "ERROR::FREETYPE: Failed to load font" << std::endl;
    }

    // Set size to load glyphs as
    FT_Set_Pixel_Sizes(face, 0, 48);

    // Disable byte-alignment restriction
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1); 

    // Load first 128 characters of ASCII set
    for (GLubyte c = 0; c < 128; c++)
    {
        // Load character glyph 
        if (FT_Load_Char(face, c, FT_LOAD_RENDER))
        {
            std::cout << "ERROR::FREETYTPE: Failed to load Glyph" << std::endl;
            continue;
        }
        // Generate texture
        GLuint texture;
        glGenTextures(1, &texture);
        glBindTexture(GL_TEXTURE_2D, texture);
        glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RED,
                face->glyph->bitmap.width,
                face->glyph->bitmap.rows,
                0,
                GL_RED,
                GL_UNSIGNED_BYTE,
                face->glyph->bitmap.buffer
                );
        // Set texture options
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        // Now store character for later use
        Character character = {
            texture,
            glm::ivec2(face->glyph->bitmap.width, face->glyph->bitmap.rows),
            glm::ivec2(face->glyph->bitmap_left, face->glyph->bitmap_top),
            face->glyph->advance.x
        };
        Characters.insert(std::pair<GLchar, Character>(c, character));
    }

    glBindTexture(GL_TEXTURE_2D, 0);
    // Destroy FreeType once we're finished
    FT_Done_Face(face);
    FT_Done_FreeType(ft);

    //
    // Configure VBO for texture quads
    //
    glGenBuffers(1, &gTextVBO);
    glBindBuffer(GL_ARRAY_BUFFER, gTextVBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(GLfloat) * 6 * 4, NULL, GL_DYNAMIC_DRAW);

    glEnableVertexAttribArray(2);
    glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), 0);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
}

void initItems(){
    for(int i=0;i<Height;i++){
        grid.push_back(vector<Item>(Width));
        grid_match.push_back(vector<bool>(Width));       
        for(int j=0;j<Width;j++){
            int ind = rand() % 5;
            Item item(j,i,0.f,scalingFactor,colors[ind]);
            grid[i][j] = item;
            grid_match[i][j] = false;
        }
    }
}

void init(string fileName) 
{
	ParseObj(fileName);

    glEnable(GL_DEPTH_TEST);
    initShaders();
    initFonts(gWidth, gHeight);
    initVBO();
    initItems();
}

void drawModel()
{
	glBindBuffer(GL_ARRAY_BUFFER, gVertexAttribBuffer);
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gIndexBuffer);

	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0);
	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, BUFFER_OFFSET(gVertexDataSizeInBytes));

	glDrawElements(GL_TRIANGLES, gFaces.size() * 3, GL_UNSIGNED_INT, 0);
}

void renderText(const std::string& text, GLfloat x, GLfloat y, GLfloat scale, glm::vec3 color)
{
    // Activate corresponding render state	
    glUseProgram(gProgram[2]);
    glUniform3f(glGetUniformLocation(gProgram[2], "textColor"), color.x, color.y, color.z);
    glActiveTexture(GL_TEXTURE0);

    // Iterate through all characters
    std::string::const_iterator c;
    for (c = text.begin(); c != text.end(); c++) 
    {
        Character ch = Characters[*c];

        GLfloat xpos = x + ch.Bearing.x * scale;
        GLfloat ypos = y - (ch.Size.y - ch.Bearing.y) * scale;

        GLfloat w = ch.Size.x * scale;
        GLfloat h = ch.Size.y * scale;

        // Update VBO for each character
        GLfloat vertices[6][4] = {
            { xpos,     ypos + h,   0.0, 0.0 },            
            { xpos,     ypos,       0.0, 1.0 },
            { xpos + w, ypos,       1.0, 1.0 },

            { xpos,     ypos + h,   0.0, 0.0 },
            { xpos + w, ypos,       1.0, 1.0 },
            { xpos + w, ypos + h,   1.0, 0.0 }           
        };

        // Render glyph texture over quad
        glBindTexture(GL_TEXTURE_2D, ch.TextureID);

        // Update content of VBO memory
        glBindBuffer(GL_ARRAY_BUFFER, gTextVBO);
        glBufferSubData(GL_ARRAY_BUFFER, 0, sizeof(vertices), vertices); // Be sure to use glBufferSubData and not glBufferData

        //glBindBuffer(GL_ARRAY_BUFFER, 0);

        // Render quad
        glDrawArrays(GL_TRIANGLES, 0, 6);
        // Now advance cursors for next glyph (note that advance is number of 1/64 pixels)

        x += (ch.Advance >> 6) * scale; // Bitshift by 6 to get value in pixels (2^6 = 64 (divide amount of 1/64th pixels by 64 to get amount of pixels))
    }

    glBindTexture(GL_TEXTURE_2D, 0);
}

int checkGrid(){
    int count = 0;
    int sumCount = 0;
    for(int j=0;j<Width;j++){
        count = 0;
        for(int i=0;i<Height;i++){
            if(!grid[i][j].visible){
                count++;
                for(int k=i-1;k>=0;k--){
                    grid[k+1][j] = grid[k][j];
                    grid[k+1][j].targetY++;
                    grid[k+1][j].sliding = true;
                }
                int ind = rand() % 5;
                Item item(j,-count,0.f,scalingFactor,colors[ind]);
                item.targetY = 0;
                item.sliding = true;
                grid[0][j] = item;
                sliding = true;
            }
        }

    }
    return sumCount;
}


int checkMatching(){
    int count = 0;
    int matching = 0;
    glm::vec3 color;
    // Row check
    for(int i = 0; i < Height; i++){
        count = 0;
        for(int j = 0; j < Width; j++){
            if(count == 0){
                color = grid[i][j].color;
                count++;
                continue;
            }
            if(grid[i][j].color == color){
                count++;
            }

            else{
                if(count < 3){
                    count = 0;
                }
                while(count > 0){
                    matching++;
                    grid_match[i][j-count] = true;
                    count--;
                }
                j--;
            }

            if(j == Width - 1){
                if(count < 3){
                    count = 0;
                }
                while(count > 0){
                    matching++;
                    grid_match[i][j-count + 1] = true;
                    count--;
                }
            }
        }
    }
    color = glm::vec3(0,0,0);
    // Column check
    for(int j = 0; j < Width; j++){
        count = 0;
        for(int i = 0; i < Height; i++){
            if(count == 0){
                color = grid[i][j].color;
                count++;
                continue;
            }
            if(grid[i][j].color == color){
                count++;
            }
            else{
                if(count < 3){
                    count = 0;
                }
                while(count > 0){
                    matching++;
                    grid_match[i-count][j] = true;
                    count--;
                }
                i--;
            }
            if(i == Height - 1){
                if(count < 3){
                    count = 0;
                }
                while(count > 0){
                    matching++;
                    grid_match[i-count + 1][j] = true;
                    count--;
                }
                //i--;
            }
        }
    }
    return matching;

}

void display()
{
    glClearColor(0, 0, 0, 1);
    glClearDepth(1.0f);
    glClearStencil(0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);

	static float angle = 0;
    

    glUseProgram(gProgram[0]);

    int explode = 0;
    int slide = 0;

    if(!sliding && !expanding)
        slide = checkGrid();
    if(!sliding && !expanding){
        explode = checkMatching();
        for(int i=0;i<Height;i++){
            for(int j=0;j<Width;j++){
                if(grid_match[i][j]){
                    score++;
                    grid[i][j].expanding = true;
                    expanding = true;
                }
            }
        }
        // reset grid_match to all false
        for(int i=0;i<Height;i++){
            for(int j=0;j<Width;j++){
                grid_match[i][j] = false;
            }
        }
    }

    for(int i=0;i<Height;i++){
        for(int j=0;j<Width;j++){

            glm::mat4 modelMat, modelMatInv, orthoMat;

            
            // Expanding object scaling
            if(grid[i][j].expanding && grid[i][j].scale >= 1.5f * scalingFactor){
                grid[i][j].expanding = false;
                grid[i][j].scale = scalingFactor;

                grid[i][j].visible = false;

                bool check = false;
                for(int k=0;k<Height;k++){
                    for(int l=0;l<Width;l++){
                        check = check || grid[k][l].expanding;
                    }
                }
                if(!check){
                    afterScore = score;
                    expanding = false;
                }
            }

            
            if(grid[i][j].sliding && abs(grid[i][j].posY - grid[i][j].targetY) * (20.f/Height) < grid[i][j].down){
                grid[i][j].sliding = false;      

                // adjust grid
                grid[i][j].posY = grid[i][j].targetY;
                grid[i][j].down = 0;

                // check any item is sliding
                bool check = false;
                for(int k=0;k<Height;k++){
                    for(int l=0;l<Width;l++){
                        check = check || grid[k][l].sliding;
                    }
                }
                if(!check){
                    sliding = false;
                }
            }
            modelMat = grid[i][j].getModelingMatrix(Width,Height);
            modelMatInv = glm::transpose(glm::inverse(modelMat));
            orthoMat = glm::ortho(-10.f,10.f,-10.f,10.f,-20.f,20.f);
             
            glUniformMatrix4fv(glGetUniformLocation(gProgram[0], "modelingMat"), 1, GL_FALSE, glm::value_ptr(modelMat));
            glUniformMatrix4fv(glGetUniformLocation(gProgram[0], "modelingMatInvTr"), 1, GL_FALSE, glm::value_ptr(modelMatInv));
            glUniformMatrix4fv(glGetUniformLocation(gProgram[0], "orthoMat"), 1, GL_FALSE, glm::value_ptr(orthoMat));
            glUniform3fv(glGetUniformLocation(gProgram[0], "kd"), 1, glm::value_ptr(grid[i][j].color));                drawModel();
            grid[i][j].incrAngle();

            
            


        }
    }

    string scoreText = " Score: " + to_string(afterScore);
    string moves = "Moves: " + to_string(clickCount);

    string text = moves + scoreText;
    renderText(text, 0, 0, 1, glm::vec3(0, 1, 1));

    assert(glGetError() == GL_NO_ERROR);

}

void reshape(GLFWwindow* window, int w, int h)
{
    w = w < 1 ? 1 : w;
    h = h < 1 ? 1 : h;

    gWidth = w;
    gHeight = h;

    glViewport(0, 0, w, h);
}

void keyboard(GLFWwindow* window, int key, int scancode, int action, int mods)
{
    if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS)
    {
        glfwSetWindowShouldClose(window, GL_TRUE);
    }
    else if(key == GLFW_KEY_R && action == GLFW_PRESS){
        cout << "R pressed. Game will restart." << endl;
        restart = true;
    }
}

void mouse(GLFWwindow* window, int button, int action, int mods)
{
    if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_PRESS && !expanding && !sliding)
    {
        double xpos, ypos;
        glfwGetCursorPos(window, &xpos, &ypos);

        cout << "xpos: " << xpos << " ypos: " << ypos << endl;


        int x = (int)((xpos * 20 / (float)gWidth) / (20.f/Width));
        int y = (int)((ypos * 20 / (float)gHeight) / (20.f/Height));

        if(y > Height-1)
            return;

        cout << "row: " << y << " col: " << x << endl;
        cout << endl;
        
        expanding = true;

        grid[y][x].expanding = true;
        clickCount++;
    }
}


void mainLoop(GLFWwindow* window)
{
    while (!glfwWindowShouldClose(window))
    {
        if(restart){
            restart = false;
            expanding = false;
            sliding = false;
            clickCount = 0;
            score = 0;
            afterScore = 0;
            initItems();
        }
        display();
        glfwSwapBuffers(window);
        glfwPollEvents();
    }
}

int main(int argc, char** argv)   // Create Main Function For Bringing It All Together
{

    GLFWwindow* window;
    if (!glfwInit())
    {
        exit(-1);
    }


    if(argc > 5){
        cout << "Arg number is not true: " << argc << endl;
        return 0;
    }
    Width = stoi(argv[1]);
    Height = stoi(argv[2]);
    string fileName(argv[3]);

    cout << "width: " << Width << endl;
    cout << "height: " << Height << endl;
    cout << "file_name: " << fileName << endl;


    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    //glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_COMPAT_PROFILE);
    //glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);

    window = glfwCreateWindow(gWidth, gHeight, "Simple Example", NULL, NULL);

    if (!window)
    {
        glfwTerminate();
        exit(-1);
    }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    // Initialize GLEW to setup the OpenGL Function pointers
    if (GLEW_OK != glewInit())
    {
        std::cout << "Failed to initialize GLEW" << std::endl;
        return EXIT_FAILURE;
    }

    char rendererInfo[512] = {0};
    strcpy(rendererInfo, (const char*) glGetString(GL_RENDERER));
    strcat(rendererInfo, " - ");
    strcat(rendererInfo, (const char*) glGetString(GL_VERSION));
    glfwSetWindowTitle(window, rendererInfo);

    init(fileName);

    glfwSetKeyCallback(window, keyboard);
    glfwSetMouseButtonCallback(window, mouse);
    glfwSetWindowSizeCallback(window, reshape);

    reshape(window, gWidth, gHeight); // need to call this once ourselves
    mainLoop(window); // this does not return unless the window is closed

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}

