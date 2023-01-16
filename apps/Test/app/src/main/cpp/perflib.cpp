
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

#define IDLEBUFF_SIZE 256
#define NAMEBUFF_SIZE 128
#define CPU_MAX 8
#define CPU_STATES 3
#define PERFBUFF_SIZE 64

#define OUTPUT_SIZE 256

#define CYCLEBUFF_SIZE 256

#define PRINTLOG(...) \
	retval = dprintf(trace_fd, __VA_ARGS__ ); \
	errtrap("dprintf");

//	__android_log_print(ANDROID_LOG_VERBOSE, "MACROBENCH", "Log:  %s\n", output_buff);
// TODO:  readd aosp logging

static int trace_fd;
static int cpu_arr[CPU_MAX];


#define errtrap(error) (__errtrap(retval, error, __LINE__))
void __errtrap(int retval, const char* error, int line) {

	if (retval == -1) {
		__android_log_print(ANDROID_LOG_VERBOSE, "MACROBENCH", "Error:  %d %s\n", errno, strerror(errno));
		_exit(errno);
	}
	return;

}


static int get_idle(int param) {

	int retval;
	int idle_fd;
	char name_buff[NAMEBUFF_SIZE];
	char idle_buff[IDLEBUFF_SIZE];
	int offset;

	memset(idle_buff, 0x20, sizeof(idle_buff));
	offset = 0;

	for (int cpu = 0; cpu < CPU_MAX; cpu++) {
		for (int state = 0; state < CPU_STATES; state++) {
			snprintf(name_buff, NAMEBUFF_SIZE, "/sys/devices/system/cpu/cpu%d/cpuidle/state%d/time", cpu, state);
			retval = open(name_buff, O_RDONLY);
			errtrap("open");
			idle_fd = retval;
			retval = read(idle_fd, idle_buff + offset, IDLEBUFF_SIZE - offset);
			errtrap("read");
			close(idle_fd);
			offset += retval;
			idle_buff[offset - 1] = ' ';  // Delimit by space
		}
	}
	idle_buff[offset - 1] = '\0';  // nullterm the string
	PRINTLOG("Idle data #%d:  %s", param, idle_buff);

	return 0;

}



extern "C" JNIEXPORT jint JNICALL Java_com_example_test_MetaTest_startcount(JNIEnv *env, jclass clazz, jint param) {

	int retval;
	struct perf_event_attr pea_struct;
	int pid;
	char trace_filename[] = "/sys/kernel/debug/tracing/trace_marker";
	char output_buff[OUTPUT_SIZE];
	int output_len;

	// Open handle to ftrace to save output:
	retval = open(trace_filename, O_WRONLY);
	errtrap("open");
	trace_fd = retval;
	PRINTLOG("Starting perf collection %d", param);

	// Open array of perf fds, for each CPU:
	for (int i = 0; i < CPU_MAX; i++) {

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

		// Get perf fd to track all tasks (-1) on a given CPU (i):
		pid = -1;
		retval = syscall(__NR_perf_event_open, &pea_struct, pid, i, -1, 0);
		errtrap("syscall");
		cpu_arr[i] = retval;
		// Enable collection:
		ioctl(retval, PERF_EVENT_IOC_RESET, 0);
		ioctl(retval, PERF_EVENT_IOC_ENABLE, 0);

	}

	get_idle(param);

	return 0;

}


extern "C" JNIEXPORT jint JNICALL Java_com_example_test_MetaTest_stopcount(JNIEnv *env, jclass clazz, jint param) {

	int retval;
	char perf_buff[PERFBUFF_SIZE];
	char output_buff[OUTPUT_SIZE];
	int output_len;
	unsigned long cycles;
	int perf_fd;
	char cycle_buff[CYCLEBUFF_SIZE];
	int offset;

	memset(cycle_buff, 0x20, sizeof(cycle_buff));
	offset = 0;

	for (int i = 0; i < CPU_MAX; i++) {

		perf_fd = cpu_arr[i];
		// Errtrap uninitialized fd:
		if (perf_fd <= 2) {
			return -2;
		}
		// Collect results:
		retval = read(perf_fd, perf_buff, PERFBUFF_SIZE);
		errtrap("read");
		// Sanity (should be collecting 1 item):
		if (((unsigned long*)perf_buff)[0] != 1) {
			return -3;
		}
		cycles = ((unsigned long*)perf_buff)[1];
		retval = snprintf(cycle_buff + offset, CYCLEBUFF_SIZE - offset, "%lu ", cycles);
		offset += retval;

	}
	cycle_buff[offset - 1] = '\0';  // remove last added space delimiter
	PRINTLOG("Cycle data #%d:  %s", param, cycle_buff);

	get_idle(param);

	// Cleanup, upon request:
	if (param > 100) {
		for (int i = 0; i < CPU_MAX; i++) {
			// Disable collection:
			ioctl(perf_fd, PERF_EVENT_IOC_DISABLE, 0);
			// Cleanup:
			close(perf_fd);
		}
		PRINTLOG("End perf collection %d", param);
		close(trace_fd);
	}

	return 0;

}


