#!/bin/bash
# run benchmark

printf "Rebooting and running benchmark on device %s\n" $1

adb -s $1 reboot
adb -s $1 wait-for-device
sleep 10
printf "Rebooted\n"
adb -s $1 root
adb -s $1 wait-for-device
sleep 10
printf "Rooted\n"

adb -s $1 shell sh /data/preBenchmark.sh $2 $3 $4 $5 $6 $7 #create database

sleep 15 # Let phone settle before starting script:
echo "Starting phone script"
adb -s $1 shell sh /data/start_benchmark.sh $4 $5 &

echo "WAITING -- START MONSOON"
# Block to allow manual phone disconnect during run for energy measurement:
#sleep 30

sleep 5 # Make sure on-phone script is running before cutting power:
ykushcmd -d 1

sleep 30 # Make sure (1) power is cut and (2) phone has finished :30 block before blocking on wifi wakeup ping:
./server.exe 2016
result=$?
ykushcmd -u 1
if [ "$result" != "0" ]; then
	echo "Error on wifi block"
	exit 3
else
	echo "OK on wifi block"
fi

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
adb pull /data/results.txt
result="$(cat results.txt)"
echo "Benchmark results:  $result"
# Trap for error on phone script:
if [ "$result" = "ERR" ]; then
	echo "Error on phone script"
	exit 1
else
	echo "OK on phone script" 
fi

# Sanity check:  Verify benchmark was run on-battery:
adb pull /data/power.txt
result2="$(cat power.txt)"
echo "BATTERY:  $result2"
adb shell rm /data/power.txt
if [ "$result2" != "  AC powered: false" ]; then
	echo "Error on battery power"
	exit 2
else
	echo "OK on battery power"
fi


# pull log
adb -s $1 pull /data/trace.log
# $2 = DB (sql, bdb, bdb100); $3 = workload (A, B, C etc.); $6 = delay (lognormal etc.)
if [ "$6" = "lognormal" ]; then
	delay="log"
else
	delay="$6"
fi
timestamp="$(date +%Y%m%d%H%M%S)"
#filename="YCSB_${2}_${3}_${delay}_${4}_${5}_$timestamp"
filename="YCSB_${2}_${3}_${delay}_${4}_${5}"
#filename="YCSB_Workload${3}_TimingA${2}.log" # old style filename
mv trace.log logs/$filename
gzip logs/$filename
sleep 1
printf "FILENAME:  %s\n" "$filename"

echo "RESULTS: $result"

printf "Completed benchmark for device %s\n" $1

# Sanity check:  Verify main phone script matches:
adb pull /data/start.txt
result1="$(cat start.txt)"
echo "Script pid:  $result1"
adb shell rm /data/start.txt
if [ "$result1" != "  AC powered: false" ]; then
	echo "Error on script pid"
	#exit 1
else
	echo "OK on script pid"
fi


#TODO:
# (7) parameterize TCP wifi wait port
# (9) add socket apps to repo and push in script
# (10) adb:  when USB connection is cut, the foreground proc dies, even if run with sighup -- ?! (which signal?  kill?)
# (11) adb:  proc on desktop blocks until all phone procs exit, even if already reparented to init -- ?!
# (12) Fix ERR result from results.txt
# (13) Remove inefficient DB populate code in java app
# (14) Clean-up socket apps (e.g. printing "Exit Clean" to console => nohup)
# (15) Consistincy-ize the -s $1 phone serial number stuff
# (16) Battery stats => ftrace logfile
# (17) logcat events -- re:  bimodal latency

# re:  blocking syscalls and spurious wakeup -- why while () and not if ()?
# syncing accept() and connect()

