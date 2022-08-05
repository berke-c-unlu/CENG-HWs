#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/wait.h>
#include "parser.h"

#include <sys/stat.h>
#include <fcntl.h>

#define MAX_INPUT_SIZE 256
#define TRUE 1

typedef struct Bundle{
    char* name; // bundle name
    char*** processes; // processes[] = argv

    char* output;
    char* input;

    int sizeOfThree;
    int sizeOfTwo;

    int countOfProcesses;

}Bundle;

/* doubles size of bundles and doubles the size of the integer */
void doubleSize(Bundle* bundles, int* size){
    *size = *size * 2;
    bundles = realloc(bundles,*size * sizeof(Bundle));
}

/* constructor for bundle */
void setBundle(Bundle* bundle){
    bundle->sizeOfThree = 10;
    bundle->sizeOfTwo = 10;

    bundle->processes = (char***)malloc(sizeof(char**)*10); // initially 10
    for(int i = 0 ; i < 10 ; i++){
        bundle->processes[i] = (char**)malloc(sizeof (char*)*10); // initially 10
    }
}

/* doubles the size of ***process or **processes */
void doubleSizeOfBundle(Bundle* bundle, int threeORtwo){
    //three pointer case
    if(threeORtwo == 0){
        int temp = bundle->sizeOfThree * 2;
        bundle->processes = realloc(bundle->processes,temp* sizeof(bundle->processes));

        for(int i = bundle->sizeOfThree ; i < (bundle->sizeOfThree << 1) ; i++){
            bundle->processes[i] = (char**)malloc(sizeof (char*)*10); // initially 10
        }

        bundle->sizeOfThree = temp;
        return;
    }
        //two pointer case
    else if (threeORtwo == 1){
        bundle->sizeOfTwo = bundle->sizeOfTwo << 1;
        for(int i = 0 ; i < bundle->sizeOfThree ; i++){
            bundle->processes[i] = realloc(bundle->processes[i] ,bundle->sizeOfTwo*sizeof(char*));
        }
        return;
    }
}

/* it will find the corresponding bundles will be executed */
Bundle* findBundles(bundle_execution* bundle_exec, Bundle* bundles, int bundleCnt, int execCnt){
    Bundle* ret = (Bundle*)malloc(sizeof(Bundle)*execCnt);

    // allocate memory for every bundle, since we will copy them from bundles
    for(int i = 0 ; i < execCnt; i++){
        setBundle(&ret[i]);
    }

    int indexOfRet = 0;

    for(int i = 0 ; i < execCnt; i++){
        for(int j = 0 ; j < bundleCnt; j++){
            char* bundleName = bundles[j].name;
            char* execName = bundle_exec[i].name;
            /* if found add it to list */
            if(strcmp(bundleName,execName) == 0){
                ret[indexOfRet] = bundles[j];
                if(bundle_exec[i].input != NULL){
                    ret[indexOfRet].input = strdup(bundle_exec[i].input);
                }
                else{
                    ret[indexOfRet].input = NULL;
                }
                if(bundle_exec[i].output != NULL){
                    ret[indexOfRet].output = strdup(bundle_exec[i].output);
                }
                else{
                    ret[indexOfRet].output = NULL;
                }
                indexOfRet++;
                break; // dont waste time since bundles are unique
            }
        }
    }
    return ret;
}

