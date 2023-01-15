
#include <android/log.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

#define OUTPUT_SIZE 256
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
	int trace_fd;
	char trace_filename[] = "/sys/kernel/debug/tracing/trace_marker";
	char output_buff[OUTPUT_SIZE];
	int output_len;
	int distribute_big;
	int distribute_little;
	long long loopcount;

	memset(&output_buff, 0, sizeof(output_buff));

	threadcount = atoi(argv[1]);
	if (threadcount > THREADMAX) {
			__android_log_print(ANDROID_LOG_VERBOSE, "FORK_WORKERS", "Error:  workers > MAX\n");
			_exit(133);
	}

	distribute_big = 0;
	if ((argv[3][0] == 'c') || (argv[3][0] == 'e') || (argv[3][0] == 'f')) {
		distribute_big = 1;
	}
	distribute_little = 0;
	if ((argv[3][1] == 'c') || (argv[3][1] == 'e') || (argv[3][1] == 'f')) {
		distribute_little = 1;
	}

	// Open handle to ftrace to save output:
	result = open(trace_filename, O_WRONLY);
	errtrap("open");
	trace_fd = result;
	PRINTLOG("FORK_START");

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
		if (i == 3) {
			newval = '1';
		}
		if (distribute_big == 1) {
			argv[3][0] = newval;
		}
		if (distribute_little == 1) {
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

	PRINTLOG("FORK_END");
	close(trace_fd);

	_exit(0);

}
