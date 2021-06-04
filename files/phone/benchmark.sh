
toggle_events() {

	#echo $1 > $trace_dir/events/sched/sched_switch/enable
	echo $1 > $trace_dir/events/sched/sched_migrate_task/enable
	echo $1 > $trace_dir/events/power/cpu_frequency/enable
	#echo $1 > $trace_dir/events/power/cpu_frequency_switch_start/enable
	#echo $1 > $trace_dir/events/power/cpu_frequency_switch_end/enable

}

set_governor() {

	# Turn on all CPUs and set governor as selected:
	for i in $cpus; do

		echo "1" > $cpu_dir/cpu$i/online
		echo "$1" > $cpu_dir/cpu$i/cpufreq/scaling_governor
		# Speed is only valid for the userspace governor:
		if [ "$1" = "userspace" ]; then
			# Extract the specific big-little speeds from the uber-parameter:
			freq_little="$(echo $frequency | cut -d "-" -f1)"
			freq_big="$(echo $frequency | cut -d "-" -f2)"
			echo "$freq_little" > $cpu_dir/cpufreq/policy0/scaling_setspeed
			echo "$freq_big" > $cpu_dir/cpufreq/policy4/scaling_setspeed
		fi
		#cat $cpu_dir/cpu$i/cpufreq/scaling_setspeed >> $logfile

	done

}

send_wakeup() {

	##svc wifi enable
	sleep 10 # NEED TO FIX THIS -- do Blocking in lieu
	echo "Phone sending wifi wakeup to server" >> $logfile
	/data/phone.exe $wakeport
	result=$?
	echo "Wifi client socket result:  $result" >> $logfile
	##svc wifi disable

}

error_exit() {

	echo "$1" >> $logfile
	echo "ERR" > $errfile
	send_wakeup
	echo foo > /sys/power/wake_unlock
	exit 1

}


echo foo > /sys/power/wake_lock

cpu_dir=/sys/devices/system/cpu
trace_dir=/sys/kernel/debug/tracing
trace_log=/sys/kernel/debug/tracing/trace_marker
errfile="/data/results.txt"
logfile="/data/phonelog.txt"

rm $logfile
echo "Starting phone script with parameters:  $1, $2, $3" > $logfile

# SELinux is a pain:
setenforce 0

echo -1 > /proc/sys/kernel/perf_event_paranoid

# Signal foreground script that we are running (and, importantly, that nohup has already run):
printf "Getpid:\n$$\n" >> /data/start.pipe

sleep 30

sync
echo 3 > /proc/sys/vm/drop_caches

governor=$1
default="schedutil"
cpus="0 4" # List of cpu core groups (0-3 and 4-7 for Pixel 2)
#frequencies="300000 422400 652800 729600 883200 960000 1036800 1190400 1267200 1497600 1574400 1728000 1958400 2265600 2457600 2496000 2572800 2649600"

#governor="ondemand" #"userspace"
frequency=$2

wakeport=$3

# Sanity check that all CPUs are on (at least for Nexus 6, they should be -- not necessarily for Nexus 5):
for i in $cpus; do
	result="$(cat $cpu_dir/cpu$i/online)"
	if [ "$result" != "1" ]; then
		error_exit "ERR CPUs not all on"
	fi
done

# Sanity check the governor choice to supported values:
if [ "$governor" = "userspace" ]; then
	:
elif [ "$governor" = "powersave" ]; then
	:
elif [ "$governor" = "performance" ]; then
	:
elif [ "$governor" = "schedutil" ]; then
	:
elif [ "$governor" = "ioblock" ]; then
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
echo 1 > $trace_dir/tracing_on
echo $(date +"Phone time 1:  %H:%M:%S.%N") >> $trace_log

echo "LOGMARKER Battery before:" >> $trace_log
dumpsys battery >> $trace_log

# Set up IPC pipe to retrieve end-of-run info from app:
rm /data/results.pipe
mknod /data/results.pipe p
chmod 777 /data/results.pipe

#am kill-all
am start -n com.example.benchmark_withjson/com.example.benchmark_withjson.MainActivity

# Pin benchmark app to core:
##ps -A | grep "withjson" > /data/apppid.txt
##/data/pincore.exe < /data/apppid.txt
#if [ "$?" != "0" ]; then
#	set_governor "$default"
#	error_exit "ERR on corepin"
#fi

# Block until app completes run and outputs exit info:
echo "Start blocking on benchmark app signal" >> $logfile
result="$(cat /data/results.pipe)"
echo "$result" >> $logfile

toggle_events 0

echo $(date +"Phone time 2:  %H:%M:%S.%N") >> $trace_log

echo "LOGMARKER Battery after:" >> $trace_log
dumpsys battery >> $trace_log

# Trap for on-app error:
if [ "$result" == "ERR" ]; then
	set_governor "$default"
	error_exit "ERR on benchmark app"
fi
echo "Received benchmark app finished signal" >> $logfile

cat $cpu_dir/cpu0/cpufreq/scaling_setspeed >> $trace_log
cat $cpu_dir/cpu4/cpufreq/scaling_setspeed >> $trace_log

# Reset CPU governors:
set_governor "$default"

# Sanity check that we are still on battery:
dumpsys battery > /data/power.txt

send_wakeup
echo "OK" > $errfile
echo "Clean Exit" >> $logfile
#echo foo > /sys/power/wake_unlock

# Block until we receive cleanup ping from foreground script:
result="$(cat /data/finish.pipe)"
echo $result >> $trace_log  # Save timesync (received as wakeup ping)
echo $(date +"Phone time 3:  %H:%M:%S.%N") >> $trace_log
echo "Received wakeup ping from main script" >> $logfile
#echo foo > /sys/power/wake_unlock

# Pull results:
cat $trace_dir/trace > /data/trace.log
echo 1500 > $trace_dir/buffer_size_kb
echo 0 > $trace_dir/tracing_on

# Block again until we receive exit ping from foreground script:
result="$(cat /data/finish.pipe)"
echo foo > /sys/power/wake_unlock
exit 0

