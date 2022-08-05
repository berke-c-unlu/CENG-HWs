#include <iostream>
#include <string.h>
#include <string>
#include <vector>
#include <sys/mman.h>
#include <fcntl.h>
#include <cmath>
#include "fat32.h"
#include "parser.h"


#define MAXINPUTSIZE 65536
#define ROOT_CLUSTER 2
#define EOC 0xFFFFFF8
#define LS_DIR_PERM "drwx------ 1 root root 0 "
#define LS_FILE_PERM "-rwx------ 1 root root "

uint32_t Current_directory_cluster;
uint32_t Parent_directory_cluster;
uint32_t First_data_sector;
uint32_t First_fat_sector;
std::string currentDir;
std::vector<std::string> Months;

/*** PROTOTYPES ***/
void fill_bpb_struct(FILE*, BPB_struct*);
void executeCommand(FILE*, parsed_input *,BPB_struct *);
void printCurrentDir();
void parse_path(char*,std::vector<std::string> &);
void closeFile(FILE*);
unsigned char lfn_checksum(const unsigned char *);
void writeMSDOSName(std::string &,std::string &, std::string &);
void fillMSDOS(std::string & , bool , FatFileEntry & );
void fillLFN(std::string & , bool , FatFileEntry & , const int &);
void createDotAndDDot(FatFileEntry & , FatFileEntry & );

std::vector<uint32_t> locate(FILE* , char*, BPB_struct *,std::vector<std::string> &);
uint32_t calculateSector(uint32_t ,BPB_struct * );
std::string constructNameOneLFN(FatFileEntry &);
std::string constructLSLFolder(const uint16_t &, const uint16_t &, const std::string &);
std::string constructLSLFile(const uint16_t &, const uint16_t &, const uint32_t&, const std::string&);


void ls(FILE*, char*, char*, std::vector<std::string>&, std::vector<uint32_t>&,BPB_struct*);
void cd(std::vector<uint32_t> ,std::vector<std::string>,char*);
void cat(FILE*, char*, char*, std::vector<std::string>&, std::vector<uint32_t>&, BPB_struct*);
void mkdir_touch(FILE*, char*, std::vector<std::string>&, std::vector<uint32_t>&,BPB_struct*, bool);

int main(int argc, char** argv) {

    FILE * imageFile;
    auto * bpbStruct = new BPB_struct;
    char * input = new char[MAXINPUTSIZE];
    auto * parsedInput = new parsed_input;


    // argv[1] for filepath
    imageFile = fopen(argv[1],"r+");
    if(imageFile == nullptr){
        fprintf(stderr,"Cannot open image file!\n");
    }

    fill_bpb_struct(imageFile, bpbStruct);

    Current_directory_cluster = ROOT_CLUSTER;
    First_fat_sector = bpbStruct->ReservedSectorCount;
    First_data_sector = bpbStruct->ReservedSectorCount + (bpbStruct->NumFATs * bpbStruct->extended.FATSize);

    Months = {"January","February","March","April","May","June","July","August","September","October","November","December"};

    while(true){
        printCurrentDir();

        std::cin.getline(input,MAXINPUTSIZE);
        parse(parsedInput,input);

        if(parsedInput->type == QUIT){
            break;
        }

        executeCommand(imageFile,parsedInput, bpbStruct);
        clean_input(parsedInput);
    }
    delete bpbStruct;
    delete parsedInput;
    delete[] input;
    closeFile(imageFile);
    return 0;
}


void executeCommand(FILE* imageFile, parsed_input * parsedInput, BPB_struct* bpb_struct){
    auto type = parsedInput->type;
    auto arg1 = parsedInput->arg1;
    auto arg2 = parsedInput->arg2;
    std::vector<std::string> pathVars;
    std::vector<uint32_t> info; // current, parent, currentSector
    long size;


    switch(type){
        case CD:
            if(arg1[0] == '.' && arg1[1] == '/'){
                arg1+=2;
            }
            parse_path(arg1,pathVars);
            info = locate(imageFile,arg1,bpb_struct,pathVars);
            cd(info, pathVars,arg1);
            break;
        case LS:
            if(arg1 && arg1[0] == '.' && arg1[1] == '/'){
                arg1+=2;
            }
            if(arg2 && arg2[0] == '.' && arg2[1] == '/') {
                arg2+=2;
            }
            ls(imageFile,arg1,arg2,pathVars,info,bpb_struct);
            break;
        case MKDIR:
            //mkdir_touch(imageFile,arg1,pathVars,info,bpb_struct, false);
            break;
        case TOUCH:
            //mkdir_touch(imageFile,arg1,pathVars,info,bpb_struct, true);
            break;
        case MV:
            break;
        case CAT:
            cat(imageFile,arg1,arg2,pathVars,info,bpb_struct);
            break;
        case QUIT:
            break;
    }
}


