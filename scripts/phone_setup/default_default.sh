# setup phone, default cache, default wait

adb root
adb push files/phone/benchmark_50.sh /data/benchmark.sh
adb push files/phone/removeBenchmarkData.sh /data/removeBenchmarkData.sh
adb push files/phone/preBenchmark.sh /data/preBenchmark.sh