/* execute bundles */
void executeBundles(bundle_execution* bundle_exec, Bundle* bundles, int bundleCnt, int execCnt){
    /***
     * firstly execute first bundle
     * then for loop
     * inside the for loop execute repeater
     * after execution of repeater execute next bundle
     * if it is last bundle
     */

    Bundle* willBeExecuted = findBundles(bundle_exec,bundles,bundleCnt,execCnt);

    int pipes[execCnt-1][2];
    // construct pipes
    // we need n-1 pipes (n : bundle count)
    for(int i = 0 ; i < execCnt - 1; i++){
        pipe(pipes[i]);
    }

    pid_t pidF;
    // first bundle execution
    if((pidF = fork()) == 0){
        char*** processes = willBeExecuted[0].processes;
        int size = willBeExecuted[0].countOfProcesses;
        if(willBeExecuted[0].input == NULL){
            for(int i = 0 ; i < size; i++){

                char** process = processes[i];
                if(fork() == 0){
                    close(pipes[0][0]);
                    dup2(pipes[0][1],STDOUT_FILENO);
                    close(pipes[0][1]);

                    execvp(process[0],process);
                }
            }
            // wait childs
            while(wait(NULL) > 0);
            exit(0);
        }
        else{
            for(int i = 0 ; i < size; i++){
                char** process = processes[i];

                if(fork() == 0){
                    int fd;
                    if((fd = open(willBeExecuted[0].input,O_RDONLY,0777)) < 0){
                        perror("cant open file");
                        exit(0);
                    } // open output file

                    dup2(fd,STDIN_FILENO); // stdin to input file!
                    close(fd);
                    close(pipes[0][0]);
                    dup2(pipes[0][1],STDOUT_FILENO);
                    close(pipes[0][1]);

                    execvp(process[0],process);
                }
            }
            // wait childs
            while(wait(NULL) > 0);
            exit(0);
        }
    }
    else{
        close(pipes[0][1]);
        waitpid(pidF,NULL,0);
    }

    for(int indexOfBundles = 1; indexOfBundles < execCnt; indexOfBundles++) {
        // repater
        char ***processes = willBeExecuted[indexOfBundles].processes;
        int size = willBeExecuted[indexOfBundles].countOfProcesses;

        int repeaterPipes[size][2];
        for(int i = 0 ; i < size; i++){
            pipe(repeaterPipes[i]);
        }

        int cap = 1024;
        char* buffer = (char*)malloc(sizeof(char)*cap);

        int z = 0; // index
        ssize_t n;
        char c;
        pid_t pidR;
        if((pidR = fork()) == 0){
            close(pipes[indexOfBundles-1][1]);
            dup2(pipes[indexOfBundles-1][0],STDIN_FILENO);
            close(pipes[indexOfBundles-1][0]);


            for(int i = 0 ; i < size ; i++){
                close(repeaterPipes[i][0]);
            }
            while(TRUE){
                n = read(STDIN_FILENO, &c, 1);
                if(n < 1) break;
                if (z == cap) {
                    cap *= 2;
                    buffer = realloc(buffer, cap);
                }
                buffer[z++] = c;
            }
            buffer[z] = '\0';

            for(int i = 0; i < size; i++){
                write(repeaterPipes[i][1],buffer,strlen(buffer)); // write buffer to pipes
                close(repeaterPipes[i][1]);
            }
            exit(0);
        }
        else{ // parent of repeater
            // close main pipe
            close(pipes[indexOfBundles-1][0]);
            for(int i  = 0 ; i < size; i++){
                close(repeaterPipes[i][1]);
            }
            waitpid(pidR,NULL,0);
            free(buffer);
            buffer = NULL;
        }


        if(indexOfBundles != execCnt - 1){
            if(fork() == 0) {
                for (int i = 0; i < size; i++) {
                    char **process = processes[i];
                    if (fork() == 0) {

                        close(repeaterPipes[i][1]);
                        dup2(repeaterPipes[i][0], STDIN_FILENO);
                        close(repeaterPipes[i][0]);

                        close(pipes[indexOfBundles][0]);
                        dup2(pipes[indexOfBundles][1], STDOUT_FILENO);
                        close(pipes[indexOfBundles][1]);

                        execvp(process[0], process);
                    }
                }
                for(int i = 0 ; i < size; i++) {
                    close(repeaterPipes[i][0]);
                }
                close(pipes[indexOfBundles][1]);
                // wait childs
                while (wait(NULL) > 0);
                exit(0);
            }
            else{
                for(int i = 0 ; i < size; i++) {
                    close(repeaterPipes[i][0]);
                }
                close(pipes[indexOfBundles][1]);
                wait(NULL);
            }
        }

            //last bundle
        else{
            pid_t pidO;
            int fd;
            if((pidO = fork()) == 0){
                if(willBeExecuted[indexOfBundles].output == NULL){
                    for (int i = 0; i < size; i++) {
                        char **process = processes[i];
                        if (fork() == 0) {

                            close(repeaterPipes[i][1]);
                            dup2(repeaterPipes[i][0], STDIN_FILENO);
                            close(repeaterPipes[i][0]);

                            execvp(process[0], process);
                        }
                    }
                    // wait childs
                    for(int i = 0 ; i < size; i++){
                        close(repeaterPipes[i][0]);
                        close(repeaterPipes[i][1]);
                    }
                    while(wait(NULL) > 0);
                    exit(0);
                }
                else{
                    if((fd = open(willBeExecuted[indexOfBundles].output,O_WRONLY | O_CREAT | O_APPEND ,0777)) < 0){
                        perror("cant open file");
                        exit(0);
                    } // open output file

                    for (int i = 0; i < size; i++) {
                        char **process = processes[i];

                        if (fork() == 0) {

                            dup2(fd,STDOUT_FILENO);
                            close(fd);

                            close(repeaterPipes[i][1]);
                            dup2(repeaterPipes[i][0], STDIN_FILENO);
                            close(repeaterPipes[i][0]);

                            execvp(process[0], process);
                        }
                    }
                    for(int i = 0 ; i < size; i++){
                        close(repeaterPipes[i][0]);
                        close(repeaterPipes[i][1]);
                    }
                    close(fd);
                    while(wait(NULL) > 0);
                    exit(0);
                }
            }
            else{
                for(int i = 0 ; i < size; i++){
                    close(repeaterPipes[i][0]);
                    close(repeaterPipes[i][1]);
                }
                waitpid(pidO,NULL,0);
            }
        }
    }
}




