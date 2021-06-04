
#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>

#define BUFFLEN 64


#define errtrap(error) (__errtrap(result, error, __LINE__))
void __errtrap(int result, const char* error, int line) {

	if (result < 0) {
		printf("Error in %s() on line %d:  %s\n", error, line, strerror(errno));
		_exit(errno);
	}
	return;

}

#define writelog(...) snprintf(argbuff, BUFFLEN, __VA_ARGS__); \
	result = write(fd_log, argbuff, strnlen(argbuff, BUFFLEN)); \
	__errtrap(result, "write", __LINE__);


int main() {

	printf("Hello World\n");

	long tid;
	cpu_set_t set;
	int result;
	int core;
	char argbuff[BUFFLEN];
	int fd_log;
	char logfile[] = "/data/pinlog.txt";


	core = 1;

	// Create logfile:
	result = open(logfile, O_CREAT | O_RDWR | O_TRUNC, 0666);
	errtrap("open");
	fd_log = result;

	// Get input line from STDIN (redirected from ps / grep output):
	result = read(0, argbuff, BUFFLEN);
	errtrap("read");
	// Unpack the PID of the benchmark app from the ps / grep input line:
	tid = atoi(argbuff + 14);
	result = writelog("PID:  %ld\n", tid);
	errtrap("write");

	// Pin client thread to core(s):
//	tid = syscall(__NR_gettid);
	CPU_ZERO(&set);
	CPU_SET(core, &set);
	result = sched_setaffinity(tid, sizeof(set), &set);
	errtrap("sched_setaffinity");
	result = writelog("Thread tid %ld pinned to core %d\n", tid, core);
	errtrap("write");

	close(fd_log);

	return 0;

}


