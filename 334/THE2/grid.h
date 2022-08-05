#ifndef GRID_H
#define GRID_H

#include <vector>
// Grid class to store Grid size and Grid itself.
class Grid{
public:

    void setOneSquare(const int & row, const int & col, const int & cigbuttNumber){
        map[row][col] = cigbuttNumber;
    }
    void setSize(const int &rowCount, const int &colCount){
        map.resize(rowCount);
        for(int i = 0 ; i < rowCount; i++){
            map[i].resize(colCount);
        }
    }

    void litterACigButt(const int &x, const int& y){
        map[x][y]++;
    }



    std::vector< std::vector< int > > map;
};

#endif //GRID_H