void executeBundleWithSizeOne(bundle_execution* bundle_exec, Bundle* bundle){
    bundle_execution* ptr = bundle_exec;

    // if input is a file
    if(ptr->input != NULL){
        // if output is a file
        if(ptr->output != NULL){
            char* inputFilePath = ptr->input;
            char* outputFilePath = ptr->output;

            int fdOut;
            int fd;

            int count = bundle->countOfProcesses;

            if((fdOut = open(outputFilePath,O_WRONLY | O_CREAT | S_IRUSR | S_IWUSR | O_APPEND ,0777)) < 0){
                perror("cant open file");
                exit(0);
            } // open output file

            // fork n times (n is process count)
            for(int i = 0 ; i < count; i++){
                char*** processes = bundle->processes; // processes
                char** processPtr = processes[i]; // one process
                // EXAMPLE : processPtr = ["echo","berke"]
                // processPtr[0] = "echo"
                // args = ["berke"]

                if(fork() == 0){
                    if((fd = open(inputFilePath,O_RDONLY,0)) < 0){
                        perror("cant open file");
                        exit(0);
                    } // open output file

                    dup2(fd,STDIN_FILENO); // stdin to input file!
                    dup2(fdOut,STDOUT_FILENO); // stdout to output file
                    close(fdOut); // close fd
                    close(fd); // close fd
                    execvp(processPtr[0],processPtr);
                }
            }
            close(fdOut);
            while(wait(NULL) > 0);
        }

            // if output is stdout
        else {

            char *inputFilePath = ptr->input;

            int count = bundle->countOfProcesses;

            // fork n times (n is process count)
            for (int i = 0; i < count; i++) {
                char ***processes = bundle->processes; // processes
                char **processPtr = processes[i]; // one process
                // EXAMPLE : processPtr = ["echo","berke"]
                // processPtr[0] = "echo"
                // args = ["berke"]

                if (fork() == 0) {
                    int fd;
                    if ((fd = open(inputFilePath, O_RDONLY, 0)) < 0) {
                        perror("cant open file");
                        exit(0);
                    } // open output file
                    dup2(fd, STDIN_FILENO); // stdin to input file!
                    close(fd); // close fd
                    execvp(processPtr[0], processPtr);
                }
            }
            while(wait(NULL) > 0);

        }

    }

        // if input is stdin
    else{
        // if output is a file
        if(ptr->output != NULL){

            int fdOut = 0;
            char* outputFilePath = ptr->output;
            int count = bundle->countOfProcesses;

            if ((fdOut = open(outputFilePath, O_WRONLY | O_CREAT | S_IRUSR | S_IWUSR | O_APPEND, 0)) < 0) {
                perror("cant open file");
                exit(0);
            } // open output file

            // fork n times (n is process count)
            for (int i = 0; i < count; i++) {
                char ***processes = bundle->processes; // processes
                char **processPtr = processes[i]; // one process
                // EXAMPLE : processPtr = ["echo","berke"]
                // processPtr[0] = "echo"
                // args = ["berke"]


                if (fork() == 0) {
                    dup2(fdOut, STDOUT_FILENO); // stdout to output file
                    close(fdOut);
                    execvp(processPtr[0], processPtr);
                }
            }
            close(fdOut);
            while(wait(NULL) > 0);
        }

            /* this part is working currently */
            // if output is stdout
        else{

            int count = bundle->countOfProcesses;

            // fork n times (n is process count)
            for(int i = 0 ; i < count; i++){
                char*** processes = bundle->processes; // processes
                char** processPtr = processes[i]; // one process
                // EXAMPLE : processPtr = ["echo","berke"]
                // processPtr[0] = "echo"
                // args = ["berke"]

                if(fork() == 0){
                    execvp(processPtr[0],processPtr);
                }

            }
            while(wait(NULL) > 0);
        }
    }
}

