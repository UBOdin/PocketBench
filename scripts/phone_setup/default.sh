# setup phone, default cache

printf "Pushing files for device %s\n" $1
 
adb -s $1 root
adb -s $1 push files/phone/benchmark.sh /data/benchmark.sh
adb -s $1 push files/phone/removeBenchmarkData.sh /data/removeBenchmarkData.sh
adb -s $1 push files/phone/preBenchmark.sh /data/preBenchmark.sh
