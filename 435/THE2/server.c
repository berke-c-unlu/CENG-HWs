#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>
#include <string.h>
#include <errno.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <netdb.h>

#include <signal.h>
#include <poll.h>

#define MAX_LINE 1024
#define TRUE 1



/* structure of a packet */
struct packet{
    char payload[8]; // maximum 8 bytes in a packet as payload
    long checksum; // checksum variable for reliability
    int ACK; 
    int number; // seq number of a packet
};


/*
struct window{

};
*/




/****************************** prototypes ******************************/
void closeServer(int);
int createServer(struct sockaddr_in *, int);
void sendMessage(int, char*, struct sockaddr_in *, int);
void receiveMessage(int, char*, struct sockaddr_in *);
void chat(int, struct sockaddr_in *, char *);
struct packet ** divideMessage(char*);
struct packet* constructPacket(char*, int);





/***
 * creates A packet
 * first param : 8 byte message
 * second param : number of the packet
 * return val : struct packet
***/
struct packet* constructPacket(char* partOfTheMessage, int number){
    struct packet* currentPacket = malloc(sizeof(struct packet)); // allocate memory for packet
    long chksm = 0;
    int i;

    for(i = 0; i < 8; i++){
        currentPacket->payload[i] = partOfTheMessage[i]; // load payload
        chksm += currentPacket->payload[i]; // create checksum
    }

    currentPacket->checksum = chksm;
    currentPacket->ACK = 0;
    currentPacket->number = number;

    return currentPacket;
}


// returns list of packets
struct packet ** divideMessage(char* message){
    int i,k;
    int j = 0;
    int allocation = strlen(message) / 8; // how many packages we will have
    struct packet** packages = malloc(sizeof(struct packet*) * allocation); // pointer of the pointer of the packages


    for(i = 0; i < allocation ; i += 8){
        char* curr = malloc(sizeof(char)*8); // part of the message
        struct packet* p = NULL; // current packet

        k = 0;
        while(j % 8 != 0){
            curr[k] = message[j];
            j++;
            k++;
        }
        p = constructPacket(curr,i);
        packages[i] = p;
    }

    return packages;
}


void chat(int sockfd, struct sockaddr_in *clientAddress, char * buffer){
    struct packet ** packages = divideMessage(buffer);
    
    struct pollfd pfds[2];
    
    // for receive
    pfds[0].fd = sockfd;
    pfds[0].events = POLLIN;

    // for send
    pfds[1].fd = STDIN_FILENO;
    pfds[1].events = POLLIN;

    // infinite loop. If "BYE" is the message, the server and client will shutdown.
    while(TRUE){
        int poll_count = poll(pfds,2,2500); // 2.5 s timeout

        if(poll_count == -1){
            perror("poll\n");
            exit(1);
        }

        // if socket is ready to receive a message
        if(pfds[0].revents && POLLIN){
            receiveMessage(sockfd,buffer,clientAddress);

            printf("%s\n",buffer);
            //printf("size: %d\n",(int)strlen(buffer));

            // test part of "BYE"
            char bye[4];
            char compare[4] = "BYE";
            for(int i = 0 ; i < 3; i++){
                bye[i] = buffer[i];
            }
            bye[3] = '\0';

            if(strcmp(bye,compare) == 0){
                //printf("BYE is received\n");
                closeServer(sockfd);
                break;
            }
        }


        // if socket is ready to send a message from stdin
        if(pfds[1].revents && POLLIN){
            fgets(buffer,MAX_LINE,stdin); // get message 

            //printf("chat will send : %s\n",buffer);
            //printf("size: %d\n",(int)strlen(buffer));

            // send message
            sendMessage(sockfd,buffer,clientAddress,strlen(buffer));

            // test part of "BYE" 
            char bye[4];
            char compare[4] = "BYE";
            for(int i = 0 ; i < 3; i++){
                bye[i] = buffer[i];
            }
            bye[3] = '\0';


            if(strcmp(bye,compare) == 0){
                //printf("BYE is sent\n");
                closeServer(sockfd);
                break;
            }
        }
    }
}




