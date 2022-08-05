#include <iostream>
#include "hw2_output.h"
#include <pthread.h>
#include <sys/time.h>
#include <vector>
#include <string>
#include <unordered_map>
#include <unistd.h>
#include "grid.h"
#include "mutexGrid.h"

/*************************** PROTOTYPES *************************/
void *threadFunction(void*);
void *commanderFunction(void*);
/****************************************************************/
typedef struct Private{
    int gid{}; // private ID
    int si{};
    int sj{}; // area size (si x sj)
    long tg{}; // time for collecting one cigbutt (ms)
    int ng{}; // gather from this number of squares
    int ngIndex{}; // for rectangle creation, starts:0 ends: ng-1
    int which{}; // indicates which rectangle are locked now

    std::vector<std::vector< std::pair<int,int> > > rectangles;
}Private;

typedef struct SneakySmoker{
    int id{};
    int tg{};
    int cellCount{};
    std::vector<std::vector<int>> coordinates;
    int which{};
}SneakySmoker;

/************************** GLOBAL VARS *************************/
pthread_t* Tids;
pthread_t CommanderTid;
pthread_t* SneakyTids;

pthread_mutex_t LockMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t OrderMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t StopMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t ContMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t LockHelperMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t SneakyMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t SneakyStop = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t SneakyEnd = PTHREAD_MUTEX_INITIALIZER;

pthread_cond_t OrderCondition = PTHREAD_COND_INITIALIZER;
pthread_cond_t ContCondition = PTHREAD_COND_INITIALIZER;
pthread_cond_t LockCondition = PTHREAD_COND_INITIALIZER;
pthread_cond_t SneakyCondition = PTHREAD_COND_INITIALIZER;
pthread_cond_t SneakyStopCondition = PTHREAD_COND_INITIALIZER;

int Break = 0;
int Stop = 0;
int CommandBarrier = 0;
int Lock = 0;


Grid CigButtGrid;
MutexGrid MtxGrid;
MutexGrid SneakyGrid;

long PrivSize;
long SneakyCount = 0;
std::vector<Private*> Privates;
std::vector<SneakySmoker*> SneakySmokers;
std::unordered_map<int,pthread_t> ThreadsForPrivates;
std::vector<std::pair<int,std::string>> Orders;
/***************************************************************/



