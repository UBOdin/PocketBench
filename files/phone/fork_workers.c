
#include <android/log.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

#define THREADMAX 128

#define PRINTLOG(...) output_len = snprintf( output_buff, OUTPUT_SIZE, __VA_ARGS__ ); \
	result = write(trace_fd, output_buff, output_len); \
	errtrap("write");


#define errtrap(error) (__errtrap(result, error, __LINE__))
void __errtrap(int result, const char* error, int line) {

	if (result == -1) {
		printf("Error in %s() on line %d:  %s\n", error, line, strerror(errno));
		__android_log_print(ANDROID_LOG_VERBOSE, "Microbench", "Error:  %d %s on line %d\n", errno, strerror(errno), line);
		_exit(errno);
	}
	return;

}


int main(int argc, char** argv) {

	int result;
	int threadcount;
	int pidpool[THREADMAX];
	int wstatus;

	threadcount = atoi(argv[1]);
	if (threadcount > THREADMAX) {
			__android_log_print(ANDROID_LOG_VERBOSE, "FORK_WORKERS", "Error:  workers > MAX\n");
			_exit(133);
	}


	int distribute_big = 0;
	if (argv[3][0] == 'e') {
		distribute_big = 1;
	}
	int distribute_little = 0;
	if (argv[3][1] == 'e') {
		distribute_little = 1;
	}

	for (int i = 0; i < threadcount; i++) {

		char newval;
		if (i == 0) {
			newval = '8';
		}
		if (i == 1) {
			newval = '4';
		}
		if (i == 2) {
			newval = '2';
		}
		if (distribute_big == 1) {
//			printf("Replaced 'e' with '%c' in big cores\n", newval);
			argv[3][0] = newval;
		}
		if (distribute_little == 1) {
//			printf("Replaced 'e' with '%c' in little cores\n", newval);
			argv[3][1] = newval;
		}

		result = fork();
		errtrap("fork");
		if (result == 0) {
			result = execv((const char*)argv[2], argv + 2);
			errtrap("execv");
			_exit(99);  // Never gets here
		}
		if (result > 0) {
			pidpool[i] = result;
		}
	}

	for (int i = 0; i < threadcount; i++) {
		result = waitpid(pidpool[i], &wstatus, 0);
		errtrap("waitpid");
		if (WIFEXITED(wstatus) == 0) {
			__android_log_print(ANDROID_LOG_VERBOSE, "Microbench Parent", "Error:  pid %d terminated\n", result);
			_exit(111);
		}
		if (WEXITSTATUS(wstatus) != 0) {
			__android_log_print(ANDROID_LOG_VERBOSE, "Microbench Parent", "Error:  pid %d retval %d\n", result, WEXITSTATUS(wstatus));
			_exit(122);
		}
	}

	_exit(0);

}
