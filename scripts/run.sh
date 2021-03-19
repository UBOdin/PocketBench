#!/bin/bash
# run benchmark

wakeport="2017"  # Phone-client wifi wakeup port
# $2 = DB (sql, bdb, bdb100); $3 = workload (A, B, C etc.); $6 = delay (lognormal etc.)
if [ "$6" = "lognormal" ]; then
	delay="log"
else
	delay="$6"
fi
timestamp="$(date +%Y%m%d%H%M%S)"
#filesuffix="${2}_${3}_${delay}_${4}_${5}_${7}_$timestamp"
filesuffix="${2}_${3}_${delay}_${4}_${5}_${7}"
filename="YCSB_${filesuffix}"

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
adb -s $1 shell sh /data/start_benchmark.sh $4 $5 $wakeport &
#adb -s $1 shell sh /data/benchmark.sh $4 $5 $wakeport

sleep 10 # Give phone script a chance to get running before starting Monsoon meter and cutting phone power:
echo "START" | nc -UN relay.sock
result=$?
if [ "$result" != "0" ]; then
	echo "Error on meter start"
	exit 1
else
	echo "OK on meter start"
fi

# Block on wakeup wifi ping from phone:
./server.exe $wakeport
result=$?
if [ "$result" != "0" ]; then
	echo "Error on wifi block"
	exit 1
else
	echo "OK on wifi block"
fi

sleep 10
#echo "STOP" | nc -UN relay.sock
#result=$?
#if [ "$result" != "0" ]; then
result=$(echo "SAVEmonsoon_${filesuffix}" | nc -U relay.sock)
if [ "$result" != "OK" ]; then
	echo "Error on meter stop:  $result"
	exit 1
else
	echo "OK on meter stop"
fi

# Block until phone is manually reconnected after measurement:
echo "Waiting for phone reconnect..."
adb wait-for-device

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

adb pull /data/phonelog.txt
cat phonelog.txt

echo "Run ${2} ${3} ${6} ${4} ${5} -- ${result}" >> progressfile.txt

# Sanity check:  Verify benchmark was run on-battery:
adb pull /data/power.txt
result="$(cat power.txt | grep "USB")"
echo "BATTERY:  $result2"
if [ "$result" != "  USB powered: false" ]; then
	echo "Error on battery power"
	exit 1 
else
	echo "OK on battery power"
fi


# pull log
adb -s $1 pull /data/trace.log
mv trace.log logs/$filename
gzip logs/$filename

printf "FILENAME:  %s\n" "$filename"
printf "Completed benchmark for device %s\n" $1

# Sanity check:  Verify main phone script matches:
#adb pull /data/start.txt
#result="$(cat start.txt)"
#echo "Script pid:  $result"
## TODO Fix this:  actually check pids


#TODO:
# (10) adb:  when USB connection is cut, the foreground proc dies, even if run with sighup -- ?! (which signal?  kill?)
# (11) adb:  proc on desktop blocks until all phone procs exit, even if already reparented to init -- ?!
# (12) Fix ERR result from results.txt
# (13) Remove inefficient DB populate code in java app
# (14) Clean-up socket apps (e.g. printing "Exit Clean" to console => nohup)
# (15) Consistincy-ize the -s $1 phone serial number stuff
# (16) Battery stats => ftrace logfile
# (19) Add check for pid==pid


