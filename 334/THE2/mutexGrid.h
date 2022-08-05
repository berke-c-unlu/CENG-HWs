#ifndef MUTEXGRID_H
#define MUTEXGRID_H

#include <vector>
#include <pthread.h>
#include <semaphore.h>
#include <string>

class MutexGrid{
public:
    void setSize(const int &row, const int &col){
        mutexes.resize(row);
        for(int i = 0 ; i < row; i++){
            for(int j = 0 ; j < col; j++){
                pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
                pthread_mutex_init(&mutex,nullptr);
                mutexes[i].push_back(mutex);
            }
        }
    }

    // mutex Grid (r x c)

    std::vector<std::vector<pthread_mutex_t>> mutexes; // key : private id
};


#endif //MUTEXGRID_H
