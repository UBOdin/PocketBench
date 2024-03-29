
toggle_events() {

	#echo $1 > $trace_dir/events/sched/sched_switch/enable
	#echo $1 > $trace_dir/events/sched/sched_migrate_task/enable
	echo $1 > $trace_dir/events/power/cpu_frequency/enable
	#echo $1 > $trace_dir/events/power/cpu_frequency_switch_start/enable
	#echo $1 > $trace_dir/events/power/cpu_frequency_switch_end/enable
	echo $1 > $trace_dir/events/power/cpu_idle/enable

}

set_governor() {

	local governor="$1"
	local frequency="$2"
	if [ "$device" = "nexus6" ]; then
		# Turn on all CPUs and set governor as selected:
		for i in $cpus; do
			echo "1" > $cpu_dir/cpu$i/online
			echo "$governor" > $cpu_dir/cpu$i/cpufreq/scaling_governor
			errtrap $? "ERR Invalid governor"
			if [ "$governor" = "userspace" ]; then
				echo "$frequency" > $cpu_dir/cpu$i/cpufreq/scaling_setspeed
			fi
		done
	else
		#for i in $cpu; do
		#	echo "1" > $cpu_dir/cpu$i/online
		#done
		cluster_list="0 4"
		for cluster in $cluster_list; do
			echo "$governor" > $cpu_dir/cpufreq/policy${cluster}/scaling_governor
			errtrap $? "ERR Invalid governor"
		done
		if [ "$governor" = "schedutil" ]; then
			# Extract the big-little min-max speeds from the uber-parameter:
			freq_lmin="$(echo $frequency | cut -d "-" -f1)"
			freq_bmin="$(echo $frequency | cut -d "-" -f2)"
			freq_lmax="$(echo $frequency | cut -d "-" -f3)"
			freq_bmax="$(echo $frequency | cut -d "-" -f4)"
			echo "$freq_lmin" > $cpu_dir/cpufreq/policy0/scaling_min_freq
			echo "$freq_bmin" > $cpu_dir/cpufreq/policy4/scaling_min_freq
			echo "$freq_lmax" > $cpu_dir/cpufreq/policy0/scaling_max_freq
			echo "$freq_bmax" > $cpu_dir/cpufreq/policy4/scaling_max_freq
		fi
		if [ "$governor" = "userspace" ]; then
			# Extract the specific big-little speeds from the uber-parameter:
			freq_little="$(echo $frequency | cut -d "-" -f1)"
			freq_big="$(echo $frequency | cut -d "-" -f2)"
			echo "$freq_little" > $cpu_dir/cpufreq/policy0/scaling_setspeed
			echo "$freq_big" > $cpu_dir/cpufreq/policy4/scaling_setspeed
		fi
		if [ "$governor" = "ioblock" ]; then
			# TODO:  Sort out freq parameter order issue with syscall
			freq_space="$(echo $frequency | tr - " ")"
			/data/setdef.exe $freq_space
			errtrap $? "ERR ioblock setdef"
		fi
	fi

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

	toggle_events 0
	set_governor "$default" "$deffreq"  # FIXME:  infinite loop if this fails
	echo "$1" >> $logfile
	echo "ERR" > $errfile
	send_wakeup
	echo foo > /sys/power/wake_unlock
	exit 1

}

errtrap() {

	if [ "$1" = "0" ]; then
		return
	fi
	error_exit "$2"

}

get_idledata() {

	idlecmd="cat $cpu_dir/cpu*/cpuidle/state*/time"
	idledata_list=$($idlecmd)
	for idledata in $idledata_list; do
		idleconcat="$idleconcat $idledata"
	done

}


get_cpufreq() {

	cpufreqconcat=""
	cluster_list="0 4"
	for cluster in $cluster_list; do
		result=$(cat /sys/devices/system/cpu/cpufreq/policy${cluster}/scaling_cur_freq)
		cpufreqconcat="$cpufreqconcat $result"
	done

}


echo foo > /sys/power/wake_lock

cpu_dir=/sys/devices/system/cpu
trace_dir=/sys/kernel/debug/tracing
trace_log=/sys/kernel/debug/tracing/trace_marker
errfile="/data/results.txt"
logfile="/data/phonelog.txt"
graphfile="/data/graphlog.txt"
idlefile="/data/idledata.txt"
#device="nexus6"
device="pixel2"
experiment="microbench"
#experiment="uiautomator"
#experiment="simpleapp"