// if file true, if dir false
void mkdir_touch(FILE* imageFile, char* path, std::vector<std::string>& pathVars, std::vector<uint32_t>& info ,BPB_struct* bpb_struct, bool dir_or_file){
    if(path[0] == '.' && path[1] == '/'){
        path+=2;
    }
    auto len = strlen(path);
    auto size = bpb_struct->BytesPerSector * bpb_struct->extended.FATSize / 4;
    auto first = First_fat_sector* bpb_struct->BytesPerSector;
    uint32_t FAT[size];
    uint32_t current;
    uint32_t FATVal;
    int val = 0;

    parse_path(path,pathVars);
    auto llll = pathVars.size();
    std::string name = pathVars[llll-1]; // name of folder or file


    int i ;
    for(i = len-1 ; i >=0 ;i-- ){
        if(path[i] == '/'){
            break;
        }
    }
    if(i > 0){
        char newPath[i+1];
        for(int j = 0 ; j < i; j++){
            newPath[j] = path[j];
        }

        parse_path(newPath,pathVars);
        info = locate(imageFile,newPath,bpb_struct,pathVars);
        current = info[1]; // parent is current dir now!
        if(info.empty()) return;
    }
    else{
        current = Current_directory_cluster;
    }


    fseek(imageFile,first,SEEK_SET);
    for(int j = 0 ; j < size ; j++){
        fread(&FAT[j],sizeof(uint32_t),1,imageFile);
    }


    auto clusLen = bpb_struct->BytesPerSector*bpb_struct->SectorsPerCluster;
    auto currentSector = calculateSector(current,bpb_struct);
    auto currentCluster = currentSector * bpb_struct->BytesPerSector;
    uint8_t bytesOfCluster[clusLen];


    // go to parent dir's cluster
    fseek(imageFile,currentCluster,SEEK_SET);

    // read cluster
    for(int j = 0 ; j < clusLen ; j++){
        fread(&bytesOfCluster[j],sizeof(uint8_t),1,imageFile);
    }
    int j;
    // find space in this cluster
    for( j= clusLen -1 ; j >= 0; j--){
        if(bytesOfCluster[j] != 0){
            break;
        }
    }

    auto fileCount = ceil(name.length()/13.0) + 1; // lfns + 1 msdos
    auto neededSize = fileCount * sizeof(FatFileEntry);
    auto occupiedSize = bpb_struct->BytesPerSector*bpb_struct->SectorsPerCluster - j;
    auto FullSize = bpb_struct->BytesPerSector*bpb_struct->SectorsPerCluster;
    uint32_t newCluster;

    // if enough space
    int k;
    if(FullSize - occupiedSize >= neededSize){
        for(k = 0 ; k < size; k++){
            if(FAT[k] == 0){
                break;
            }
        }
        newCluster = k;
    }
    else{
        while(val != EOF){
            FATVal = FAT[current];
            FATVal &= 0x0fffffff;
            if(FATVal >= EOC){
                val = EOF;
            }
            else{
                current = FATVal;
            }

            if(val == EOF){
                for(k = 0 ; k < size; k++){
                    if(FAT[k] == 0){
                        break;
                    }
                }
                auto nextCluster = k;
                FAT[current] = nextCluster;
                FAT[nextCluster] = 0x0fffffff;
                for(k = 0 ; k < size; k++){
                    if(FAT[k] == 0){
                        break;
                    }
                }
                newCluster = k;
            }
        }
    }



    FAT[newCluster] = 0xFFFFFF8;
    auto ea = newCluster & 0xF0;
    auto firstCluster = newCluster & 0x0F;
    bool sub = false;
    FatFileEntry files[(int)fileCount];
    if(!dir_or_file){
        FatFileEntry d,dd;
        createDotAndDDot(d,dd);
        d.msdos.eaIndex = ea;
        d.msdos.firstCluster =firstCluster;
        files[0] = d;
        files[1] = dd;
        sub = true;
    }

    int seq = (int)fileCount-1;
    int p;
    if(sub) p = 2;
    else p = 0;
    for(int h = 0 ; h < name.length(); h+=13){
        std::string s = name.substr(h, 13);
        FatFileEntry f;
        fillLFN(s,dir_or_file,f,seq);
        seq--;
        files[p++] = f;
    }
    FatFileEntry msdosFile;
    fillMSDOS(name,dir_or_file,msdosFile);
    msdosFile.msdos.eaIndex = ea;
    msdosFile.msdos.firstCluster = firstCluster;
    files[p] = msdosFile;

    // write files to cluster
    currentSector = calculateSector(current,bpb_struct);
    while(j % 32 != 0){
        j++;
    }
    currentCluster = currentSector * bpb_struct->BytesPerSector+j;
    fseek(imageFile,currentCluster,SEEK_SET);
    std::cout << sizeof(FatFileEntry) << std::endl;
    for(int l = 0 ; l < fileCount; l++){
        fwrite(&files[l],sizeof(FatFileEntry),1,imageFile);
    }
}


