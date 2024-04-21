
#include <asm/unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>


int main(int argc, char** argv) {

	int result;

//	char strout[] = "This is a test.\n";

//	printf("Hello World\n");

//	printf("Testval:  %d\n", __NR_wait4);

//	result = syscall(285, 89);
//	result = syscall(285, 41, 43, 47, 53, 59);
//	result = syscall(243, 73, 7, 7, 7, 7, 7, 7, 7);
//	result = syscall(__NR_write, 1, strout, sizeof(strout));
//	result = write(1, strout, sizeof(strout));

	int lmin;
	int lmax;
	int bmin;
	int bmax;

	// TODO:  Resolve ordering issue
	lmin = atoi(argv[1]);
	lmax = atoi(argv[3]);
	bmin = atoi(argv[2]);
	bmax = atoi(argv[4]);

	result = syscall(286, lmin, lmax, bmin, bmax);

	if (result == -1) {
//		printf("Error:  %d %s\n", errno, strerror(errno));
		return -1;
	}

//	printf("Return value:  %d\n", result);

	return 0;

}

