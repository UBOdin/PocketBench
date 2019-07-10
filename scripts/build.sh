
# build and install

cd apps/Benchmark_withJson/
./gradlew installDebug

if [ $? -ne 0 ]; then
	echo "ERROR on build"
	exit 1
else
	echo "CLEAN"
fi

cd ../..