uint16_t get_time(){
    time_t t = time(0);
    struct tm * curr = localtime( & t );
    uint16_t time = (curr->tm_hour << 11) | (curr->tm_min << 5) | (curr->tm_sec >> 1);
    return time;
}

uint16_t get_date(){
    time_t t = time(0);
    struct tm * curr = localtime( & t );
    uint16_t date = ((curr->tm_year - 80) << 9) | ((curr->tm_mon + 1) << 5) | curr->tm_mday;
    return date;
}

void writeMSDOSName(std::string &name,std::string &msdosName, std::string &extension){
    auto len = name.length();

    int i = len-1; // extension index

    // find dot
    while(i >= 0){
        if(name[i] == '.'){
            break;
        }
        i--;
    }

    // i == dot index
    // if extension exists
    if(i > 0){
        for(int j = i+1; j < i+3; j++){
            if(j < len)
                extension.push_back(name[j]);
            else
                extension.push_back(' ');
        }

    }
    else{
        extension.push_back(' ');
        extension.push_back(' ');
        extension.push_back(' ');
    }

    // if length can fit into msdos
    if(len <= 8){
        msdosName.push_back('~');
        msdosName.push_back('1');
        for(int q = 2 ; q < 8; q++){
            msdosName.push_back(' ');
        }
    }
    // capitalize and 6 = ~, 7 = 1
    else{
        for(int q = 0 ; q < 6; q++){
            msdosName.push_back(_toupper(name[q]));
        }
        msdosName.push_back('~');
        msdosName.push_back('1');
    }
}

void fillLFN(std::string & name, bool dir_or_file, FatFileEntry & lfn, const int & sequence_number){
    int q=0;
    std::string msdosName,extension;
    std::string complete = msdosName+extension;
    auto len = complete.length();
    unsigned char n[len];
    for(auto c : complete){
        n[q++] = c;
    }

    writeMSDOSName(name,msdosName,extension);
    auto checksum = lfn_checksum(n);

    int i,j=0;
    auto size = name.length();
    uint16_t name123[13];

    for(i = 0 ; i < size; i++){
        name123[i] = name[i];
    }
    name123[i++] = 0;

    while(i < 13){
        name123[i++] = -1;
    }

    for(j = 0 ; j < 5; j++){
        lfn.lfn.name1[j] = name123[j];
    }
    int k = 0;
    for(j = 5 ; j < 11; j++){
        lfn.lfn.name2[k++] = name123[j];
    }
    k = 0;
    for(j = 11 ; j < 13; j++){
        lfn.lfn.name3[k++] = name123[j];
    }

    lfn.lfn.sequence_number = sequence_number;
    lfn.lfn.reserved = 0;
    lfn.lfn.firstCluster = 0;
    lfn.lfn.attributes = 0x0f;
    lfn.lfn.checksum = checksum;


}

/* dir false, file true */
void fillMSDOS(std::string & name, bool dir_or_file, FatFileEntry & msdos){
    std::string msdosName,extension;
    writeMSDOSName(name,msdosName,extension);

    int i = 0;
    for(auto c : msdosName){
        msdos.msdos.filename[i] = c;
        i++;
    }
    i = 0;
    for(auto c : extension){
        msdos.msdos.extension[i] = c;
        i++;
    }

    if(!dir_or_file){
        msdos.msdos.attributes = 16;
        msdos.msdos.fileSize = 0;
    }
    else{
        msdos.msdos.attributes = 32;
        msdos.msdos.fileSize = 0; // CHANGE!
    }
    msdos.msdos.reserved = 0;

    msdos.msdos.creationTime = get_time();
    msdos.msdos.modifiedTime = get_time();
    msdos.msdos.creationDate = get_date();
    msdos.msdos.modifiedDate = get_date();
    msdos.msdos.lastAccessTime = get_date();

    msdos.msdos.firstCluster;
    msdos.msdos.eaIndex;
}

void createDotAndDDot(FatFileEntry & dot, FatFileEntry & doubleDot){
    dot.msdos.filename[0] = '.';
    for(int i  = 1 ; i < 8; i++){
        dot.msdos.filename[i] = ' ';
    }
    for(unsigned char & i : dot.msdos.extension){
        i = ' ';
    }
    dot.msdos.attributes = 16;
    dot.msdos.reserved = 0;
    dot.msdos.creationTime = get_time();
    dot.msdos.modifiedTime = get_time();
    dot.msdos.creationDate = get_date();
    dot.msdos.modifiedDate = get_date();
    dot.msdos.fileSize = 0;
    dot.msdos.lastAccessTime = get_date();

    dot.msdos.eaIndex;
    dot.msdos.firstCluster;


    doubleDot.msdos.filename[0] = '.';
    doubleDot.msdos.filename[1] = '.';
    for(int i  = 2 ; i < 8; i++){
        doubleDot.msdos.filename[i] = ' ';
    }
    for(unsigned char & i : dot.msdos.extension){
        i = ' ';
    }
    doubleDot.msdos.attributes = 16;
    doubleDot.msdos.reserved = 0;
    doubleDot.msdos.creationTime = get_time();
    doubleDot.msdos.modifiedTime = get_time();
    doubleDot.msdos.creationDate = get_date();
    doubleDot.msdos.creationDate = get_date();
    doubleDot.msdos.fileSize = 0;
    doubleDot.msdos.lastAccessTime = get_date();

    doubleDot.msdos.eaIndex;
    doubleDot.msdos.firstCluster;
}

