

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

// TODO:  Parameterize size
//	int buffsize = 100;

	int buffsize;
	int* sortbuff;
	char statm_filename[] = "/proc/self/statm"; 
	int result;
	int statm_fd;
	int statm_buffsize = 64;
	char statm_buffer[statm_buffsize];
	char* statm_save;
	char* token;
	int vmsize;
	int sparse;

	if (argc != 3) {
		printf("Err:  Wrong paramcount\n");
		_Exit(1);
	}

	buffsize = atoi(argv[1]);
	sparse = atoi(argv[2]);
	sortbuff = malloc(sizeof(int) * buffsize * sparse);

//	printf("Buffer:  %p\n", sortbuff);
	printf("Sparse:  %d\n", sparse);
	printf("Size:  %d\n", buffsize);
//	printf("Max:  %d\n", RAND_MAX);

	result = open(statm_filename, O_RDONLY);
	if (result == -1) {
		printf("Err on open()\n");
		_Exit(1);
	}
	statm_fd = result;

	populate(sortbuff, buffsize, sparse);
//	print(sortbuff, buffsize, sparse);
	sort(sortbuff, buffsize, sparse);
//	print(sortbuff, buffsize, sparse);
	test(sortbuff, buffsize, sparse);

	result = read(statm_fd, statm_buffer, statm_buffsize);
	if (result == -1) {
		printf("Err on read()\n");
		_Exit(1);
	}
	token = strtok_r(statm_buffer, " ", &statm_save);
	vmsize = atoi(token);

	printf("Memory:  %d\n", vmsize);

	close(statm_fd);

	return 0;

}


