
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


long gettime_us() {

	struct timeval now;

	gettimeofday(&now, NULL);

	return now.tv_sec * 1000000 + now.tv_usec;

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
	long interval_us;

	struct timespec interval;
	long time_start_us;
	long time_delta_us;

//printf("Experiment 3\n");
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
	interval_us = 1000;
//TODO:  ^Correct?  Should *ADD* average time length of work slice TO the desired sleep period to get this

	for (outerloop = 0; outerloop < batchcount; outerloop++) {

		time_start_us = gettime_us();

		for (innerloop = 0; innerloop < loopcount / batchcount; innerloop++) {

//printf("Outerloop:  %f  Innerloop:  %f  Degree:  %f\n", outerloop, innerloop, degree);
			sum += sin(degree * PI / 180);
			degree++;

		}

		time_delta_us = gettime_us() - time_start_us;
		sleep_us = interval_us - time_delta_us;
		if (sleep_us < 0) {
printf("Err:  Negative sleep\n");
return 8;
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
	PRINTLOG("SQL_experiment_3:  loops:  %d  batches:  %d  interval_us:  %lu  sum:  %f", loopcount, batchcount, interval_us, sum);
	PRINTLOG("SQL_END");

	return 0;

}


