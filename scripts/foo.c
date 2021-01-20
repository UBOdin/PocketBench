
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#include <signal.h>
#include <time.h>


#define BUFFSIZE 256


char buffer[BUFFSIZE];
int fd;


void errtrap(int result, char* error, int err) {

	if (result == -1) {
		printf("Error on %s():  %s %d\n", error, strerror(errno), err);
		_exit(err);
	}
	return;

}


void writelog(char* string, int err) {

	int result;

	result = write(fd, string, strlen(string));
	errtrap(result, "write", err);

	return;

}


void sighup_handler(int sig) {


	strcpy(buffer, "Caught signal sighup\n");
	writelog(buffer, 44);
//	return;

	close(fd);
	_exit(5);

}


int main(int argc, char** argv) {

	printf("Hello World\n");

	int result;

	char logfile[] = "/data/pid.txt";

//	char logfile[] = "pid.txt";

	struct sigaction sighup_action_struct;

	memset(&sighup_action_struct, 0, sizeof(struct sigaction));
	sighup_action_struct.sa_handler = &sighup_handler;

	result = open(logfile, O_CREAT | O_RDWR | O_TRUNC, 0666);
        errtrap(result, "open", 1);
        fd = result;

	result = sigaction(SIGHUP, &sighup_action_struct, NULL);
	errtrap(result, "sigaction", 31);



	for (int i = 0; i < argc; i++) {

		printf("Arg %d:  %s\n", i, argv[i]);
		snprintf(buffer, BUFFSIZE, "Arg %d:  %s\n", i, argv[i]);
		writelog(buffer, 2);

	}

	printf("PID:  %d\n", getpid());
	snprintf(buffer, BUFFSIZE, "PID:  %d\n", getpid());
	writelog(buffer, 3);

	struct timespec timewait_struct;

	memset(&timewait_struct, 0, sizeof(struct timespec));
	timewait_struct.tv_sec = 10;
	timewait_struct.tv_nsec = 0;

	result = nanosleep(&timewait_struct, NULL);
	errtrap(result, "nanosleep", 51);


	result = close(fd);
	errtrap(result, "close", 3);

	return 0;

}


