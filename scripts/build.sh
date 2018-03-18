
# Copy over timing files

rm -rf apps/Benchmark_withJson/app/src/main/res/raw
cp -r files/json/raw apps/Benchmark_withJson/app/src/main/res/

# build and install

cd apps/Benchmark_withJson/
./gradlew installDebug

if [ $? -ne 0 ]; then
	echo "ERROR"
else
	echo "CLEAN"
fi

cd ../..
