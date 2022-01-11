

#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>


//int sparse = 1;
//int sparse = 4096;


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


int test(int* sortbuff, int buffsize, int sparse) {

	for (int i = 0; i < buffsize - 1; i++) {
		if (sortbuff[i * sparse] > sortbuff[(i + 1) * sparse]) {
			printf("Unsorted\n");
			return 1;
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
	int iosize = 64;
	char iobuff[iosize];
	char* statm_save;
	char* token;
	int vmsize;
	int sparse;
	char trace_filename[] = "/sys/kernel/debug/tracing/trace_marker";
	int trace_fd;

	if (argc != 3) {
		printf("Err:  Wrong paramcount\n");
		_Exit(1);
	}

	sortsize = atoi(argv[1]);
	sparse = atoi(argv[2]);
	sortbuff = malloc(sizeof(int) * sortsize * sparse);

//	printf("Sort Buffer:  %p\n", sortbuff);
	printf("Sparse:  %d\n", sparse);
	printf("Sort Size:  %d\n", sortsize);
//	printf("Max:  %d\n", RAND_MAX);

	result = open(statm_filename, O_RDONLY);
	if (result == -1) {
		printf("Err on statm open():  %d  %s\n", errno, strerror(errno));
		_Exit(1);
	}
	statm_fd = result;

	result = open(trace_filename, O_WRONLY);
	if (result == -1) {
		printf("Err on trace open():  %d %s\n", errno, strerror(errno));
		_Exit(1);
	}
	trace_fd = result;


printf("Trace fd:  %d\n", trace_fd);

	populate(sortbuff, sortsize, sparse);
//	print(sortbuff, sortsize, sparse);
	snprintf(iobuff, iosize, "{\"EVENT\":\"SQL_START\", \"thread\":0}\n");  // legacy flag
	result = write(trace_fd, iobuff, iosize);
	if (result == -1) {
		printf("Err on trace write() 1:  %d %s\n", errno, strerror(errno));
		_Exit(1);
	}
	sort(sortbuff, sortsize, sparse);
	snprintf(iobuff, iosize, "{\"EVENT\":\"SQL_END\", \"thread\":0}\n");  // legacy flag
	result = write(trace_fd, iobuff, iosize);
	if (result == -1) {
		printf("Err on trace write() 2:  %d %s\n", errno, strerror(errno));
		_Exit(1);
	}
	snprintf(iobuff, iosize, "Cycle data\n");  // legacy flag
	result = write(trace_fd, iobuff, iosize);
	if (result == -1) {
		printf("Err on trace write() 3:  %d %s\n", errno, strerror(errno));
		_Exit(1);
	}
//	print(sortbuff, sortsize, sparse);
	test(sortbuff, sortsize, sparse);

	result = read(statm_fd, iobuff, iosize);
	if (result == -1) {
		printf("Err on statm read():  %d %s\n", errno, strerror(errno));
		_Exit(1);
	}
	token = strtok_r(iobuff, " ", &statm_save);
	vmsize = atoi(token);

	printf("Memory:  %d\n", vmsize);

	close(trace_fd);
	close(statm_fd);

	return 0;

}