unsigned char lfn_checksum(const unsigned char *pFCBName){
    int i;
    unsigned char sum = 0;

    for (i = 11; i; i--)
        sum = ((sum & 1) << 7) + (sum >> 1) + *pFCBName++;

    return sum;
}

void cat(FILE* imageFile, char* arg1, char* arg2, std::vector<std::string>& pathVars, std::vector<uint32_t>& info, BPB_struct* bpb_struct){
    parse_path(arg1,pathVars);
    info = locate(imageFile,arg1,bpb_struct,pathVars);

    // error
    if(info.empty()){
        return;
    }
    // directory!
    if(info.size() == 5 && info[4] == 0){
        return;
    }


    auto size = bpb_struct->BytesPerSector * bpb_struct->extended.FATSize / 4;
    auto first = First_fat_sector* bpb_struct->BytesPerSector;
    uint32_t FAT[size];
    uint32_t current;
    uint32_t FATVal;
    int val = 0;
    std::vector<std::string> nameList;

    fseek(imageFile,first,SEEK_SET);
    for(int i = 0 ; i < size ; i++){
        fread(&FAT[i],sizeof(uint32_t),1,imageFile);
    }

    current = info[0];

    while(val != EOF){
        auto currentSector = calculateSector(current,bpb_struct);
        auto currentCluster = currentSector * bpb_struct->BytesPerSector;
        auto len = bpb_struct->BytesPerSector*bpb_struct->SectorsPerCluster;

        char cluster[len];

        // entries contains inside of the file
        fseek(imageFile,currentCluster,SEEK_SET);
        fread(cluster,sizeof(char),len,imageFile);

        for(auto c : cluster){
            if(((int)c) != 0)
                std::cout << c;
        }



        FATVal = FAT[current];
        FATVal &= 0x0fffffff;
        if(FATVal >= EOC){
            val = EOF;
        }
        else{
            current = FATVal;
        }
    }
    std::cout << std::endl;
}

