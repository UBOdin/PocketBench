
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>


#define LISTEN_BACKLOG 10
#define BUFFER_SIZE 256


char buffer[BUFFER_SIZE];
int fd_log;


#define errtrap(error) (__errtrap(result, error, __LINE__))
void __errtrap(int result, char* error, int line) {

	if (result == -1) {
		snprintf(buffer, BUFFER_SIZE, "Error in %s() on line %d:  %s\n", error, line, strerror(errno));
		write(fd_log, buffer, strlen(buffer));
		printf("%s", buffer);
		_exit(errno);
	}
	return;

}


#define writelog(string) (__writelog(string, __LINE__))
void __writelog(char* string, int line) {

	int result;

	result = write(fd_log, string, strlen(string));
	errtrap("write");

	return;

}


int main(int argc, char** argv) {
	
	int result;					// Generic return code holder
	struct sockaddr_in ssin_listen;
	int sock_listen;
	int port_listen;
	long optval;
	char server_ip_address[] = "128.205.39.155";

	char logfile[] = "wifi_server_log.txt";

	socklen_t addrlen;

	struct sockaddr_in ssin;
	int sock;

	if (argc != 2) {
		printf("Missing port number\n");
		exit(1);
	}
	port_listen = atoi(argv[1]);

	// Create logfile:
	result = open(logfile, O_CREAT | O_RDWR | O_TRUNC, 0666);
	errtrap("open");
	fd_log = result;
writelog("After open\n");


snprintf(buffer, BUFFER_SIZE, "Listen port requested:  %d\n", port_listen);
writelog(buffer);

	// Request a TCP socket for listening:
	result = socket(AF_INET, SOCK_STREAM, 0);
	errtrap("socket");
	sock_listen = result;

	// Disable reuse checking (sidestep TIME_WAIT problems):
	optval = 1;
	result = setsockopt(sock_listen, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval));
	errtrap("setsockopt");

	// Populate sockaddr_in struct with ip port and address:
	ssin_listen.sin_family = AF_INET;
	ssin_listen.sin_port = htons(port_listen);
	result = inet_pton(AF_INET, server_ip_address, &ssin_listen.sin_addr.s_addr);
	errtrap("pton");
	if (result == 0) {
		printf("Invalid IP address\n");  // N.b., errno _not_ set in this case...
		exit(1);
	}

	// Attempt to bind to the port requested:
	result = bind(sock_listen, (struct sockaddr*) &ssin_listen, sizeof(struct sockaddr_in) );
	errtrap("bind");
	// Turn on listening:
	result = listen(sock_listen, LISTEN_BACKLOG);
	errtrap("listen");

//result = close(sock_listen);
//errtrap("close");

writelog("Blocking on incoming connection\n");

	// Accept the connection:
	addrlen = sizeof(struct sockaddr_in);	// set to the actual socket address size upon return
	result = accept(sock_listen, (struct sockaddr*) &ssin, &addrlen);
	errtrap("accept");
	sock = result;

snprintf(buffer, BUFFER_SIZE, "Accepted incoming connection.  Assigned new fd #%i\n", result);
writelog(buffer);

	// Read in chunk of data:
	result = recv(sock, buffer, BUFFER_SIZE, 0);
	errtrap("recv");
	// Nullterm the string:
	buffer[result] = (char)0;

writelog("Received data:\n");
writelog(buffer);
writelog("\n");
snprintf(buffer, BUFFER_SIZE, "%d bytes received\n", result);
writelog(buffer);

	result = close(sock);
	errtrap("close");
writelog("After close");

	close(sock_listen);

	result = close(fd_log);
	errtrap("close");

	printf("Exit clean\n");
	exit(0);

}


