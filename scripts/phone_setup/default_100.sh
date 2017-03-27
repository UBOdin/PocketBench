# setup phone, default cache, 100 wait

adb root
adb push files/phone/benchmark_100.sh /data/benchmark.sh
adb push files/phone/removeBenchmarkData.sh /data/removeBenchmarkData.sh
adb push files/phone/preBenchmark.sh /data/preBenchmark.sh
