
#include <android/log.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
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
//	char trace_filename[] = "/sys/kernel/debug/tracing/trace_marker";
	char trace_filename[] = "/sys/kernel/tracing/trace_marker";
	char output_buff[OUTPUT_SIZE];
	int output_len;
	int bit;
	int bitmask;

	memset(&output_buff, 0, sizeof(output_buff));
	memset(&pidpool, 0, sizeof(pidpool));

	// Open handle to ftrace to save output:
	result = open(trace_filename, O_WRONLY);
	errtrap("open");
	trace_fd = result;
	PRINTLOG("FORK_START");

	threadcount = 8;
	bit = 1;
	bitmask = strtoul(argv[3], NULL, 16);

	for (int i = 0; i < threadcount; i++) {
		snprintf(argv[3], 3, "%02x", bit);
		if ((bitmask & bit) != 0) {
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
		bit = bit << 1;
	}

	for (int i = 0; i < threadcount; i++) {
		if (pidpool[i] != 0) {
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
	}

	PRINTLOG("FORK_END");
	close(trace_fd);

	_exit(0);

}
