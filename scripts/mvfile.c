
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>


#define errtrap(error) (__errtrap(retval, error, __LINE__))
void __errtrap(int retval, const char* error, int line) {

	if (retval == -1) {
		printf("Error in %s() on line %d:  %s\n", error, line, strerror(errno));
		_exit(errno);
	}
	return;

}

#define SYSCALL( ret, call, ... ) ret = call( __VA_ARGS__ ); \
	__errtrap(ret, #call, __LINE__);


int subproc(char** childargv) {

	int retval;
	pid_t pid;
	int wstatus;

	SYSCALL(retval, fork);
	pid = retval;
	if (pid > 0) {
		SYSCALL(retval, waitpid, pid, &wstatus, 0);
		if (WIFEXITED(wstatus) == 0) {
			_exit(11);
		}
		if (WEXITSTATUS(wstatus) != 0) {
			_exit(12);
		}
	}
	if (pid == 0) {
		SYSCALL(retval, execve, childargv[0], childargv, NULL);
		_exit(99);
	}

	return 0;

}


int main(int argc, char** argv) {

	printf("Hello World\n");

	int BUFFLEN = 128;
	char argbuff0[BUFFLEN];
	char argbuff1[BUFFLEN];
	char argbuff2[BUFFLEN];
	char* childargv[] = {argbuff0, argbuff1, argbuff2, NULL};

	snprintf(argbuff0, BUFFLEN, "/bin/mv");
	snprintf(argbuff1, BUFFLEN, "/home/carlnues/win_mount/monsoon_%s.csv", argv[1]);
	snprintf(argbuff2, BUFFLEN, "logs/");
	subproc(childargv);

	snprintf(argbuff1, BUFFLEN, "/home/carlnues/win_mount/monsoon_%s.pt5", argv[1]);
	subproc(childargv);

	snprintf(argbuff0, BUFFLEN, "/bin/chown");
	snprintf(argbuff1, BUFFLEN, "1000:1000");
	snprintf(argbuff2, BUFFLEN, "logs/monsoon_%s.csv", argv[1]);
	subproc(childargv);

	snprintf(argbuff2, BUFFLEN, "logs/monsoon_%s.pt5", argv[1]);
	subproc(childargv);

	snprintf(argbuff0, BUFFLEN, "/bin/chmod");
	snprintf(argbuff1, BUFFLEN, "644");
	snprintf(argbuff2, BUFFLEN, "logs/monsoon_%s.csv", argv[1]);
	subproc(childargv);

	snprintf(argbuff2, BUFFLEN, "logs/monsoon_%s.pt5", argv[1]);
	subproc(childargv);

	return 0;

}