void *threadFunction(void *ptr){
    auto *current = (Private*)ptr;
    hw2_notify(PROPER_PRIVATE_CREATED,current->gid,0,0); // notify that a proper private has been created


    unsigned long size = current->rectangles.size();


    for(auto i = 0; i < size; i++) {
        /***
         * firstly, locks down an area
         * secondly, gathers all cigarette butts in that area
         * then leaves the area
         * this loop continues while all areas, that a private is responsible from, are cleaned.
         */
        afterOrder:
        int which = current->which;
        std::vector<std::pair<int, int>> rect = current->rectangles[which];
        auto rectSize = rect.size();

        /** lock down area */
        pthread_mutex_lock(&LockMutex);
        for (unsigned long j = 0; j < rectSize; j++) {
            int x = rect[j].first;
            int y = rect[j].second;

            int rw = pthread_mutex_trylock(&MtxGrid.mutexes[x][y]);

            if(rw == EBUSY){
                for(long k = j-1 ; k >= 0; k--){
                    int xs = rect[k].first;
                    int ys = rect[k].second;
                    pthread_mutex_unlock(&MtxGrid.mutexes[xs][ys]);
                }
                pthread_mutex_unlock(&LockMutex);

                pthread_mutex_lock(&LockHelperMutex);
                pthread_cond_wait(&LockCondition,&LockHelperMutex);
                pthread_mutex_unlock(&LockHelperMutex);
                // order wait
                if (Break == 1) {
                    pthread_mutex_lock(&ContMutex);
                    CommandBarrier++;
                    hw2_notify(PROPER_PRIVATE_TOOK_BREAK,current->gid,0,0);
                    pthread_cond_broadcast(&LockCondition);
                    pthread_cond_wait(&ContCondition,&ContMutex);
                    if(Stop == 1){
                        pthread_mutex_lock(&StopMutex);
                        hw2_notify(PROPER_PRIVATE_STOPPED,current->gid,0,0);
                        pthread_mutex_unlock(&StopMutex);
                        pthread_mutex_unlock(&ContMutex);
                        pthread_mutex_unlock(&LockMutex);
                        goto end;
                    }

                    hw2_notify(PROPER_PRIVATE_CONTINUED,current->gid,0,0);
                    pthread_mutex_unlock(&ContMutex);
                    pthread_mutex_unlock(&LockMutex);
                    goto afterOrder;
                }
                else if(Stop == 1){

                    pthread_mutex_lock(&StopMutex);
                    CommandBarrier++;
                    hw2_notify(PROPER_PRIVATE_STOPPED,current->gid,0,0);
                    pthread_mutex_unlock(&StopMutex);
                    pthread_mutex_unlock(&LockMutex);
                    goto end;
                }
                pthread_mutex_unlock(&LockMutex);
                goto afterOrder;
            }

        }
        hw2_notify(PROPER_PRIVATE_ARRIVED, current->gid, rect[0].first, rect[0].second);
        pthread_mutex_unlock(&LockMutex);
        /** end of lock down */

        /** gatherCigButtsInAnArea */
        long tm = current->tg;
        int rc;

        for (unsigned long j = 0; j < rectSize; j++) {
            int x = rect[j].first;
            int y = rect[j].second;
            bool isEmpty = CigButtGrid.map[x][y] == 0;

            // while there are cigarette butts, collect them

            while (!isEmpty) {
                struct timeval tv{0, 0};
                gettimeofday(&tv, nullptr);
                struct timespec ts{0, 0};

                ts.tv_sec = (tm / 1000) + tv.tv_sec;
                ts.tv_nsec = ((tm % 1000) * 1000000) + (tv.tv_usec * 1000);
                if (ts.tv_nsec >= 1000000000) {
                    ts.tv_nsec -= 1000000000;
                    ts.tv_sec++;
                }
                // order wait
                pthread_mutex_lock(&OrderMutex);
                rc = pthread_cond_timedwait(&OrderCondition, &OrderMutex, &ts);
                pthread_mutex_unlock(&OrderMutex);

                // order came
                if (rc == 0) {
                    if (Break == 1) {
                        for(unsigned long k = 0 ; k < rectSize; k++){
                            int a = rect[k].first;
                            int b = rect[k].second;
                            pthread_mutex_unlock(&MtxGrid.mutexes[a][b]);
                        }

                        pthread_mutex_lock(&ContMutex);
                        CommandBarrier++;
                        hw2_notify(PROPER_PRIVATE_TOOK_BREAK,current->gid,0,0);
                        pthread_cond_broadcast(&LockCondition);
                        pthread_cond_wait(&ContCondition,&ContMutex);
                        if(Stop == 1){
                            pthread_mutex_lock(&StopMutex);
                            hw2_notify(PROPER_PRIVATE_STOPPED,current->gid,0,0);
                            pthread_mutex_unlock(&StopMutex);
                            pthread_mutex_unlock(&ContMutex);
                            goto end;
                        }

                        hw2_notify(PROPER_PRIVATE_CONTINUED,current->gid,0,0);
                        pthread_mutex_unlock(&ContMutex);
                        goto afterOrder;
                    }
                    else if(Stop == 1){
                        pthread_cond_broadcast(&LockCondition);
                        pthread_mutex_lock(&StopMutex);
                        CommandBarrier++;
                        hw2_notify(PROPER_PRIVATE_STOPPED,current->gid,0,0);
                        pthread_mutex_unlock(&StopMutex);
                        goto end;
                    }
                }

                hw2_notify(PROPER_PRIVATE_GATHERED, current->gid, x, y);
                CigButtGrid.map[x][y]--;

                isEmpty = CigButtGrid.map[x][y] == 0;

            }
            /** end of collection! */
        }
        /** private will unlock the area */
        for(unsigned long k = 0 ; k < rectSize; k++){
            int a = rect[k].first;
            int b = rect[k].second;
            pthread_mutex_unlock(&MtxGrid.mutexes[a][b]);
        }
        pthread_cond_broadcast(&LockCondition);
        hw2_notify(PROPER_PRIVATE_CLEARED, current->gid, 0, 0);

        current->which++; // increment which : private will lock-gather-leave for the next

    }


    hw2_notify(PROPER_PRIVATE_EXITED,current->gid,0,0);

    end:
    PrivSize--;
    pthread_exit(nullptr);

}

