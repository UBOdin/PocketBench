# run benchmark
adb -s $1 shell pm disable com.example.benchmark_withjson
sleep 1
adb -s $1 shell pm enable com.example.benchmark_withjson

printf "Rebooting and running benchmark on device %s\n" $1

adb -s $1 reboot
sleep 70s
adb -s $1 root
sleep 2m
adb -s $1 shell sh /data/removeBenchmarkData.sh
adb -s $1 shell sh /data/preBenchmark.sh #create database 
adb -s $1 shell pm disable com.example.benchmark_withjson
sleep 5
adb -s $1 shell pm enable com.example.benchmark_withjson
adb -s $1 shell sh /data/benchmark.sh #run queries

# pull log
adb -s $1 pull /data/trace.log
mv trace.log logs/YCSB_WorkloadIB_TimingAbdb100.log
gzip logs/YCSB_WorkloadIB_TimingAbdb100.log
sleep 1

adb -s $1 shell pm disable com.example.benchmark_withjson
sleep 1
adb -s $1 shell pm enable com.example.benchmark_withjson

printf "Completed benchmark for device %s\n" $1

