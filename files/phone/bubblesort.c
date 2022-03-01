
#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <linux/perf_event.h>
#include <linux/hw_breakpoint.h>
#include <sched.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

//int sparse = 1;
//int sparse = 4096;

#define PERFBUFF_SIZE 64


#define errtrap(error) (__errtrap(result, error, __LINE__))
void __errtrap(int result, const char* error, int line) {

	if (result == -1) {
		printf("Error in %s() on line %d:  %s\n", error, line, strerror(errno));
		_exit(errno);
	}
	return;

}


int perf_init(int type, int config_1, int config_2, int* perf_1_fd_ptr, int* perf_2_fd_ptr) {

	int perf_1_fd;
	int perf_2_fd;
	int result;
	struct perf_event_attr pea_struct;

	// Initialize HW performance monitoring structure:
	memset(&pea_struct, 0, sizeof(pea_struct));
	pea_struct.type = type;
	pea_struct.size = sizeof(struct perf_event_attr);
	pea_struct.config = config_1;
	pea_struct.sample_period = 0;  // Not using sample periods; will do manual collection
	pea_struct.sample_type = 0;  // ditto above
	pea_struct.read_format = PERF_FORMAT_GROUP;  // | PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING;
	// Some bitfields:
	pea_struct.disabled = 1;  // Disabled for now -- will start collection later
	pea_struct.inherit = 0;  // Yes, track both client and worker (n.b. documentation says this = 1 is incompatible with PERF_FORMAT_GROUP -- it is _not_; bug?)
	pea_struct.pinned = 0;  // N.b. pinned = 1 _is_ incompatible with PERF_FORMAT_GROUP -- either a bug in kernel or documentation?
	pea_struct.exclusive = 0;
	pea_struct.exclude_user = 0;
	pea_struct.exclude_kernel = 0;
	pea_struct.exclude_hv = 1;

	// Group leader for first of 2 events (cache references):
	result = syscall(__NR_perf_event_open, &pea_struct, 0, -1, -1, 0);
	errtrap("perf_event_open");
	perf_1_fd = result;

	if (config_2 > 0) {
		// Configure second event to monitor cache misses:
		pea_struct.config = config_2;
		pea_struct.disabled = 0;  // N.b. -- enabled, but dependent on status of leader event (initially disabled)
		// Include in monitoring group:
		result = syscall(__NR_perf_event_open, &pea_struct, 0, -1, perf_1_fd, 0);
		errtrap("perf_event_open");
		perf_2_fd = result;
	} else {
		perf_2_fd = -1;  // Magic val:  Invalid
	}

	// Enable perf:
	ioctl(perf_1_fd, PERF_EVENT_IOC_RESET, 0);
	ioctl(perf_1_fd, PERF_EVENT_IOC_ENABLE, 0);

	*perf_1_fd_ptr = perf_1_fd;
	*perf_2_fd_ptr = perf_2_fd;

	return 0;

}


int perf_finish(int perf_1_fd, int perf_2_fd, unsigned long* result_1_ptr, unsigned long* result_2_ptr) {

	int result;
	char perf_buff[PERFBUFF_SIZE];

	// Fetch cache data from perf:
	result = read(perf_1_fd, perf_buff, PERFBUFF_SIZE);
	errtrap("read");
	// Disable perf:
	ioctl(perf_1_fd, PERF_EVENT_IOC_DISABLE, 0);
	close(perf_1_fd);
	*result_1_ptr = ((unsigned long*)perf_buff)[1];
	if (perf_2_fd > 0) {
		close(perf_2_fd);
		*result_2_ptr = ((unsigned long*)perf_buff)[2];
	}

	return 0;

}


int pin_core(int core) {

	long tid;
	cpu_set_t set;
	int result;

	// Pin client thread to core(s):
	tid = syscall(__NR_gettid);
	CPU_ZERO(&set);
	CPU_SET(core, &set);
	result = sched_setaffinity(tid, sizeof(set), &set);
	errtrap("sched_setaffinity");
	printf("Thread tid %ld pinned to core %d\n", tid, core);

	return 0;

}