void* commanderFunction(void* arg){
    unsigned long size = Orders.size();

    for(int i = 0; i < size ; i++){
        if(i == 0){
            long ms = Orders[0].first;
            std::string orderName = Orders[0].second;
            usleep(ms*1000);

            if(orderName == "break"){
                hw2_notify(ORDER_BREAK,0,0,0);
                Break = 1;
                Stop = 0;
                while(CommandBarrier < PrivSize) {
                    pthread_cond_broadcast(&OrderCondition);
                }
                CommandBarrier = 0;
            }
            else if(orderName == "continue"){
                hw2_notify(ORDER_CONTINUE,0,0,0);
                Break = 0;
                Stop = 0;
                pthread_cond_broadcast(&ContCondition);
            }
            else{
                hw2_notify(ORDER_STOP,0,0,0);
                Stop = 1;
                if(Break == 1){
                    pthread_cond_broadcast(&ContCondition);
                }
                while(CommandBarrier < PrivSize + SneakyCount){
                    pthread_cond_broadcast(&SneakyStopCondition);
                    pthread_cond_broadcast(&OrderCondition);
                }
            }
        }

        else{
            long ms = Orders[i-1].first;
            std::string orderName = Orders[i].second;
            long nextMs = Orders[i].first - ms;
            usleep(nextMs*1000);

            if(orderName == "break"){
                hw2_notify(ORDER_BREAK,0,0,0);
                Break = 1;
                Stop = 0;
                while(CommandBarrier < PrivSize) {
                    pthread_cond_broadcast(&OrderCondition);
                }
                CommandBarrier = 0;
            }
            else if(orderName == "continue"){
                hw2_notify(ORDER_CONTINUE,0,0,0);
                Break = 0;
                Stop = 0;
                pthread_cond_broadcast(&ContCondition);
            }
            else{
                hw2_notify(ORDER_STOP,0,0,0);
                Stop = 1;
                if(Break == 1){
                    pthread_cond_broadcast(&ContCondition);
                }
                while(CommandBarrier < PrivSize + SneakyCount){
                    pthread_cond_broadcast(&SneakyStopCondition);
                    pthread_cond_broadcast(&OrderCondition);
                }
            }


        }
    }
    pthread_exit(nullptr);
}

