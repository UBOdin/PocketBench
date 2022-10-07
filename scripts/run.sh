#!/bin/bash
# run benchmark

wakeport="2017"  # Phone-client wifi wakeup port
# $2 = DB (sql); $3 = workload (A, B, C etc.); $4 = governor (schedutil etc.); $5 = speed; $6 = delay (lognormal etc.); $7 = threadcount (1); $8 = runcount
if [ "$6" = "lognormal" ]; then
	delay="log"
else
	delay="$6"
fi
cpuspeed="$(echo $5 | cut -d ":" -f2)"
filespeed="$(echo $5 | cut -d ":" -f1)"
timestamp="$(date +%Y%m%d%H%M%S)"
#filesuffix="${2}_${3}_${delay}_${4}_${filespeed}_${7}_$timestamp"
filesuffix="${2}_${3}_${delay}_${4}_${filespeed}_${7}_${8}"
meter="0"  # boolean -- whether using Monsoon meter
userapp="0"  # boolean -- whether running an AOSP app (1) or a native microbenchmark (0)

if [ "$userapp" = "1" ]; then
	filename="YCSB_${filesuffix}"

	printf "Rebooting and running benchmark\n"

	adb reboot
	adb wait-for-device
	sleep 10
	printf "Rebooted\n"
	adb root
	adb wait-for-device
	sleep 10
	printf "Rooted\n"

	adb shell sh /data/preBenchmark.sh $2 $3 $4 $cpuspeed $6 $7 #create database

	sleep 15 # Let phone settle before starting script:
else
	filename="micro_${filesuffix}"
fi

echo "Starting phone script"
adb shell sh /data/start_benchmark.sh $4 $cpuspeed $6 $wakeport &
#adb shell sh /data/benchmark.sh $4 $cpuspeed $wakeport

if [ "$meter" = "1" ]; then
	sleep 10 # Give phone script a chance to get running before starting Monsoon meter and cutting phone power:
	echo "START" | nc -UN relay.sock
	result=$?
	if [ "$result" != "0" ]; then
		echo "Error on meter start"
		exit 1
	else
		echo "OK on meter start"
	fi
else
	echo "(No meter start)"
fi

# Block on wakeup wifi ping from phone:
echo "Starting blocking -- Start app"
./server.exe $wakeport
result=$?
if [ "$result" != "0" ]; then
	echo "Error on wifi block"
	exit 1
else
	echo "OK on wifi block"
fi

if [ "$meter" = "1" ]; then
	sleep 10
	#echo "STOP" | nc -UN relay.sock
	result=$(echo "SAVEmonsoon_${filesuffix}" | nc -U relay.sock)
	# Split up return string from meter into errflag and timestamp:
	echo "RESULT"
	echo $result
	error_flag=$(echo $result | cut -c1-2)
	meter_time=$(echo $result | cut -c3-)
	if [ "$error_flag" != "OK" ]; then
		echo "Error on meter stop:  $result"
		exit 1
	else
		echo "OK on meter stop"
	fi
else
	echo "(No meter stop)"
	meter_time="dummy"
fi

# Block until phone is manually reconnected after measurement:
echo "Waiting for phone reconnect..."
adb wait-for-device

# Trap for initial errors on phone script (may be no resultfile yet):
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

# Wakeup phone script to commence cleanup (and simultaneously inject synchronization timestamp):
adb shell "echo ${meter_time} > /data/finish.pipe"

# Trap for more errors on phone script:
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

if [ "$meter" = "1" ]; then
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
else
	echo "(skipping battery sanity)"
fi

# Wakeup phone script again (to let it know it can drop its wakelock and exit):
adb shell "echo ${meter_time} > /data/finish.pipe"

# pull script log and tracing log:
adb pull /data/graphlog.txt
cat graphlog.txt
adb pull /data/phonelog.txt
cat phonelog.txt
adb pull /data/trace.log
mv trace.log logs/$filename
gzip logs/$filename

printf "FILENAME:  %s\n" "$filename"
printf "Completed benchmark\n"

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
# (16) Battery stats => ftrace logfile
# (19) Add check for pid==pid


