
#include <asm/unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>


int main(int argc, char** argv) {

	int result;
	int call;
	int lmin;
	int mmin;
	int bmin;
	int lmax;
	int mmax;
	int bmax;

	call = atoi(argv[1]);
	lmin = atoi(argv[2]);
	mmin = atoi(argv[3]);
	bmin = atoi(argv[4]);
	lmax = atoi(argv[5]);
	mmax = atoi(argv[6]);
	bmax = atoi(argv[7]);

	if ((call != 286) || (call != 450)) {
		return -2;
	}

	// TODO:  Resolve ordering issue
//	result = syscall(286, lmin, lmax, bmin, bmax);
	result = syscall(call, lmin, lmax, mmin, mmax, bmin, bmax);

	printf("Return value:  %d\n", result);

	if (result == -1) {
//		printf("Error:  %d %s\n", errno, strerror(errno));
		return -1;
	}

	return 0;

}