void* sneakyFunction(void* arg){
    auto *current = (SneakySmoker *)arg;
    hw2_notify(SNEAKY_SMOKER_CREATED,current->id,0,0); // notify that a proper private has been created

    auto size = current->cellCount;

    for(auto i = 0; i < size; i++) {
        /***
         * firstly, locks down an area
         * secondly, smokes
         * then leaves the area
         */
        after:
        pthread_mutex_lock(&LockMutex);

        int x = current->coordinates[current->which][0];
        int y = current->coordinates[current->which][1];
        int cigarCount = current->coordinates[current->which][2];

        // try to lock SneakyGrid
        int canLocked = pthread_mutex_trylock(&SneakyGrid.mutexes[x][y]);
        // if cannot lock, then wait for signal to lock it !
        if(canLocked == EBUSY){
            pthread_mutex_unlock(&LockMutex);

            pthread_mutex_lock(&SneakyMutex);
            pthread_cond_wait(&SneakyCondition,&SneakyMutex);
            pthread_mutex_unlock(&SneakyMutex);
        }


        hw2_notify(SNEAKY_SMOKER_ARRIVED,current->id,x,y);
        pthread_mutex_unlock(&LockMutex);

        int xs = x-1;
        int ys = y-1;
        auto tm = current->tg;
        for(int j = 0 ; j < cigarCount; j++){
                if(xs == x && ys == y){
                    ys++;
                    j--;
                    continue;
                }
                struct timespec ts{0, 0};
                struct timeval tv{0, 0};
                gettimeofday(&tv, nullptr);
                ts.tv_sec = (tm / 1000) + tv.tv_sec;
                ts.tv_nsec = ((tm % 1000) * 1000000) + (tv.tv_usec * 1000);
                if (ts.tv_nsec >= 1000000000) {
                    ts.tv_nsec -= 1000000000;
                    ts.tv_sec++;
                }

                // order wait
                pthread_mutex_lock(&SneakyStop);
                int rc = pthread_cond_timedwait(&SneakyStopCondition, &SneakyStop, &ts);
                pthread_mutex_unlock(&SneakyStop);
                if(rc == 0){
                    if(Stop == 1){
                        pthread_mutex_lock(&SneakyEnd);
                        CommandBarrier++;
                        hw2_notify(SNEAKY_SMOKER_STOPPED,current->id,0,0);
                        pthread_mutex_unlock(&SneakyEnd);
                        goto end;
                    }
                }

                CigButtGrid.litterACigButt(xs,ys);

                hw2_notify(SNEAKY_SMOKER_FLICKED,current->id,xs,ys);

                ys++;
                if(ys == y + 2){
                    ys = y-1;
                    xs++;
                }
                if(xs == x + 2){
                    xs = x-1;
                }
        }
        for(int k = -1; k < 2 ; k++){
            for(int q = -1; q < 2; q++) {
                pthread_mutex_unlock(&MtxGrid.mutexes[x + k][y + k]);
            }
        }
        pthread_mutex_unlock(&SneakyGrid.mutexes[x][y]);
        pthread_cond_broadcast(&SneakyCondition);
        hw2_notify(SNEAKY_SMOKER_LEFT, current->id, 0, 0);

        current->which++; // increment which : private will lock-gather-leave for the next

    }
    SneakyCount--;

    hw2_notify(SNEAKY_SMOKER_EXITED,current->id,0,0);
    end:
    pthread_exit(nullptr);
}


