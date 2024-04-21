
#include <asm/unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>


#define errtrap(error) (__errtrap(retval, error, __LINE__))
void __errtrap(int retval, const char* error, int line) {

	if (retval == -1) {
		printf("Error in %s() on line %d:  %s\n", error, line, strerror(errno));
//		__android_log_print(ANDROID_LOG_VERBOSE, "Microbench", "Error:  %d %s\n", errno, strerror(errno));
		_exit(errno);
	}
	return;

}


int main(int argc, char** argv) {

	int retval;
	int policy;
	struct timespec interval;
	long sleep1_s;
	long sleep2_s;

	policy = atoi(argv[1]);
	if ((policy != 70) && (policy != 100)) {
		return -2;
	}
	sleep1_s = (long)atoi(argv[2]);
	sleep2_s = (long)atoi(argv[3]);

	retval = syscall(285, policy);
	errtrap("syscall");

	interval.tv_sec = sleep1_s;
	interval.tv_nsec = 0;
	retval = nanosleep(&interval, NULL);
	errtrap("nanosleep");

	if (sleep2_s != 0) {
		retval = syscall(285, policy);
		errtrap("syscall");
		interval.tv_sec = sleep2_s;
		retval = nanosleep(&interval, NULL);
		errtrap("nanosleep");
	}

	printf("Return value:  %d\n", retval);

	return 0;

}

