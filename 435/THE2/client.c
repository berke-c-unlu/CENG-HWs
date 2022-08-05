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

/***
 * TODO
 * divide message into packets and send it properly
 * concatenate received packets into message
 * structure window
 * selective repeat
 * ack/nak
***/

/* structure of a packet */
struct packet{
    char payload[8]; // maximum 8 bytes in a packet as payload, last byte is '\0'
    long checksum; // checksum variable for reliability
    int ACK; // 1 for ack, 0 for nak
    int number; // seq number of a packet
};

/*
struct window{


};
*/


/****************************** prototypes ******************************/
void closeClient(int);
int startClient(struct sockaddr_in *, int,char*);
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

    //printf("payload: %s\n",currentPacket->payload);
    //printf("checksum : %ld\n",currentPacket->checksum);
    //printf("ACK : %d\n",currentPacket->ACK);
    //printf("number: %d\n",currentPacket->number);

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
        free(curr);
    }

    return packages;
}

void chat(int sockfd, struct sockaddr_in *clientAddress, char * buffer){
    struct packet ** packages = divideMessage(buffer);
    
    struct pollfd pfds[2];
    
    pfds[0].fd = sockfd;
    pfds[0].events = POLLIN;

    pfds[1].fd = STDIN_FILENO;
    pfds[1].events = POLLIN;

    while(TRUE){
        int poll_count = poll(pfds,2,2500);

        if(poll_count == -1){
            perror("poll\n");
            exit(1);
        }

        if(pfds[0].revents && POLLIN){
            receiveMessage(sockfd,buffer,clientAddress);

            printf("%s\n",buffer);
            //printf("size: %d\n",(int)strlen(buffer));

            char bye[4];
            char compare[4] = "BYE";
            for(int i = 0 ; i < 3; i++){
                bye[i] = buffer[i];
            }
            bye[3] = '\0';



            if(strcmp(bye,compare) == 0){
                //printf("BYE is received\n");
                closeClient(sockfd);
                break;
            }
        }

        if(pfds[1].revents && POLLIN){
            fgets(buffer,MAX_LINE,stdin);

            //printf("chat will send : %s\n",buffer);
            //printf("size: %d\n",(int)strlen(buffer));

            sendMessage(sockfd,buffer,clientAddress,strlen(buffer));

            char bye[4];
            char compare[4] = "BYE";
            for(int i = 0 ; i < 3; i++){
                bye[i] = buffer[i];
            }
            bye[3] = '\0';

            if(strcmp(bye,compare) == 0){
                //printf("BYE is sent\n");
                closeClient(sockfd);
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
void sendMessage(int sockfd, char* buffer, struct sockaddr_in *serverAddress, int size){

    socklen_t len = sizeof(*serverAddress);
    int bytes_sent; // sendto returns the number of bytes sent. if an error occurs, returns -1.

    bytes_sent = sendto(sockfd, (const char*) buffer, size, MSG_CONFIRM, (const struct sockaddr*) serverAddress, len);

    //printf("bytes_sent (client) : %d\n",bytes_sent);
    //printf("message (client send) : %s\n",buffer);

}


/***
 *  basic message receive function 
 *  first param: socket
 *  second param : message
 *  third param : server address
***/
void receiveMessage(int sockfd, char* buffer, struct sockaddr_in *serverAddress){

    socklen_t* len = malloc(sizeof(socklen_t));
    int bytes_received; // recvfrom returns the number of bytes received. if an error occurs, returns -1.

    *len = sizeof(*serverAddress);

    bytes_received = recvfrom(sockfd, buffer, MAX_LINE, MSG_WAITALL, (struct sockaddr*) serverAddress, len);

    buffer[bytes_received] = '\0'; // bytes_received is the size of the message. So, it is the last index and I put the end of string symbol.

    //printf("bytes_received (client) : %d\n",bytes_received);
    //printf("message (client recv) : %s\n",buffer);

}

/***
 * first param : client address struct
 * second param : bind port
 * third param : ip address
***/
int startClient(struct sockaddr_in *clientAddress, int port,char* ip){
    int bind_value; // check whether bind operation is successful
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0); // create socket, AF_INET : IpV4, SOCK_DGRAM : UDP SOCKET

    if(sockfd < 0) {fprintf(stderr, "socket creation error\n");} // if error occurs while creating socket

    clientAddress->sin_family = AF_INET; // IpV4
    clientAddress->sin_port = htons(port);  // bit order issue
    clientAddress->sin_addr.s_addr = inet_addr(ip); // ip address 127.0.0.1

    /***
     * bind the socket to client address and bind port
     * first param : clientSocket
     * second param : client address + bind port
     * third param : size of the struct
     * return value : int, indicates whether binding is successful or not
    ***/
    bind_value = bind(sockfd,(const struct sockaddr *) clientAddress,sizeof(*clientAddress));

    //printf("bind_val : %d\n",bind_value);
    //printf("address: %s,  port : %d\n",ip,port);

    
    return sockfd;
}

/* closes client */
void closeClient(int sockfd){
    close(sockfd);
    fprintf(stderr,"client has been closed!\n");
}


int main(int argc, char* argv[]){
    /***** variables *****/
    int clientSocket;
    struct sockaddr_in serverAddress, clientAddress;
    char buffer[MAX_LINE];

    /***** arguments *****/
    char* ip_string = argv[1];
    int troll_port = atoi(argv[2]);
    int bind_port = atoi(argv[3]);

    /***** fill addresses with 0s, since we'll give values later *****/
    memset(&serverAddress,0,sizeof(serverAddress));
    memset(&clientAddress,0,sizeof(clientAddress));

    // create socket
    clientSocket = startClient(&clientAddress,bind_port,ip_string);

    // fill necessary values of server address, since client will send the first message it will need it.
    serverAddress.sin_addr.s_addr = inet_addr(ip_string);
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(troll_port);


    // handshake
    char buf[MAX_LINE] = "hello!";
    sendMessage(clientSocket,buf,&serverAddress,strlen(buf));
    //printf("client message sent 1\n");

    // handshake
    receiveMessage(clientSocket,buffer,&serverAddress);
    printf("%s\n",buffer);    

    chat(clientSocket,&serverAddress,buffer);

    return 0;
}