void ls(FILE* imageFile, char* arg1, char* arg2, std::vector<std::string>& pathVars, std::vector<uint32_t>& info, BPB_struct* bpb_struct){
    auto size = bpb_struct->BytesPerSector * bpb_struct->extended.FATSize / 4;
    auto first = First_fat_sector* bpb_struct->BytesPerSector;
    uint32_t FAT[size];
    FatFileEntry entries[(bpb_struct->SectorsPerCluster * bpb_struct->BytesPerSector) / sizeof(FatFileEntry)];
    uint32_t current;
    uint32_t FATVal;
    int val = 0;
    std::vector<std::string> nameList;

    fseek(imageFile,first,SEEK_SET);
    for(int i = 0 ; i < size ; i++){
        fread(&FAT[i],sizeof(uint32_t),1,imageFile);
    }


    // ls
    // only find current cluster and print everything
    if(!arg1 && !arg2){
        current = Current_directory_cluster;

        auto currentSector = calculateSector(current,bpb_struct);
        auto currentCluster = currentSector * bpb_struct->BytesPerSector;
        auto len = (bpb_struct->SectorsPerCluster * bpb_struct->BytesPerSector) / sizeof(FatFileEntry);

        // set index to the beginning of the cluster
        // fill entries
        fseek(imageFile,currentCluster,SEEK_SET);
        for(int i = 0 ; i < len ; i++){
            fread(&entries[i],sizeof(FatFileEntry),1,imageFile);
        }

        // while cluster continues
        while(val != EOF){
            // construct files in these entries
            std::string name;

            int j;
            if(current == ROOT_CLUSTER) j = 0;
            else j = 2;

            for(; j < len ; j++){
                if(entries[0].lfn.sequence_number == 0){
                    break;
                }
                if(entries[j].lfn.sequence_number == 0){
                    continue;
                }
                if(entries[j].lfn.attributes == 0x0F){
                    auto lfnName = constructNameOneLFN(entries[j]);
                    name = lfnName + name;
                }
                // MSDOS
                else{
                    nameList.push_back(name);
                    name = "";
                }

            }
            FATVal = FAT[current];
            FATVal &= 0x0fffffff;
            if(FATVal >= EOC){
                val = EOF;
            }
            else{
                current = FATVal;
            }
        }
        auto nameListSize = nameList.size();
        for(int i = 0 ; i < nameListSize; i++){
            if(i == nameListSize - 1){
                std::cout << nameList[i] << std::endl;
            }
            else{
                std::cout << nameList[i] << " ";
            }
        }
    }

    // ls -l
    // find current cluster and print everything in detail
    else if(!strcmp(arg1,"-l") && !arg2){
        current = Current_directory_cluster;

        auto currentSector = calculateSector(current,bpb_struct);
        auto currentCluster = currentSector * bpb_struct->BytesPerSector;
        auto len = (bpb_struct->SectorsPerCluster * bpb_struct->BytesPerSector) / sizeof(FatFileEntry);

        // set index to the beginning of the cluster
        // fill entries
        fseek(imageFile,currentCluster,SEEK_SET);
        for(int i = 0 ; i < len ; i++){
            fread(&entries[i],sizeof(FatFileEntry),1,imageFile);
        }

        // while cluster continues
        while(val != EOF){
            // construct files in these entries
            std::string name;

            int j;
            if(current == ROOT_CLUSTER) j = 0;
            else j = 2;

            for(; j < len ; j++){
                if(entries[0].lfn.sequence_number == 0){
                    break;
                }
                if(entries[j].lfn.sequence_number == 0){
                    continue;
                }
                if(entries[j].lfn.attributes == 0x0F){
                    auto lfnName = constructNameOneLFN(entries[j]);
                    name = lfnName + name;
                }
                    // MSDOS
                else{
                    auto date = entries[j].msdos.modifiedDate;
                    auto time = entries[j].msdos.modifiedTime;
                    auto fileSize = entries[j].msdos.attributes & 0x10;
                    std::string out;
                    if(fileSize != 0) {
                        out = constructLSLFolder(date,time,name);
                    }
                    else{
                        out = constructLSLFile(date,time,fileSize,name);
                    }
                    nameList.push_back(out);
                    name = "";
                }

            }
            FATVal = FAT[current];
            FATVal &= 0x0fffffff;
            if(FATVal >= EOC){
                val = EOF;
            }
            else{
                current = FATVal;
            }
        }
        auto nameListSize = nameList.size();
        for(int i = 0 ; i < nameListSize; i++){
            std::cout << nameList[i] << std::endl;
        }
    }

    // ls dir
    // LOCATE the cluster and print everything
    else if(strcmp(arg1,"-l") != 0 && !arg2){
        parse_path(arg1,pathVars);
        info = locate(imageFile,arg1,bpb_struct,pathVars);

        current = info[0];

        auto currentSector = calculateSector(current,bpb_struct);
        auto currentCluster = currentSector * bpb_struct->BytesPerSector;
        auto len = (bpb_struct->SectorsPerCluster * bpb_struct->BytesPerSector) / sizeof(FatFileEntry);
        int countOfFolders = 0;

        // set index to the beginning of the cluster
        // fill entries
        fseek(imageFile,currentCluster,SEEK_SET);
        for(int i = 0 ; i < len ; i++){
            fread(&entries[i],sizeof(FatFileEntry),1,imageFile);
        }

        // while cluster continues
        while(val != EOF){
            // construct files in these entries
            std::string name;

            int j;
            if(current == ROOT_CLUSTER) j = 0;
            else j = 2;

            for(; j < len ; j++){
                if(entries[0].lfn.sequence_number == 0){
                    break;
                }
                if(entries[j].lfn.sequence_number == 0){
                    continue;
                }
                if(entries[j].lfn.attributes == 0x0F){
                    auto lfnName = constructNameOneLFN(entries[j]);
                    name = lfnName + name;
                }
                    // MSDOS
                else{
                    nameList.push_back(name);
                    name = "";
                }

            }
            FATVal = FAT[current];
            FATVal &= 0x0fffffff;
            if(FATVal >= EOC){
                val = EOF;
            }
            else{
                current = FATVal;
            }
        }
        auto nameListSize = nameList.size();
        for(int i = 0 ; i < nameListSize; i++){
            if(i == nameListSize - 1){
                std::cout << nameList[i] << std::endl;
            }
            else{
                std::cout << nameList[i] << " ";
            }
        }
    }

    // ls -l dir
    // LOCATE the cluster and print everything in detail
    else{
        parse_path(arg2,pathVars);
        info = locate(imageFile,arg2,bpb_struct,pathVars);

        current = info[0];

        auto currentSector = calculateSector(current,bpb_struct);
        auto currentCluster = currentSector * bpb_struct->BytesPerSector;
        auto len = (bpb_struct->SectorsPerCluster * bpb_struct->BytesPerSector) / sizeof(FatFileEntry);
        int countOfFolders = 0;

        // set index to the beginning of the cluster
        // fill entries
        fseek(imageFile,currentCluster,SEEK_SET);
        for(int i = 0 ; i < len ; i++){
            fread(&entries[i],sizeof(FatFileEntry),1,imageFile);
        }

        // while cluster continues
        while(val != EOF){
            // construct files in these entries
            std::string name;

            int j;
            if(current == ROOT_CLUSTER) j = 0;
            else j = 2;

            for(; j < len ; j++){
                if(entries[j].lfn.sequence_number == 0){
                    break;
                }
                if(entries[j].lfn.sequence_number == 0xe5){
                    continue;
                }
                if(entries[j].lfn.attributes == 0x0f){
                    auto lfnName = constructNameOneLFN(entries[j]);
                    name = lfnName + name;
                }
                    // MSDOS
                else{
                    auto date = entries[j].msdos.modifiedDate;
                    auto time = entries[j].msdos.modifiedTime;
                    auto fileSize = entries[j].msdos.attributes & 0x10;
                    std::string out;
                    if(fileSize != 0) {
                        out = constructLSLFolder(date,time,name);
                    }
                    else{
                        out = constructLSLFile(date,time,fileSize,name);
                    }
                    nameList.push_back(out);
                    name = "";
                }

            }
            FATVal = FAT[current];
            FATVal &= 0x0fffffff;
            if(FATVal >= EOC){
                val = EOF;
            }
            else{
                current = FATVal;
            }
        }
        auto nameListSize = nameList.size();
        for(int i = 0 ; i < nameListSize; i++){
            std::cout << nameList[i] << std::endl;
        }
    }
}

