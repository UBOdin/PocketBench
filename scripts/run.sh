#!/bin/bash
# run benchmark
adb -s $1 shell pm disable com.example.benchmark_withjson
sleep 1
adb -s $1 shell pm enable com.example.benchmark_withjson

printf "Rebooting and running benchmark on device %s\n" $1

adb -s $1 reboot
adb -s $1 wait-for-device
sleep 40
printf "Rebooted\n"
adb root
sub=""
while [ "$sub" != "uid=0(" ]; do
	sleep 5
	var=$(adb shell id)
	sub=${var%%root*}  # var:4:1
	printf ".\n"
done
sleep 40
printf "Rooted\n"

adb -s $1 shell sh /data/removeBenchmarkData.sh
adb -s $1 shell sh /data/preBenchmark.sh $2 $3 $4 $5 $6 $7 #create database
adb -s $1 shell pm disable com.example.benchmark_withjson
sleep 5
adb -s $1 shell pm enable com.example.benchmark_withjson

sleep 15 # Let phone settle before starting script:
echo "Starting phone script"
adb -s $1 shell sh /data/benchmark.sh $4 $5 #run queries -- specify governor ($4) and speed ($5)
#adb shell "nohup > data/output.out sh /data/benchmark.sh $4 $5 &" &

echo "WAITING -- START MONSOON"
# Block to allow manual phone disconnect during run for energy measurement:
#sleep 30

# Block until phone is manually reconnected after measurement:
result="1"
while [ "$result" = "1" ]; do
	sleep 5
	echo "Try... ${result}"
	#result=$(adb shell id 2>&1)
	adb shell id 2>&1
	result="$?"
done

# Get results (and trap for error):
result="$(adb shell cat /data/results.txt)"
#error=${result:0:3}
#if [ ${error} == "ERR" ]; then
#	echo "Error on phone:  $result"
#	exit 1
#fi

# pull log
adb -s $1 pull /data/trace.log
# $2 = DB (sql, bdb, bdb100); $3 = workload (A, B, C etc.); $6 = delay (lognormal etc.)
if [ "$6" = "lognormal" ]; then
	delay="log"
else
	delay="$6"
fi
filename="YCSB_${2}_${3}_${delay}_${4}_${5}"
#filename="YCSB_Workload${3}_TimingA${2}.log" # old style filename
mv trace.log logs/$filename
gzip logs/$filename
sleep 1
printf "FILENAME:  %s\n" "$filename"

echo "RESULTS: $result"

printf "Completed benchmark for device %s\n" $1

