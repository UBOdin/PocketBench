
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
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
	struct sockaddr_un ssun_listen;
	int listen_inet;
	int listen_unix;
	int port_listen;
	char server_ip_address[] = "128.205.39.155";
	char logfile[] = "wifi_server_log.txt";
	socklen_t addrlen;
	struct sockaddr_in ssin;
	struct sockaddr_un ssun;
	int sock_inet;
	int sock_unix;
	char relay_file[] = "relay.sock";

	if (argc != 2) {
		printf("Missing port number\n");
		exit(1);
	}
	port_listen = atoi(argv[1]);

	memset(&ssin_listen, 0, sizeof(ssin_listen));
	memset(&ssun_listen, 0, sizeof(ssun_listen));

	// Create logfile:
//	result = open(logfile, O_CREAT | O_RDWR | O_TRUNC, 0666);
//	errtrap("open");
//	fd_log = result;
	fd_log = 2;  // STDERR
//	writelog("After open\n");
	snprintf(buffer, BUFFER_SIZE, "Listen port requested:  %d\n", port_listen);
	writelog(buffer);

	// Request a TCP socket for listening:
	result = socket(AF_INET, SOCK_STREAM, 0);
	errtrap("socket");
	listen_inet = result;

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
	result = bind(listen_inet, (struct sockaddr*) &ssin_listen, sizeof(struct sockaddr_in) );
	errtrap("bind");
	// Turn on listening:
	result = listen(listen_inet, LISTEN_BACKLOG);
	errtrap("listen");

	// Accept the connection:
	writelog("Blocking on incoming connection\n");
	addrlen = sizeof(struct sockaddr_in);	// set to the actual socket address size upon return
	result = accept(listen_inet, (struct sockaddr*) &ssin, &addrlen);
	errtrap("accept");
	sock_inet = result;
	snprintf(buffer, BUFFER_SIZE, "Accepted incoming connection.  Assigned new fd #%i\n", result);
	writelog(buffer);

//

	// Remove any previous relay file:
	result = unlink(relay_file);
	// Ignore nonexistent file error:
	if ((result == -1) && (errno != ENOENT)) {
		errtrap("unlink");
	}
	if (result == 0) {
		printf("Removed previous unix socket\n");
	}

	// Request a Unix socket for listening:
	result = socket(AF_UNIX, SOCK_STREAM, 0);
	errtrap("socket");
	listen_unix = result;

	// Populate sockaddr_un struct with relay socket filename:
	ssun_listen.sun_family = AF_UNIX;
	strncpy(ssun_listen.sun_path, relay_file, sizeof(ssun_listen.sun_path) - 1);

	// Attempt to bind to the file requested:
	result = bind(listen_unix, (struct sockaddr*) &ssun_listen, sizeof(struct sockaddr_un) );
	errtrap("bind");
	// Turn on listening:
	result = listen(listen_unix, LISTEN_BACKLOG);
	errtrap("listen");

//
	fd_set fds;
	int fds_max;

	sock_unix = 0;

	while (1) {

		FD_ZERO(&fds);
		FD_SET(0, &fds);
		FD_SET(sock_inet, &fds);
		FD_SET(listen_unix, &fds);
		if (sock_unix > 0) {
			FD_SET(sock_unix, &fds);
		}

		fds_max = sock_inet;
		if (listen_unix > fds_max) {
			fds_max = listen_unix;
		}
		if (sock_unix > fds_max) {
			fds_max = sock_unix;
		}

		result = select(fds_max + 1, &fds, NULL, NULL, NULL);
		errtrap("select");

		if (FD_ISSET(0, &fds)) {

			result = read(0, buffer, BUFFER_SIZE);
			errtrap("read");
			printf("Bytes typed:  %d\n", result);
			printf("Type again\n");
			buffer[result] = 0;
			result = send(sock_inet, buffer, result - 1, 0);
			errtrap("send");

		}

		if (FD_ISSET(sock_inet, &fds)) {

			result = recv(sock_inet, buffer, BUFFER_SIZE, 0);
			errtrap("recv");
			if (result == 0) {
				break;
			}
			buffer[result] = 0;
			printf("Received inet data:  %s\n", buffer);

		}

		if (FD_ISSET(listen_unix, &fds)) {

			result = accept(listen_unix, (struct sockaddr*) &ssun, &addrlen);
			errtrap("accept");
			sock_unix = result;
			snprintf(buffer, BUFFER_SIZE, "Accepted unix connection.  Assigned new fd #%i\n", result);
			writelog(buffer);

		}

		if ((sock_unix > 0) && (FD_ISSET(sock_unix, &fds))) {

			result = recv(sock_unix, buffer, BUFFER_SIZE, 0);
			errtrap("recv");
			if (result == 0) {
				sock_unix = 0;
				printf("Lost unix connection\n");
			} else {
				buffer[result] = 0;
				printf("Received unix data:  %s\n", buffer);
				result = send(sock_inet, buffer, result - 1, 0);
				errtrap("send");
			}

		}

	}

	result = close(sock_inet);
	errtrap("close");
	writelog("After close\n");
//	result = close(fd_log);
//	errtrap("close");
	writelog("Exit clean\n");
	exit(0);

}


