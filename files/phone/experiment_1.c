
#include <android/log.h>
#include <asm/unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define OUTPUT_SIZE 256
#define PI 3.14159265

#define PRINTLOG(...) output_len = snprintf( output_buff, OUTPUT_SIZE, __VA_ARGS__ ); \
	result = write(trace_fd, output_buff, output_len); \
	if (result == -1) { \
		errlog(); \
		return -6; \
	}


static void errlog() {

	__android_log_print(ANDROID_LOG_VERBOSE, "PocketData", "Error:  %d %s\n", errno, strerror(errno));
//printf("Error:  %d %s\n", errno, strerror(errno));

	return;

}


int main(int argc, char** argv) {

	printf("Hello World\n");

	int result;
	int trace_fd;
	char trace_filename[] = "/sys/kernel/debug/tracing/trace_marker";
	char output_buff[OUTPUT_SIZE];
	int output_len;

	long long loopcount;
	long long innercount;
	long long sum;

//printf("Experiment 1\n");
	// Open handle to ftrace to save output:
	result = open(trace_filename, O_WRONLY);
	if (result == -1) {
		errlog();
		return -4;
	}
	trace_fd = result;

	memset(&output_buff, 0, sizeof(output_buff));

	PRINTLOG("SQL_START");

	if (argc != 2) {
		printf("Err:  Missing loopcount\n");
		_Exit(1);
	}

	loopcount = atoi(argv[1]);
//printf("Loopcount:  %llu\n  size:  %lu\n", loopcount, sizeof(loopcount));
	if (loopcount <= 0) {
		printf("Err:  Bad loopcount\n");
		_Exit(1);
	}

	sum = 0;
	innercount = 20;
	for (long long i = 0; i < loopcount; i++) {
		for (long long j = 0; j < innercount; j++) {
			sum = sum + i + j;
		}
	}

//printf("loopcount:  %llu  sum:  %llu\n", loopcount, sum);
	PRINTLOG("SQL_experiment_1:  loopcount:  %lld  sum:  %lld\n", loopcount, sum);
	PRINTLOG("SQL_END");

	return 0;

}


