# setup phone, 100 cache, 100 wait

adb root
adb push files/phone/benchmark_100.sh /data/benchmark.sh
adb push files/phone/removeBenchmarkData_bdb100.sh /data/removeBenchmarkData.sh
adb push files/phone/preBenchmark.sh /data/preBenchmark.sh
adb push files/bdb/100MB/DB_CONFIG /data/