std::string constructLSLFile(const uint16_t &date, const uint16_t &time, const uint32_t &filesize, const std::string& filename){

    //hhhh hmmm mmms ssss bit representation
    auto hourRaw = (time & 0xf800)>>11;
    std::string hour;
    if(hourRaw < 9) hour = "0"+std::to_string(hourRaw);
    else hour = std::to_string(hourRaw);

    auto minRaw = (time & 0x07e0)>>5;
    std::string min;
    if(minRaw < 9) min = "0"+std::to_string(minRaw);
    else min = std::to_string(minRaw);

    //yyyy yyym mmmd dddd bit representation
    auto month = (date & 0x01e0)>>5;

    auto dayRaw = date & 0x001f;
    std::string day;
    if(dayRaw < 9) day = "0"+std::to_string(dayRaw);
    else day = std::to_string(dayRaw);

    return LS_FILE_PERM + std::to_string(filesize) + " " + Months[month-1] + " " + day + " " + hour + ":" + min + " " + filename;
}

std::string constructLSLFolder(const uint16_t &date, const uint16_t &time, const std::string& filename){
    //hhhh hmmm mmms ssss bit representation
    auto hourRaw = (time & 0xf800)>>11;
    std::string hour;
    if(hourRaw < 9) hour = "0"+std::to_string(hourRaw);
    else hour = std::to_string(hourRaw);

    auto minRaw = (time & 0x07e0)>>5;
    std::string min;
    if(minRaw < 9) min = "0"+std::to_string(minRaw);
    else min = std::to_string(minRaw);

    //yyyy yyym mmmd dddd bit representation
    auto month = (date & 0x01e0)>>5;

    auto dayRaw = date & 0x001f;
    std::string day;
    if(dayRaw < 9) day = "0"+std::to_string(dayRaw);
    else day = std::to_string(dayRaw);

    return LS_DIR_PERM + Months[month-1] + " " + day + " " + hour + ":" + min + " " + filename;
}

void cd(std::vector<uint32_t> info,std::vector<std::string> pathVars, char* arg){
    auto size = pathVars.size();

    if(info.empty()){
        return;
    }
    if(info.size() == 5 && info[4] != 0){
        return;
    }
    if(arg[0] == '.' && arg[1] == '.' && info[1] == Current_directory_cluster){
        return;
    }

    Current_directory_cluster = info[0];
    Parent_directory_cluster = info[1];

    // ".."
    if(arg[0] == '.' && arg[1] == '.'){
        char c = '/';
        auto len = currentDir.length()-1;
        while(currentDir[len] != c){
            len--;
            currentDir.pop_back();
        }
        currentDir.pop_back();

        if(pathVars.size() > 1){
            auto pathSize = pathVars.size();
            for(int i = 1; i < pathSize; i++){
                currentDir += "/" + pathVars[i];
            }
        }
    }

    // RELATIVE PATH
    else if(arg[0] == '.'){
        for(int i = 1 ; i < size ; i++){
            currentDir += ("/" + pathVars[i]);
        }
    }
    else if(arg[0] != '/'){
        for(int i = 0 ; i < size ; i++){
            currentDir += ("/" + pathVars[i]);
        }
    }

    // ABSOLUTE PATH
    else if(arg[0] == '/'){
        currentDir.clear();
        for(int i = 0 ; i < size ; i++){
            currentDir += ("/" + pathVars[i]);
        }
    }
}