governor=$1
frequency=$2
bgdelay=$3
wakeport=$4

rm $errfile
rm $logfile

echo "Starting phone script with parameters:  governor $governor, frequency $frequency, bgdelay $bgdelay, wakeport $wakeport" > $logfile

# SELinux is a pain:
setenforce 0

echo -1 > /proc/sys/kernel/perf_event_paranoid

# Signal foreground script that we are running (and, importantly, that nohup has already run):
printf "Getpid:\n$$\n" >> /data/start.pipe

input tap 100 100
sleep 20
input tap 100 100

sync
echo 3 > /proc/sys/vm/drop_caches

# TODO:  Sanity check for supported $device strings

if [ "$device" = "nexus6" ]; then
	default="interactive"
	cpus="0 1 2 3"
else
	default="schedutil"
	deffreq="300000-300000-1900800-2457600"
	cpus="0 1 2 3 4 5 6 7"
fi

# Sanity check that all CPUs are on (at least for Nexus 6, they should be -- not necessarily for Nexus 5):
for i in $cpus; do
	result="$(cat $cpu_dir/cpu$i/online)"
	if [ "$result" != "1" ]; then
		error_exit "ERR CPUs not all on"
	fi
done

# Set up IPC pipe to retrieve end-of-run info from app:
rm /data/results.pipe
mknod /data/results.pipe p
chmod 777 /data/results.pipe

# Set governor as selected (use userspace if oscillating):
if [ "$governor" = "oscillate" ]; then
	set_governor "userspace" "$frequency"
else
	set_governor "$governor" "$frequency"
fi
toggle_events 1

# Turn on tracing:
echo 150000 > $trace_dir/buffer_size_kb
echo 1 > $trace_dir/tracing_on
echo $(date +"Phone time 1:  %H:%M:%S.%N") >> $trace_log
echo "Microbenchmark params:  governor:  ${1} ${2}" >> $trace_log

if [ "$experiment" = "microbench" ]; then

	# Start background task to oscillate CPU frequencies:
	if [ "$governor" = "oscillate" ]; then
		oscspeeds=$(echo $frequency | tr "-" " ")
		echo "Oscillate speeds:  $oscspeeds" >> $trace_log
		sh /data/oscillate.sh $oscspeeds &
		bgpid="$!"
		sleep 1
	fi

	# N.b. SQL_START and SQL_END events are written inside microbenchmark

	#/data/compute.exe 200000000 1000 $bgdelay
	#taskset $cpumask /data/compute.exe 200000000 1000 $bgdelay  # Run microbench pinned to a core
	batchcount="$(echo $bgdelay | cut -d "-" -f1)"
	sleepinter="$(echo $bgdelay | cut -d "-" -f2)"
	cpumask="$(echo $bgdelay | cut -d "-" -f3)"
	proccount="$(echo $bgdelay | cut -d "-" -f4)"
	#loopcount="4000000"
	loopcount="100000000"
	#loopcount="5000000"
	#loopcount="30000000"

	#if [ "$proccount" != "0" ]; then
	#	loopcount=$(( loopcount / proccount ))
	#fi

	echo "loopcount:  $loopcount  batchcount:  $batchcount  sleepinter:  $sleepinter  cpumask:  $cpumask  proccount:  $proccount" >> $trace_log

	waittime="70"
	#waittime="0"
	sleep $waittime &
	waitpid="$!"

	get_cpufreq
	echo "CPU FREQ $cpufreqconcat" >> $trace_log

	get_idledata
	if [ "$proccount" != "0" ]; then
		/data/forker.exe $proccount /system/bin/taskset $cpumask /data/compute.exe $loopcount $batchcount $sleepinter
		result="$?"
	else
		result="0"
	fi
	get_idledata
	printf "IDLE DATA %s" "$idleconcat" >> $trace_log

	if [ "$governor" = "oscillate" ]; then
		kill -9 $bgpid
	fi

	errtrap $result "ERR on microbench 1"

	wait $waitpid
	echo "Finished fixed time $waittime" >> $trace_log