int main(){
    // call hw2_notifier to create output!
    hw2_init_notifier();

    // inputs of layers
    int r, c;
    int cigbuttNumber;
    int x,y; // for gather area

    std::cin >> r; // row size
    std::cin >> c; // col size

    CigButtGrid.setSize(r,c);
    MtxGrid.setSize(r,c);
    SneakyGrid.setSize(r,c);

    for(int i = 0; i < r; i++){
        for(int j = 0; j < c; j++){
            std::cin >> cigbuttNumber;
            CigButtGrid.setOneSquare(i, j, cigbuttNumber); // load Grid
        }
    }

    std::cin >> PrivSize; // how many Privates (threads)
    // create pthread ids
    Tids = new pthread_t[PrivSize];

    // take input of the variables of each private
    for(int i = 0; i < PrivSize; i++){
        // create private and push it to the vector
        auto *priv = new Private;
        std::cin >> priv->gid;
        std::cin >> priv->si;
        std::cin >> priv->sj;
        std::cin >> priv->tg;
        std::cin >> priv->ng;
        priv->rectangles.resize(priv->ng);

        // areas to gather from
        for(int j = 0 ; j < priv->ng; j++){
            std::cin >> x;
            std::cin >> y;
            for(int k = 0 ; k < priv->si; k++){
                for(int m = 0 ; m < priv->sj; m++){
                    priv->rectangles[priv->ngIndex].emplace_back(x+k,y+m);
                }
            }
            priv->ngIndex++;
        }
        Privates.push_back(priv);
    }
    std::cin >> std::ws;
    // TODO: Input handle!
    if(!std::cin.eof()) {
        std::string check;
        int count;
        int ms;
        bool flag = true;
        std::string orderName;
        std::cin >> count;

        std::cin >> std::ws;

        getline(std::cin, check);
        if (check.find("break") != std::string::npos) {
            orderName = "break";
            flag = false;
        }
        else if (check.find("continue") != std::string::npos) {
            orderName = "continue";
            flag = false;
        }
        else if (check.find("stop") != std::string::npos) {
            orderName = "stop";
            flag = false;
        }
        // then input for second part
        if (!flag) {
            std::string temp;
            for (char ch: check) {
                if (ch == ' ') break;
                temp.push_back(ch);
            }
            int tempMs = std::stoi(temp);
            Orders.emplace_back(tempMs, orderName);

            for (int i = 1; i < count; i++) {
                std::cin >> ms;
                std::cin >> orderName;
                Orders.emplace_back(ms, orderName);
            }
        } else {
            SneakyCount = count;
            SneakyTids = new pthread_t[SneakyCount];
            std::string temp[3];
            int index=0;
            for (char ch: check) {
                if (ch == ' ') {
                    index++;
                    continue;
                }
                temp[index].push_back(ch);
            }
            int arr[3] = {std::stoi(temp[0]),std::stoi(temp[1]),std::stoi(temp[2])};
            auto *tempSmoker = new SneakySmoker;
            SneakySmokers.push_back(tempSmoker);
            tempSmoker->id = arr[0];
            tempSmoker->tg = arr[1];
            tempSmoker->cellCount = arr[2];
            tempSmoker->coordinates.resize(tempSmoker->cellCount);
            for(int j = 0 ; j < tempSmoker->cellCount; j++){
                tempSmoker->coordinates[j].resize(3);
                std::cin >> tempSmoker->coordinates[j][0];
                std::cin >> tempSmoker->coordinates[j][1];
                std::cin >> tempSmoker->coordinates[j][2];
            }
            for (int i = 1; i < SneakyCount; i++) {
                auto *smoker = new SneakySmoker;
                SneakySmokers.push_back(smoker);
                std::cin >> smoker->id;
                std::cin >> smoker->tg;
                std::cin >> smoker->cellCount;
                smoker->coordinates.resize(smoker->cellCount);
                for (int j = 0; j < smoker->cellCount; j++) {
                    smoker->coordinates[j].resize(3);
                    std::cin >> smoker->coordinates[j][0];
                    std::cin >> smoker->coordinates[j][1];
                    std::cin >> smoker->coordinates[j][2];
                }
            }
        }
    }

    if(!std::cin.eof()){
        std::cin >> SneakyCount;
        SneakyTids = new pthread_t[SneakyCount];

        for(int i = 0 ; i < SneakyCount; i++){
            auto * smoker = new SneakySmoker;
            SneakySmokers.push_back(smoker);
            std::cin >> smoker->id;
            std::cin >> smoker->tg;
            std::cin >> smoker->cellCount;
            smoker->coordinates.resize(smoker->cellCount);
            for(int j = 0 ; j < smoker->cellCount; j++){
                smoker->coordinates.resize(3);
                smoker->coordinates[j].resize(3);
                std::cin >> smoker->coordinates[j][0];
                std::cin >> smoker->coordinates[j][1];
                std::cin >> smoker->coordinates[j][2];
            }
        }
    }


    /*** start threads and simulation!
    * if there is no order, do not create a commander!
    ***/

    /* create commander */
    pthread_create(&CommanderTid,nullptr,&commanderFunction,nullptr);

    /* create privates */
    unsigned long size = Privates.size();
    for(unsigned long i = 0 ; i < size; i++){
        Private * currentPriv = Privates[i];

        pthread_create(&Tids[i], nullptr, &threadFunction, currentPriv);
        ThreadsForPrivates[currentPriv->gid] = Tids[i];
    }

    long SneakySize = SneakyCount;
    for(auto i = 0 ; i < SneakyCount; i++){
        pthread_create(&SneakyTids[i], nullptr,&sneakyFunction, SneakySmokers[i]);
    }


    /* wait threads done */
    for(auto & Private : Privates){
        pthread_join(ThreadsForPrivates[Private->gid],nullptr);
    }

    for(int i = 0 ; i < SneakySize; i++){
        pthread_join(SneakyTids[i],nullptr);
    }
    pthread_join(CommanderTid,nullptr);
    // exiting

    pthread_mutex_destroy(&LockMutex);
    pthread_mutex_destroy(&OrderMutex);
    pthread_mutex_destroy(&ContMutex);
    pthread_mutex_destroy(&StopMutex);
    pthread_cond_destroy(&OrderCondition);
    pthread_cond_destroy(&ContCondition);
    delete [] Tids;
    return 0;
}