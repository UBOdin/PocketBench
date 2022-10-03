
#include <android/log.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

#define THREADMAX 16


#define errtrap(error) (__errtrap(result, error, __LINE__))
void __errtrap(int result, const char* error, int line) {

	if (result == -1) {
//		printf("Error in %s() on line %d:  %s\n", error, line, strerror(errno));
		__android_log_print(ANDROID_LOG_VERBOSE, "FORK_WORKERS", "Error:  %d %s\n", errno, strerror(errno));
		_exit(errno);
	}
	return;

}


void errlog() {

	__android_log_print(ANDROID_LOG_VERBOSE, "PocketData", "Error:  %d %s\n", errno, strerror(errno));
//printf("Error:  %d %s\n", errno, strerror(errno));

	return;

}


int main(int argc, char** argv) {

	int result;
	char binpath[] = "/data/compute.exe";
	int threadcount;
	int pidpool[THREADMAX];
	int wstatus;

	threadcount = atoi(argv[1]);
	if (threadcount > THREADMAX) {
			__android_log_print(ANDROID_LOG_VERBOSE, "FORK_WORKERS", "Error:  workers > MAX\n");
			_exit(133);
	}

	for (int i = 0; i < threadcount; i++) {
		result = fork();
		errtrap("fork");
		if (result == 0) {
			result = execv(binpath, argv + 2);
			errtrap("execv");
			_exit(99);  // Never gets here
		}
		if (result > 0) {
			pidpool[i] = result;
		}
//printf("Forked thread %d\n", result);
	}

	for (int i = 0; i < threadcount; i++) {
		result = waitpid(pidpool[i], &wstatus, 0);
		errtrap("waitpid");

		if (WIFEXITED(wstatus) == 0) {
			__android_log_print(ANDROID_LOG_VERBOSE, "FORK_WORKERS", "Error:  child thread %d terminated\n", result);
			_exit(111);
		}

		if (WEXITSTATUS(wstatus) != 0) {
			__android_log_print(ANDROID_LOG_VERBOSE, "FORK_WORKERS", "Error:  child thread %d retval %d\n", result, WEXITSTATUS(wstatus));
//printf("Child pid %d error retval:  %d\n", pidpool[i], WEXITSTATUS(wstatus));
			_exit(122);
		}
//printf("Thread %d retval %d\n", pidpool[i], WEXITSTATUS(wstatus));

	}

//printf("Clean exit\n");
	_exit(0);

}
