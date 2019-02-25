
echo foo > /sys/power/wake_lock
sleep 30

trace_dir=/sys/kernel/debug/tracing

sync
echo 3 > /proc/sys/vm/drop_caches

governor=$1
default="interactive"
cpus="0 1 2 3" # List of cpus on phone
#frequencies="300000 422400 652800 729600 883200 960000 1036800 1190400 1267200 1497600 1574400 1728000 1958400 2265600 2457600 2496000 2572800 2649600"

#governor="ondemand" #"userspace"
frequency=$2 #"300000"


#frequency="2649600" #"2457600" #"1728000" #"1267200" #"1036800" #"729600"


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
	echo "ERR Invalid governor" > /data/results.txt
	exit 1
fi

# Stop mpdecision to permit setting the desired governor on all 4 cores:
stop mpdecision
# Turn on all CPUs and set governor as selected:
for i in $cpus; do
	echo "1" > /sys/devices/system/cpu/cpu$i/online
	echo "$governor" > /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor

	if [ "$governor" = "userspace" ]; then
		echo "$frequency" > /sys/devices/system/cpu/cpu$i/cpufreq/scaling_setspeed 
	fi

done
# Restart mpdecision for all governors (turned-off cores retain governor specified)
start mpdecision

#echo 0 > $trace_dir/events/phonelab_syscall_tracing/enable
#echo 0 > $trace_dir/events/sched/plsc_exec/enable
#echo 0 > $trace_dir/events/sched/plsc_fork/enable

# SELinux is a pain:
setenforce 0

echo 150000 > $trace_dir/buffer_size_kb
#echo 300000 > $trace_dir/buffer_size_kb
#echo 1 > $trace_dir/events/sched/sched_switch/enable
#echo 1 > $trace_dir/events/block/block_rq_insert/enable
#echo 1 > $trace_dir/events/block/block_rq_complete/enable
##echo 1 > $trace_dir/events/cpufreq_interactive/enable
#echo 1 > $trace_dir/events/power/cpu_frequency/enable
#echo 1 > $trace_dir/events/power/cpu_frequency_switch_start/enable
#echo 1 > $trace_dir/events/power/cpu_frequency_switch_end/enable

echo > $trace_dir/trace
#echo 1 > $trace_dir/tracing_enabled
echo 1 > $trace_dir/tracing_on

# Set up IPC pipe to retrieve end-of-run info from app:
rm /data/results.pipe
mknod /data/results.pipe p
chmod 777 /data/results.pipe
#/data/makepipe /data/results.pipe # mknod is MIA; chmod is weird and tries to read the pipe

#am kill-all
am start -n com.example.benchmark_withjson/com.example.benchmark_withjson.MainActivity

# Block until app completes run and outputs exit info:
echo "Starting blocking on pipe"
cat /data/results.pipe > /data/results.txt
echo "Ending blocking on pipe"

echo "Governor used:  $governor" >> /data/results.txt

echo 0 > $trace_dir/tracing_on
cat $trace_dir/trace > /data/trace.log
echo 1500 > $trace_dir/buffer_size_kb
echo 0 > $trace_dir/events/sched/sched_switch/enable
echo 0 > $trace_dir/events/block/block_rq_insert/enable
echo 0 > $trace_dir/events/block/block_rq_complete/enable
#echo 0 > $trace_dir/events/cpufreq_interactive/enable
echo 0 > $trace_dir/events/power/cpu_frequency/enable
echo 0 > $trace_dir/events/power/cpu_frequency_switch_start/enable
echo 0 > $trace_dir/events/power/cpu_frequency_switch_end/enable

# Reset governor to default (ondemand) (need to reactivate all cores first):
stop mpdecision
# Turn on all CPUs and reset governor to back to default:
for i in $cpus; do
	echo "1" > /sys/devices/system/cpu/cpu$i/online
	echo $default > /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor
done
start mpdecision

echo foo > /sys/power/wake_unlock