int zeroout(int* sortbuff, int buffsize, int sparse) {

	for (int i = 0; i < buffsize; i++) {
		sortbuff[i * sparse] = 0;
	}

	return 0;

}


int populate(int* sortbuff, int buffsize, int sparse) {

/*
	srand(time(NULL));

	for (int i = 0; i < buffsize; i++) {
		sortbuff[i * sparse] = rand();
	}
*/

	for (int i = 0; i < buffsize; i++) {
		sortbuff[i * sparse] = buffsize - i;
	}

	return 0;

}


int print(int* sortbuff, int buffsize, int sparse) {

	for (int i = 0; i < buffsize; i++) {
		printf("%d:  %d\n", i, sortbuff[i * sparse]);
	}

	return 0;

}


int sort(int* sortbuff, int buffsize, int sparse) {

	int swap;

	for (int i = 0; i < buffsize; i++) {
		for (int j = 0; j < buffsize - i - 1; j ++) {
			if (sortbuff[j * sparse] > sortbuff[(j + 1) * sparse]) {
				swap = sortbuff[j * sparse];
				sortbuff[j] = sortbuff[(j + 1) * sparse];
				sortbuff[(j + 1) * sparse] = swap;
			}
		}
	}

	return 0;

}


// Loop [buffsize] number of times, reading from random points in the array:
int randomread(int* sortbuff, int buffsize, int sparse, int loopcount) {

	int index;
	int sum;  // keep and return dummy value to prevent optimizing out

	srand(time(NULL));
	for (int i = 0; i < loopcount; i++) {

		index = rand() % buffsize;
		sum += sortbuff[index * sparse];
	}

	return sum;

}


// Loop [buffsize] number of times, writing to random points in the array:
int randomwrite(int* sortbuff, int buffsize, int sparse, int loopcount) {

	int index;

	srand(time(NULL));
	for (int i = 0; i < loopcount; i++) {

		index = rand() % buffsize;
		sortbuff[index * sparse] = 1;
	}

	return 0;

}


int test(int* sortbuff, int buffsize, int sparse) {

	for (int i = 0; i < buffsize - 1; i++) {
		if (sortbuff[i * sparse] > sortbuff[(i + 1) * sparse]) {
			printf("Unsorted\n");
			return -1;
		}
	}

	printf("Verified\n");
	return 0;

}


