# run benchmark
adb shell pm disable com.example.benchmark_withjson
sleep 1
adb shell pm enable com.example.benchmark_withjson
adb reboot
sleep 70s
adb root
sleep 2m
adb shell sh /data/removeBenchmarkData.sh
adb shell sh /data/preBenchmark.sh #create database 
adb shell pm disable com.example.benchmark_withjson
sleep 5
adb shell pm enable com.example.benchmark_withjson
adb shell sh /data/benchmark.sh #run queries

# pull log
adb pull /data/trace.log
mv trace.log logs/YCSB_WorkloadIB_TimingAbdb100.log
gzip logs/YCSB_WorkloadIB_TimingAbdb100.log
sleep 1

adb shell pm disable com.example.benchmark_withjson
sleep 1
adb shell pm enable com.example.benchmark_withjson
