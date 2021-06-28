
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

	int loopcount;
	double degree;
	double sum;
	int batchcount;
	int innerloop;
	int outerloop;
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
	if (loopcount <= 0) {
		printf("Err:  Bad loopcount\n");
		_Exit(1);
	}
//printf("Loopcount:  %d\n", loopcount);

	batchcount = 5000;
	degree = 0;
	sleep_us = 1000;

	for (outerloop = 0; outerloop < batchcount; outerloop++) {

		for (innerloop = 0; innerloop < loopcount / batchcount; innerloop++) {

//printf("Outerloop:  %f  Innerloop:  %f  Degree:  %f\n", outerloop, innerloop, degree);
			sum += sin(degree * PI / 180);
			degree++;

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
	PRINTLOG("SQL_experiment_2:  loops:  %d  batches:  %d  sleep_us:  %ld  sum:  %f", loopcount, batchcount, sleep_us, sum);
	PRINTLOG("SQL_END");

	return 0;

}