int main(int argc, char** argv) {

	printf("Hello World\n");

	int sortsize;
	int* sortbuff;
	char statm_filename[] = "/proc/self/statm"; 
	int result;
	int statm_fd;
	int iosize = 128;
	char iobuff[iosize];
	char* statm_save;
	char* token;
	int vmsize;
	int sparse;
	char trace_filename[] = "/sys/kernel/debug/tracing/trace_marker";
	int trace_fd;
	int perf_1_fd;
	int perf_2_fd;
	unsigned long result_1;
	unsigned long result_2;
	int coreno;
	int testtype;  // whether bubblesort, randomread, or randomwrite
	int dummysum;
	int loopcount;
	int type;
	int config_1;
	int config_2;

	type = PERF_TYPE_HARDWARE;
	config_1 = PERF_COUNT_HW_CPU_CYCLES;
	config_2 = -1;
//	config_1 = PERF_COUNT_HW_CACHE_REFERENCES;
//	config_2 = PERF_COUNT_HW_CACHE_MISSES;

//	type = PERF_TYPE_HW_CACHE;
//	config_1 = PERF_COUNT_HW_CACHE_DTLB | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16);
//	config_2 = PERF_COUNT_HW_CACHE_DTLB | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16);
//	config_1 = PERF_COUNT_HW_CACHE_DTLB | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16);
//	config_2 = PERF_COUNT_HW_CACHE_DTLB | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16);
//	config_1 = PERF_COUNT_HW_CACHE_LL | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16);
//	config_2 = PERF_COUNT_HW_CACHE_LL | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16);

//printf("type:  %d  conf1:  %d  conf2:  %d\n", type, config_1, config_2);
//_Exit(0);

	if (argc != 6) {
		printf("Err:  Wrong paramcount\n");
		_Exit(1);
	}

	sortsize = atoi(argv[1]);
	sparse = atoi(argv[2]);
	coreno = atoi(argv[3]);
	testtype = atoi(argv[4]);
	loopcount = atoi(argv[5]);
//	type = atoi(argv[6]);
//	config_1 = atoi(argv[7]);
//	config_2 = atoi(argv[8]);
	sortbuff = malloc(sizeof(int) * sortsize * sparse);

//	printf("Sort Buffer:  %p\n", sortbuff);
	printf("Sparse:  %d\n", sparse);
	printf("Sort Size:  %d\n", sortsize);
//	printf("Max:  %d\n", RAND_MAX);

	result = open(statm_filename, O_RDONLY);
	errtrap("open");
	statm_fd = result;

	result = open(trace_filename, O_WRONLY);
	errtrap("open");
	trace_fd = result;
//	printf("Trace fd:  %d\n", trace_fd);

	if (testtype == 1) {
		populate(sortbuff, sortsize, sparse);
//		print(sortbuff, sortsize, sparse);
	} else if ((testtype == 2) || (testtype == 3)) {
		zeroout(sortbuff, sortsize, sparse);
	} else {
		printf("Invalid test param\n");
		_exit(1);
	}

	if (coreno > 0) {
		pin_core(coreno);
	}

	snprintf(iobuff, iosize, "PARAMS:  Sortsize:  %d  Sparsity:  %d  Core:  %d  Test:  %d  Loop:  %d  Type:  %d  Conf1:  %d  Conf2:  %d\n", sortsize, sparse, coreno, testtype, loopcount, type, config_1, config_2);
	result = write(trace_fd, iobuff, iosize);
	errtrap("write");
	snprintf(iobuff, iosize, "{\"EVENT\":\"SQL_START\", \"thread\":0}\n");  // legacy flag
	result = write(trace_fd, iobuff, iosize);
	errtrap("write");
	perf_init(type, config_1, config_2, &perf_1_fd, &perf_2_fd);

	if (testtype == 1) {
		sort(sortbuff, sortsize, sparse);
	}
	if (testtype == 2) {
		dummysum = randomread(sortbuff, sortsize, sparse, loopcount);
	}
	if (testtype == 3) {
		randomwrite(sortbuff, sortsize, sparse, loopcount);
	}

	perf_finish(perf_1_fd, perf_2_fd, &result_1, &result_2);
	snprintf(iobuff, iosize, "CACHE_REFS:  %lu\n", result_1);
	result = write(trace_fd, iobuff, iosize);
	errtrap("write");
	snprintf(iobuff, iosize, "CACHE_MISSES:  %lu\n", result_2);
	result = write(trace_fd, iobuff, iosize);
	errtrap("write");
	snprintf(iobuff, iosize, "{\"EVENT\":\"SQL_END\", \"thread\":0}\n");  // legacy flag
	result = write(trace_fd, iobuff, iosize);
	errtrap("write");

	if (testtype == 1) {
//		print(sortbuff, sortsize, sparse);
		result = test(sortbuff, sortsize, sparse);
		errtrap("bubblesort_verity");
	}

	result = read(statm_fd, iobuff, iosize);
	errtrap("read");
	token = strtok_r(iobuff, " ", &statm_save);
	vmsize = atoi(token);

	printf("Memory:  %d\n", vmsize);
	printf("Dummy sum:  %d\n", dummysum);

	close(trace_fd);
	close(statm_fd);

	return 0;

}


