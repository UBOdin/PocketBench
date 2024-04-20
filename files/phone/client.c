
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
	struct sockaddr_in ssin;
	int sock;
	int port;
//	char server_ip_address[] = "128.205.39.155";
	char server_ip_address[] = "192.168.1.199";
	socklen_t addrlen;

	char logfile[] = "/data/wifi_client_log.txt";

	if (argc != 2) {
		printf("Missing port number\n");
		_exit(11);
	}
	port = atoi(argv[1]);

	// Create logfile:
	result = open(logfile, O_CREAT | O_RDWR | O_TRUNC, 0666);
	errtrap("open");
	fd_log = result;
writelog("After open\n");

	// Request a TCP socket:
	result  = socket(AF_INET, SOCK_STREAM, 0);
	errtrap("socket");
	sock = result;
writelog("After socket\n");

	// Populate sockaddr_in struct with ip port and address:
	ssin.sin_family = AF_INET;
	ssin.sin_port = htons(port);
	result = inet_pton(AF_INET, server_ip_address, &ssin.sin_addr.s_addr);
	errtrap("pton");
	if (result == 0) {
		printf("Invalid IP address\n");  // N.b., errno _not_ set in this case...
		_exit(12);
	}
writelog("After populate\n");

	// Make the external connection:
	result = connect(sock, (struct sockaddr*) &ssin, sizeof(struct sockaddr_in));
	errtrap("connect");
writelog("After connect\n");

writelog("Sending data:\n");
strcpy(buffer, "Testing 123 Testing...");
writelog(buffer);
writelog("\n");

	// Send identification string:
	result = send(sock, buffer, strnlen(buffer, BUFFER_SIZE), 0);
	errtrap("send");
writelog("After send\n");

	result = close(sock);
	errtrap("close");
writelog("After close\n");

	result = close(fd_log);
	errtrap("close");

	printf("Exit clean\n");
	exit(0);

}


