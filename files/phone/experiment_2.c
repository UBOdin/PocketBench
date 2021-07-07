
#include <android/log.h>
#include <asm/unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#define OUTPUT_SIZE 256
#define PI 3.14159265

#define PRINTLOG(...) output_len = snprintf( output_buff, OUTPUT_SIZE, __VA_ARGS__ ); \
	result = write(trace_fd, output_buff, output_len); \
	if (result == -1) { \
		errlog(); \
		return 6; \
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
	long long batchcount;
	long long innercount;
	long long sum;
	long sleep_us;

	struct timespec interval;

//printf("Experiment 2\n");
	// Open handle to ftrace to save output:
	result = open(trace_filename, O_WRONLY);
	if (result == -1) {
		errlog();
		return 4;
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

	batchcount = 50000;
	sleep_us = 100;

	sum = 0;
	innercount = 20;
	for (long long i = 0; i < batchcount; i++) {
		for (long long j = 0; j < loopcount / batchcount; j++) {
			for (long long k = 0; k < innercount; k++) {
				sum = sum + i + j + k;
			}
		}
		interval.tv_sec = 0;
		interval.tv_nsec = sleep_us * 1000;
		result = nanosleep(&interval, NULL);
		if (result == -1) {
			errlog();
			return 7;
		}
	}

//printf("Degrees:  %f\n", degree);
	PRINTLOG("SQL_experiment_2:  loopcount:  %lld  batchcount:  %lld  sleep_us:  %ld  sum:  %lld", loopcount, batchcount, sleep_us, sum);
	PRINTLOG("SQL_END");

	return 0;

}