/***
     * first param : socket
     * second param : message
     * third param: client Address
     * fourth param: size of the message
***/
void sendMessage(int sockfd, char* buffer, struct sockaddr_in *clientAddress, int size){

    socklen_t len = sizeof(*clientAddress);
    int bytes_sent; // sendto returns the number of bytes sent. if an error occurs, returns -1.

    //printf("len variable send message: %d\n",len);

    bytes_sent = sendto(sockfd, (const char*) buffer, size, MSG_CONFIRM, (const struct sockaddr*) clientAddress, len);
    //printf("bytes recv : %d\n",bytes_sent);
}

void receiveMessage(int sockfd, char* buffer, struct sockaddr_in *clientAddress){
    socklen_t* len = malloc(sizeof(socklen_t));
    int bytes_received; // recvfrom returns the number of bytes received. if an error occurs, returns -1.

    *len = sizeof(clientAddress);
    //printf("len variable receive message: %d\n",*len);

    bytes_received = recvfrom(sockfd, buffer, MAX_LINE, MSG_WAITALL, (struct sockaddr*) clientAddress, len);

    buffer[bytes_received] = '\0'; // bytes_received is the size of the message. So, it is the last index and I put the end of string symbol.

    //printf("bytes recv : %d\n",bytes_received);
    //printf("buff: %s\n",buffer);
}


/***
 * first param: empty server address struct, I will fill the necessary parts in this function
 * second param: port, I will put port in the server adress struct
 * return value: the UDP socket has been created.
***/
int createServer(struct sockaddr_in *server_address, int port){
    int bind_value; // check whether bind operation is successful
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0); // create socket, AF_INET : IpV4, SOCK_DGRAM : UDP SOCKET
    
    //printf("socket created (server)\n");

    if(sockfd < 0) {fprintf(stderr, "socket creation error");} // if socket couldnt be created, then exit

    server_address->sin_family = AF_INET; // IpV4
    server_address->sin_port = htons(port); // saw in beej's guide, bit order issue
    server_address->sin_addr.s_addr = INADDR_ANY; // host ip address

    //printf("address filled (server)\n");

    /***
     * bind the socket to server address and port
     * first param : serverSocket
     * second param : server address + port
     * third param : size of the struct
     * return value : int, indicates whether binding is successful or not
    ***/
    bind_value = bind(sockfd,(const struct sockaddr *)server_address,sizeof(*server_address));

    //printf("socket bound (server)\n");
    //printf("port: %d, address: %d \n",port,server_address->sin_addr.s_addr);

    if(bind_value < 0){fprintf(stderr, "while binding socket, an error occured");} // if binding is not successful, then exit


    return sockfd;
}

/* closes server */
void closeServer(int sockfd){
    close(sockfd);
    fprintf(stderr,"the server has been closed.\n");
}


int main(int argc, char* argv[]){
    /***** variables *****/
    struct sockaddr_in serverAddress, clientAddress;
    int serverSocket, currentPort;
    char* port_string;
    char buffer[MAX_LINE];

    /***** arguments *****/
    port_string = argv[1];
    currentPort = atoi(port_string);

    // fill everything inside these to 0
    memset(&serverAddress,0,sizeof(serverAddress));
    memset(&clientAddress,0,sizeof(clientAddress));

    serverSocket = createServer(&serverAddress,currentPort); // socket created
    
    //printf("socket value: %d\n",serverSocket);
    


    // handshake
    receiveMessage(serverSocket,buffer,&clientAddress); // client address will be filled
    printf("%s\n",buffer);

    // handshake
    char buf[MAX_LINE] = "HELLO!";
    sendMessage(serverSocket,buf,&clientAddress,strlen(buf));
    //printf("server message sent\n");

    chat(serverSocket,&clientAddress,buffer);
    
    return 0;
}
