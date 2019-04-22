
toggle_events() {

	echo $1 > $trace_dir/events/sched/sched_switch/enable
	echo $1 > $trace_dir/events/block/block_rq_insert/enable
	echo $1 > $trace_dir/events/block/block_rq_complete/enable
	#echo $1 > $trace_dir/events/cpufreq_interactive/enable
	echo $1 > $trace_dir/events/power/cpu_frequency/enable
	echo $1 > $trace_dir/events/power/cpu_frequency_switch_start/enable
	echo $1 > $trace_dir/events/power/cpu_frequency_switch_end/enable

}

set_governor() {

	# Stop mpdecision to permit setting the desired governor on all 4 cores:
	stop mpdecision
	# Turn on all CPUs and set governor as selected:
	for i in $cpus; do

		echo "1" > /sys/devices/system/cpu/cpu$i/online
		echo "$1" > /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor
		# Speed is only valid for the userspace governor:
		if [ "$1" = "userspace" ]; then
			echo "$frequency" > /sys/devices/system/cpu/cpu$i/cpufreq/scaling_setspeed 
		fi

	done
	# Restart mpdecision for all governors (turned-off cores retain governor specified)
	start mpdecision

}

send_wakeup() {

	svc wifi enable
	sleep 60 # NEED TO FIX THIS -- do Blocking in lieu
	echo "Phone sending wifi wakeup to server" >> $logfile
	/data/phone.exe $wakeport
	result=$?
	echo "Wifi client socket result:  $result" >> $logfile
	svc wifi disable

}

error_exit() {

	echo "$1" >> $logfile
	echo "ERR" > $errfile
	send_wakeup
	echo foo > /sys/power/wake_unlock
	exit 1

}


echo foo > /sys/power/wake_lock

trace_dir=/sys/kernel/debug/tracing
trace_log=/sys/kernel/debug/tracing/trace_marker
errfile="/data/results.txt"
logfile="/data/phonelog.txt"

rm $logfile
echo "Starting phone script with parameters:  $1, $2, $3" > $logfile

# SELinux is a pain:
setenforce 0

# Signal foreground script that we are running (and, importantly, that nohup has already run):
printf "Getpid:\n$$\n" >> /data/start.pipe

sleep 30

sync
echo 3 > /proc/sys/vm/drop_caches

governor=$1
default="interactive"
cpus="0 1 2 3" # List of cpus on phone
#frequencies="300000 422400 652800 729600 883200 960000 1036800 1190400 1267200 1497600 1574400 1728000 1958400 2265600 2457600 2496000 2572800 2649600"

#governor="ondemand" #"userspace"
frequency=$2 #"300000"


#frequency="2649600" #"2457600" #"1728000" #"1267200" #"1036800" #"729600"

wakeport=$3

# Sanity check the governor choice to supported values:
if [ "$governor" = "performance" ]; then
	:
elif [ "$governor" = "interactive" ]; then
	:
elif [ "$governor" = "conservative" ]; then
	:
elif [ "$governor" = "ondemand" ]; then
	:
elif [ "$governor" = "userspace" ]; then
	:
elif [ "$governor" = "powersave" ]; then
	:
else
	error_exit "ERR Invalid governor"
fi

# Set governor as selected:
set_governor "$governor"

# Turn on tracing:
echo 150000 > $trace_dir/buffer_size_kb
toggle_events 1
echo > $trace_dir/trace
#echo 1 > $trace_dir/tracing_enabled
echo 1 > $trace_dir/tracing_on

echo "LOGMARKER Battery before:" >> $trace_log
dumpsys battery >> $trace_log

# Set up IPC pipe to retrieve end-of-run info from app:
rm /data/results.pipe
mknod /data/results.pipe p
chmod 777 /data/results.pipe

#am kill-all
am start -n com.example.benchmark_withjson/com.example.benchmark_withjson.MainActivity

# Block until app completes run and outputs exit info:
echo "Start blocking on benchmark app signal" >> $logfile
result="$(cat /data/results.pipe)"
echo "$result" >> $logfile

echo "LOGMARKER Battery after:" >> $trace_log
dumpsys battery >> $trace_log

# Turn off tracing:
echo 0 > $trace_dir/tracing_on
toggle_events 0

# Trap for on-app error:
if [ "$result" == "ERR" ]; then
	set_governor "$default"
	error_exit "ERR on benchmark app"
fi
echo "Received benchmark app finished signal" >> $logfile

# Pull results:
cat $trace_dir/trace > /data/trace.log
echo 1500 > $trace_dir/buffer_size_kb

# Reset CPU governors:
set_governor "$default"

# Sanity check that we are still on battery:
dumpsys battery | grep AC > /data/power.txt

send_wakeup
echo "OK" > $errfile
echo "Clean Exit" >> $logfile
echo foo > /sys/power/wake_unlock
exit 0

