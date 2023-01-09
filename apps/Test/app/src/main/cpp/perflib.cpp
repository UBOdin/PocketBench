
#include <android/log.h>
#include <asm/unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <jni.h>
#include <linux/perf_event.h>
#include <linux/hw_breakpoint.h>
#include <stdio.h>
//#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define PERFBUFF_SIZE 64
#define OUTPUT_SIZE 256


static int perf_cycles_fd = 0;


static void errlog() {

	__android_log_print(ANDROID_LOG_VERBOSE, "PocketData", "Error:  %d %s\n", errno, strerror(errno));

	return;

}


extern "C" JNIEXPORT jint JNICALL Java_com_example_test_MetaTest_startcount(JNIEnv *env, jclass clazz, jint param) {

	int result;
	struct perf_event_attr pea_struct;

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
	pea_struct.exclude_kernel = 1;  // And kernel
	pea_struct.exclude_hv = 1;  // NOT HV (if any)

	// Open perf fd:
	result = syscall(__NR_perf_event_open, &pea_struct, 0, -1, -1, 0);
	if (result == -1) {
		errlog();
		return -2;
	}
	perf_cycles_fd = result;

	// Enable collection:
	ioctl(perf_cycles_fd, PERF_EVENT_IOC_RESET, 0);
	ioctl(perf_cycles_fd, PERF_EVENT_IOC_ENABLE, 0);

	return 0;

}


extern "C" JNIEXPORT jint JNICALL Java_com_example_test_MetaTest_stopcount(JNIEnv *env, jclass clazz, jint param) {

	int result;
	char perf_buff[PERFBUFF_SIZE];
	int trace_fd;
	char trace_filename[] = "/sys/kernel/debug/tracing/trace_marker";
	char output_buff[OUTPUT_SIZE];
	int output_len;
	unsigned long cycles;

	// Errtrap uninitialized fd:
	if (perf_cycles_fd <= 0) {
		return -1;
	}

	// Collect results:
	result = read(perf_cycles_fd, perf_buff, PERFBUFF_SIZE);
	if (result == -1) {
		errlog();
		return -3;
	}

	// Disable collection:
	ioctl(perf_cycles_fd, PERF_EVENT_IOC_DISABLE, 0);

	// Sanity (should be collecting 1 item):
	if (((unsigned long*)perf_buff)[0] != 1) {
		__android_log_print(ANDROID_LOG_VERBOSE, "PocketData", "Error:  Bad perf itemcount\n");
		return -5;
	}

	// Open handle to ftrace to save output:
	result = open(trace_filename, O_WRONLY);
	if (result == -1) {
		errlog();
		return -4;
	}
	trace_fd = result;

	memset(&output_buff, 0, sizeof(output_buff));
	cycles = ((unsigned long*)perf_buff)[1];
	output_len = snprintf(output_buff, OUTPUT_SIZE, "Cycle data:  %lu", cycles);

	result = write(trace_fd, output_buff, output_len);
	if (result == -1) {
		errlog();
		return -6;
	}

	// Cleanup:
	close(perf_cycles_fd);
	close(trace_fd);
	perf_cycles_fd = 0;  // signal tracing is off

	return 0;

}