std::string constructNameOneLFN(FatFileEntry & lfn){
    std::string tempName;
    bool flag = false;
    uint16_t* fname = lfn.lfn.name1;
    uint16_t* sname = lfn.lfn.name2;
    uint16_t* tname = lfn.lfn.name3;
    for(int i = 0; i < 5; i++){
        char c = fname[i] & 0x00FF;
        if(c == 0){
            flag = true;
            break;
        }
        tempName += c;
    }
    for(int i = 0; i < 6; i++){
        char c = sname[i] & 0x00FF;
        if(c == 0 || flag){
            flag = true;
            break;
        }
        tempName += c;
    }
    for(int i = 0 ; i < 2; i++){
        char c = tname[i] & 0x00FF;
        if(c == 0 || flag){
            flag = true;
            break;
        }
        tempName += c;
    }
    return tempName;

}

// RETURN : CurrentCluster, ParentCluster, Sector ,ClusterIndex, filesize
std::vector<uint32_t> locate(FILE* imageFile, char* path, BPB_struct * bpb_struct, std::vector<std::string> &pathVars){
    // parse
    auto size = bpb_struct->BytesPerSector * bpb_struct->extended.FATSize / 4;
    auto first = First_fat_sector* bpb_struct->BytesPerSector;
    uint32_t FAT[size];
    FatFileEntry entries[(bpb_struct->SectorsPerCluster * bpb_struct->BytesPerSector) / sizeof(FatFileEntry)];
    uint32_t current;
    uint32_t parent;
    bool gotoparent = false;

    fseek(imageFile,first,SEEK_SET);
    for(int i = 0 ; i < size ; i++){
        fread(&FAT[i],sizeof(uint32_t),1,imageFile);
    }



    if(pathVars[0] == ".."){
        current = Parent_directory_cluster;
        gotoparent = true;

    }
    else if(pathVars[0] == "." || path[0] != '/'){
        current = Current_directory_cluster;
    }
    else{
        current = ROOT_CLUSTER;
    }

    uint32_t FATVal;
    int val = 0;
    int j;
    while(val != EOF){
        if(gotoparent && pathVars.size() > 1) j = 1;
        else j = 0;

        for(; j < pathVars.size(); j++){

            auto currentSector = calculateSector(current,bpb_struct);
            auto currentCluster = currentSector * bpb_struct->BytesPerSector;
            auto len = (bpb_struct->SectorsPerCluster * bpb_struct->BytesPerSector) / sizeof(FatFileEntry);


            // RETRIEVE CURRENT CLUSTER
            fseek(imageFile,currentCluster,SEEK_SET);
            for(int i = 0 ; i < len ; i++){
                fread(&entries[i],sizeof(FatFileEntry),1,imageFile);
            }


            if(gotoparent){

                parent = (entries[1].msdos.eaIndex << 16) | entries[1].msdos.firstCluster;
                if(parent == 0) parent = ROOT_CLUSTER;

                // just cd ..
                if(pathVars.size()== 1){
                    if(current == ROOT_CLUSTER){
                        return std::vector<uint32_t>{current,0};
                    }
                    if(parent == ROOT_CLUSTER){
                        return std::vector<uint32_t>{current,parent};
                    }
                    else{
                        return std::vector<uint32_t>{current,parent,currentSector,currentCluster};
                    }
                }
            }

            if(current == ROOT_CLUSTER){
                std::string name;
                for(int i = 0 ; i < len; i++){
                    // LFN
                    if(entries[i].lfn.sequence_number == 0){
                        return std::vector<uint32_t>(0);
                    }
                    if(entries[i].lfn.sequence_number == 0xe5){
                        continue;
                    }
                    if(entries[i].lfn.attributes == 0x0F){
                        std::string tempName = constructNameOneLFN(entries[i]);

                        name = tempName + name;

                    }

                    // MSDOS
                    else{
                        // if name equals to what we search
                        if(name == pathVars[j]){
                            // if final direction
                            if(j == pathVars.size()-1){
                                uint32_t temp = (entries[i].msdos.eaIndex << 16) | entries[i].msdos.firstCluster; // folders cluster

                                return std::vector<uint32_t>{temp,ROOT_CLUSTER,currentSector,currentCluster,entries[i].msdos.fileSize};
                            }
                            else{
                                current = (entries[i].msdos.eaIndex << 16) | entries[i].msdos.firstCluster;
                                parent = ROOT_CLUSTER;
                                name = "";
                                break;
                            }
                        }
                        else{
                            name = "";
                        }
                    }
                }
            }
            else{
                std::string name;
                parent = (entries[1].msdos.eaIndex << 16) | entries[1].msdos.firstCluster;
                if(parent == 0) parent = ROOT_CLUSTER;
                for(int i = 2 ; i < len; i++){
                    if(entries[i].lfn.sequence_number == 0){
                        return std::vector<uint32_t>(0);
                    }
                    if(entries[i].lfn.sequence_number == 0xe5){
                        continue;
                    }
                    // LFN
                    if(entries[i].lfn.attributes == 0x0F){
                        std::string tempName = constructNameOneLFN(entries[i]);

                        name = tempName + name;
                    }
                    else{
                        // if name equals to what we search
                        if(name == pathVars[j]){
                            // if final direction
                            if(j == pathVars.size()-1){
                                uint32_t temp = (entries[i].msdos.eaIndex << 16) | entries[i].msdos.firstCluster;
                                return std::vector<uint32_t>{temp,current,currentSector,currentCluster,entries[i].msdos.fileSize};
                            }
                            else{
                                current = (entries[i].msdos.eaIndex << 16) | entries[i].msdos.firstCluster;
                                name = "";
                                break;
                            }
                        }
                        else{
                            name = "";
                        }
                    }
                }
            }
        }
        FATVal = FAT[current];
        FATVal &= 0x0fffffff;
        if(FATVal >= EOC){
            val = EOF;
        }
        else{
            current = FATVal;
        }
    }
    return std::vector<uint32_t>(0);
}