fi
if [ "$experiment" = "simpleapp" ]; then

	pkgname="com.spotify.music"
	alogcat_file="/data/logcat.txt"

	am force-stop $pkgname
	sleep 5

	logcat -c
	echo "before start" >> $trace_log
	# repurpose $bgdelay:
	if [ "$bgdelay" = "boost" ]; then
		set_governor "performance" "none"
	fi
	am start -a android.intent.action.MAIN -c andorid.intent.category.LAUNCHER -n $pkgname/.MainActivity
	sleep 2
	set_governor "$governor" "$frequency"
	echo "after start" >> $trace_log
	sleep 5
	logcat -d > $alogcat_file
	sleep 5

	am start -a android.intent.action.MAIN -c android.intent.category.HOME
	sleep 5
	input tap 100 100

	grep "ActivityTaskManager: Displayed" $alogcat_file >> $trace_log
	grep "ActivityTaskManager: Fully drawn" $alogcat_file >> $trace_log

fi
if [ "$experiment" = "uiautomator" ]; then

	# Start background task loads:
	bgthreads="1"
	if [ "$bgdelay" != "normal" ]; then
		/data/forker.exe $bgthreads /data/compute.exe 400000000 1000 $bgdelay &
		bgpid="$!"
	fi

	pkgname="com.facebook.katana"
	pkgtest="com.example.test.MetaTest"

	#pkgname= TDB
	#pkgtest="com.example.test.TempleTest"
	#pkgname="com.google.android.calculator"
	#pkgtest="com.example.test.CalcTest"

	#pkgname="com.google.android.youtube"
	#pkgtest="com.example.test.YoutubeTest"

	#pkgname="com.spotify.music"
	#pkgtest="com.example.test.SpotifyTest"

	get_cpufreq
	echo "CPU FREQ $cpufreqconcat" >> $trace_log

	dumpsys gfxinfo $pkgname reset > /dev/null
	get_idledata

	echo "SQL_START" >> $trace_log
	am instrument -w -e class $pkgtest com.example.test.test
	result="$?"
	echo "SQL_END" >> $trace_log

	get_idledata
	printf "IDLE DATA %s" "$idleconcat" >> $trace_log

	dumpsys gfxinfo $pkgname > $graphfile

	errtrap $result "ERR on uiautomator"
	echo "Microbenchmark result:  ${?}" >> $logfile
	am start -a android.intent.action.MAIN -c android.intent.category.HOME
	sleep 5
	input tap 100 100

	# Verify the background workers exited cleanly:
	if [ "$bgdelay" != "normal" ]; then
		wait $bgpid
		result="$?"
		echo "Background threads:  $bgthreads  Delay:  $bgdelay  Result:  $result" >> $trace_log
		errtrap $result "ERR on background threads"
	else
		echo "Background threads:  (normal; N/A)" >> $trace_log
	fi

	# Crunch gfxinfo data and inject into ftrace:
	# Gross kludge -- hardcoded index map:
	index_arr=(0 0 0 0 0 0 3 2 0 0 0 0 3 4 4 4 5 4)
	i=0
	output=""
	while read -r line; do
		line_arr=($line)
		#len=${#line_arr[*]}
		#if [ $i -ge 12 ] || [ $i -lt 18 ]; then
		#	word=${line_arr[((len - 1))]}
		#	echo $word
		#fi
		index=${index_arr[$i]}
		word=${line_arr[${index}]}
		if [ $index -ne 0 ]; then
			#echo "Word:  $word"
			output="$output $word"
		fi
		i=$((i + 1))
		if [ $i -ge 18 ]; then
			break
		fi
	done < $graphfile
	# Short sanitycheck:
	if [ ${line_arr[1]} != "Frame" ]; then
		error_exit "ERR on frame data 1"
	fi
	output_arr=($output)
	if [ "${#output_arr[*]}" != "8" ]; then
		error_exit "ERR on frame data 2"
	fi
	printf "GFX DATA:  %s" "$output" >> $trace_log
fi

echo "Received benchmark app finished signal" >> $logfile
echo $(date +"Phone time 2:  %H:%M:%S.%N") >> $trace_log
printf "Governor used:  %s\n" "$governor" >> $trace_log
cat $cpu_dir/cpufreq/policy0/scaling_min_freq >> $trace_log
cat $cpu_dir/cpufreq/policy4/scaling_min_freq >> $trace_log
cat $cpu_dir/cpufreq/policy0/scaling_max_freq >> $trace_log
cat $cpu_dir/cpufreq/policy4/scaling_max_freq >> $trace_log

toggle_events 0
set_governor "$default" "$deffreq"

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