int main() {
    int sizeOfBundles = 20;
    int* sizeptr = &sizeOfBundles;
    Bundle* bundles = (Bundle*)malloc(sizeof(Bundle)*20); // initially size of 20
    int indexOfBundles = 0;

    /* set bundles */
    for(int i = 0 ; i < sizeOfBundles ; i++){
        setBundle(&bundles[i]);
    }

    int indexOfSingle = 0;
    while (TRUE) {
        char buf[MAX_INPUT_SIZE]; // buffer for input
        memset(buf,0,sizeof(char)*MAX_INPUT_SIZE);

        int is_bundle_creation = 0;
        parsed_input *parsed = (parsed_input *) malloc(sizeof(parsed_input));

        fgets(buf,MAX_INPUT_SIZE,stdin);
        strcat(buf,"\n\0");
        parse(buf, is_bundle_creation, parsed); // parse

        /* input is taken and ready to process */

        /* if quit has given as input, quit the bshell */
        if (parsed->command.type == QUIT) {

            return 0;
        }

            /* if bundle create */
        else if (parsed->command.type == PROCESS_BUNDLE_CREATE) {


            /* bundle has already been created, we gave it a name */
            /* check whether or not there is space , if not double the size */
            if(indexOfBundles == sizeOfBundles){
                doubleSize(bundles,sizeptr);
            }
            bundles[indexOfBundles].name = strdup(parsed->command.bundle_name);

            is_bundle_creation = 1; // set it 1 since we are creating a bundle right now

            bundles[indexOfBundles].countOfProcesses = 0; // set count of processes

            memset(buf,0,sizeof(char)*MAX_INPUT_SIZE); // reset buffer;

            /*** in this loop we will take input of processes
             * take input
             * process is in char** argv
             * copy it into processes part of the corresponding bundle
             * then continue
             * if current input is "pbs" stop
            ***/
            int p = 0; // index for bundles' processes

            while(TRUE){

                fgets(buf,MAX_INPUT_SIZE,stdin); // take input
                strcat(buf,"\n\0");
                parse(buf,is_bundle_creation,parsed); // parse it

                // if pbs comes an input stop creation of bundle
                if(parsed->command.type == PROCESS_BUNDLE_STOP) {
                    is_bundle_creation = 0;
                    break;
                }

                /* if processes is full, double the size */
                if(p == bundles[indexOfBundles].sizeOfThree){
                    doubleSizeOfBundle(&bundles[indexOfBundles],0);
                }
                int i = 0;
                char** arg = parsed->argv;
                while(arg[i] != NULL){

                    bundles[indexOfBundles].processes[p][i] = strdup(arg[i]);
                    i++;
                }
                p++;
                bundles[indexOfBundles].countOfProcesses++; // increment process counter
            }
            indexOfBundles++;
        }

            /* if execution command of a bundle comes */

        else if(parsed->command.type == PROCESS_BUNDLE_EXECUTION){
            bundle_execution* currentExecution = parsed->command.bundles;
            int size = parsed->command.bundle_count;


            // now we should execute the bundle
            // firstly one bundle check

            if(size == 1){
                Bundle* b = findBundles(currentExecution,bundles,sizeOfBundles,size);
                executeBundleWithSizeOne(currentExecution, b);
            }
                // execute corresponding bundles together
            else{
                executeBundles(currentExecution, bundles, indexOfBundles, size);
            }
        }
    }


    return 0;
}