uint32_t calculateSector(uint32_t addr,BPB_struct * bpb_struct){
    return ((addr - 2) * bpb_struct->SectorsPerCluster) + First_data_sector;
}


void parse_path(char* path, std::vector<std::string> & pathVars){
    if(!path){
        return;
    }

    std::string s;
    auto len = strlen(path);
    for(int i = 0 ; i < len; i++){
        s.push_back(path[i]);
    }

    auto position = 0;
    std::string tok;
    std::string delim = "/";
    while(1){
        position = s.find(delim);
        if(position == std::string::npos){
            break;
        }
        tok = s.substr(0,position);
        s.erase(0, position + 1);
        if(tok != "")
            pathVars.push_back(tok);
    }
    pathVars.push_back(s);
}

/* fills bpb struct */
void fill_bpb_struct(FILE* imageFile, BPB_struct* bpbStruct){
    // READ BPB STRUCT FROM IMAGE FILE
    fseek(imageFile,0,SEEK_SET);

    fread(&bpbStruct->BS_JumpBoot,3,1,imageFile);
    fread(&bpbStruct->BS_OEMName,8,1,imageFile);
    fread(&bpbStruct->BytesPerSector,2,1,imageFile);
    fread(&bpbStruct->SectorsPerCluster,1,1,imageFile);

    fread(&bpbStruct->ReservedSectorCount,2,1,imageFile);
    fread(&bpbStruct->NumFATs,1,1,imageFile);
    fread(&bpbStruct->RootEntryCount,2,1,imageFile);
    fread(&bpbStruct->TotalSectors16,2,1,imageFile);

    fread(&bpbStruct->Media,1,1,imageFile);
    fread(&bpbStruct->FATSize16,2,1,imageFile);
    fread(&bpbStruct->SectorsPerTrack,2,1,imageFile);
    fread(&bpbStruct->NumberOfHeads,2,1,imageFile);

    fread(&bpbStruct->HiddenSectors,4,1,imageFile);
    fread(&bpbStruct->TotalSectors32,4,1,imageFile);

    // OFFSET IS SET TO 36 TO GET BPB32 STRUCT
    fseek(imageFile,36,SEEK_SET);
    fread(&bpbStruct->extended.FATSize,4,1,imageFile);
    fread(&bpbStruct->extended.ExtFlags,2,1,imageFile);
    fread(&bpbStruct->extended.FSVersion,2,1,imageFile);
    fread(&bpbStruct->extended.RootCluster,4,1,imageFile);
    fread(&bpbStruct->extended.FSInfo,2,1,imageFile);
    fread(&bpbStruct->extended.BkBootSec,2,1,imageFile);
    fread(&bpbStruct->extended.Reserved,12,1,imageFile);
    fread(&bpbStruct->extended.BS_DriveNumber,1,1,imageFile);
    fread(&bpbStruct->extended.BS_Reserved1,1,1,imageFile);
    fread(&bpbStruct->extended.BS_BootSig,1,1,imageFile);
    fread(&bpbStruct->extended.BS_VolumeID,4,1,imageFile);
    fread(&bpbStruct->extended.BS_VolumeLabel,11,1,imageFile);
    fread(&bpbStruct->extended.BS_FileSystemType,8,1,imageFile);
}

void printCurrentDir(){
    if(currentDir.empty()){
        std::cout << "/> ";
        return;
    }
    std::cout << currentDir << "> ";
}
void closeFile(FILE* imageFile){
    fclose(imageFile);
}

