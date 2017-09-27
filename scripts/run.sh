# run benchmark
adb -s $1 shell pm disable com.example.benchmark_withjson
sleep 1
adb -s $1 shell pm enable com.example.benchmark_withjson

printf "Rebooting and running benchmark on device %s\n" $1

adb -s $1 reboot
sleep 70s
adb -s $1 root
sleep 1m
adb -s $1 shell sh /data/removeBenchmarkData.sh
adb -s $1 shell sh /data/preBenchmark.sh #create database 
adb -s $1 shell pm disable com.example.benchmark_withjson
sleep 5
adb -s $1 shell pm enable com.example.benchmark_withjson
adb -s $1 shell sh /data/benchmark.sh #run queries

# pull log
adb -s $1 pull /data/trace.log
# $2 = workload (A, B, C etc.); $3 = DB (sql, bdb, bdb100)
filename="YCSB_Workload${3}TimingA${2}.log"
mv trace.log logs/$filename
gzip logs/$filename
sleep 1
printf "FILENAME:  %s\n" "$filename"

printf "RESULTS:"
adb shell cat /data/results.txt

printf "Completed benchmark for device %s\n" $1

