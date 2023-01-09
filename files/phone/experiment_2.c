
#include <android/log.h>
#include <asm/unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/perf_event.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#define OUTPUT_SIZE 256
#define PERFBUFF_SIZE 64

#define PRINTLOG(...) output_len = snprintf( output_buff, OUTPUT_SIZE, __VA_ARGS__ ); \
	result = write(trace_fd, output_buff, output_len); \
	errtrap("write");


#define errtrap(error) (__errtrap(result, error, __LINE__))
void __errtrap(int result, const char* error, int line) {

	if (result == -1) {
		printf("Error in %s() on line %d:  %s\n", error, line, strerror(errno));
		__android_log_print(ANDROID_LOG_VERBOSE, "Microbench", "Error:  %d %s\n", errno, strerror(errno));
		_exit(errno);
	}
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
	struct perf_event_attr pea_struct;
	int perf_cycles_fd;
	char perf_buff[PERFBUFF_SIZE];
	unsigned long cycles;

	long long loopcount;
	long long batchcount;
	long long innercount;
	long long sum;
	long sleep_ms;

	struct timespec interval;

	memset(&output_buff, 0, sizeof(output_buff));

	// Initialize HW performance monitoring structure:
	memset(&pea_struct, 0, sizeof(pea_struct));
	pea_struct.type = PERF_TYPE_HARDWARE;
	pea_struct.size = sizeof(struct perf_event_attr);
	pea_struct.config = PERF_COUNT_HW_CPU_CYCLES;
	pea_struct.sample_period = 0;  // Not using sample periods; will do manual collection
	pea_struct.sample_type = 0;  // ditto above
	pea_struct.read_format = PERF_FORMAT_GROUP;  // | PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING;
	// Some bitfields:
	pea_struct.disabled = 1;  // Disabled for now -- will start collection later
	pea_struct.inherit = 0;  // No -- main thread only (n.b. documentation says this = 1 is incompatible with PERF_FORMAT_GROUP -- it is _not_; bug?)
	pea_struct.pinned = 0;  // N.b. pinned = 1 _is_ incompatible with PERF_FORMAT_GROUP -- either a bug in kernel or documentation?
	pea_struct.exclusive = 0;
	pea_struct.exclude_user = 0;  // Track userspace
	pea_struct.exclude_kernel = 0;  // And kernel
	pea_struct.exclude_hv = 1;  // NOT HV (if any)

	// Open perf fd:
	result = syscall(__NR_perf_event_open, &pea_struct, 0, -1, -1, 0);
	errtrap("syscall");
	perf_cycles_fd = result;

	// Open handle to ftrace to save output:
	result = open(trace_filename, O_WRONLY);
	errtrap("open");
	trace_fd = result;

	PRINTLOG("SQL_START");

	if (argc != 4) {
		printf("Err:  Incorrect params\n");
		_Exit(1);
	}

	loopcount = atoi(argv[1]);
	if (loopcount <= 0) {
		printf("Err:  Bad loopcount\n");
		_Exit(1);
	}
	batchcount = atoi(argv[2]);
	sleep_ms = atoi(argv[3]);

	// Enable collection:
	ioctl(perf_cycles_fd, PERF_EVENT_IOC_RESET, 0);
	ioctl(perf_cycles_fd, PERF_EVENT_IOC_ENABLE, 0);

	sum = 0;
	innercount = 20;
	long long i = 0;
	while (1) {

		if (i >= batchcount) {
			break;
		}

		for (long long j = 0; j < loopcount / batchcount; j++) {
			for (long long k = 0; k < innercount; k++) {
				sum = sum + i + j + k;
			}
		}

		interval.tv_sec = 0;
		interval.tv_nsec = sleep_ms * 1000 * 1000;
		if (sleep_ms > 0) {
			result = nanosleep(&interval, NULL);
			errtrap("nanosleep");
		}

		i++;
	}
	printf("Iter count:  %lld\n", i);

	// Disable collection:
	ioctl(perf_cycles_fd, PERF_EVENT_IOC_DISABLE, 0);

	PRINTLOG("SQL_experiment_2:  loopcount:  %lld  batchcount:  %lld  sleep_ms:  %ld  sum:  %lld", loopcount, batchcount, sleep_ms, sum);
	PRINTLOG("SQL_END");

	// Collect results:
	result = read(perf_cycles_fd, perf_buff, PERFBUFF_SIZE);
	errtrap("read");

	// Sanity (should be collecting 1 item):
	if (((unsigned long*)perf_buff)[0] != 1) {
		__android_log_print(ANDROID_LOG_VERBOSE, "PocketData", "Error:  Bad perf itemcount\n");
		return -5;
	}

	cycles = ((unsigned long*)perf_buff)[1];
	PRINTLOG("Cycle data:  %lu", cycles);

	close(perf_cycles_fd);
	close(trace_fd);

	return 0;

}


