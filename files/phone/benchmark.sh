trace_dir=/sys/kernel/debug/tracing

sync
echo 3 > /proc/sys/vm/drop_caches

governor=$1
# Sanity check the governor choice ("performance" or "interactive")
if [ "$governor" != "performance" ] && [ "$governor" != "interactive" ]; then
	echo "Invalid governor" > /data/results.txt
	exit 1
fi
# Stop mpdecision to permit setting the desired governor on all 4 cores:
stop mpdecision
echo "1" > /sys/devices/system/cpu/cpu2/online
echo "1" > /sys/devices/system/cpu/cpu3/online
echo "1" > /sys/devices/system/cpu/cpu0/online
echo "1" > /sys/devices/system/cpu/cpu1/online
echo "$governor" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo "$governor" > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor
echo "$governor" > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor
echo "$governor" > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor
# Restart mpdecision if interactive (turned-off cores retain governor specified)
if [ "$governor" = "interactive" ]; then
	start mpdecision
fi

#echo 0 > $trace_dir/events/phonelab_syscall_tracing/enable
#echo 0 > $trace_dir/events/sched/plsc_exec/enable
#echo 0 > $trace_dir/events/sched/plsc_fork/enable

# SELinux is a pain:
setenforce 0

echo 150000 > $trace_dir/buffer_size_kb
#echo 300000 > $trace_dir/buffer_size_kb
echo 1 > $trace_dir/events/sched/sched_switch/enable
echo 1 > $trace_dir/events/block/block_rq_insert/enable
echo 1 > $trace_dir/events/block/block_rq_complete/enable
echo 1 > $trace_dir/events/cpufreq_interactive/enable

echo > $trace_dir/trace
#echo 1 > $trace_dir/tracing_enabled
echo 1 > $trace_dir/tracing_on

# Set up IPC pipe to retrieve end-of-run info from app:
rm /data/results.pipe
mknod /data/results.pipe p
chmod 777 /data/results.pipe

#am kill-all
am start -n com.example.benchmark_withjson/com.example.benchmark_withjson.MainActivity

# Block until app completes run and outputs exit info:
cat /data/results.pipe > /data/results.txt
echo "Governor used:  $governor" >> /data/results.txt

echo 0 > $trace_dir/tracing_on
cat $trace_dir/trace > /data/trace.log
echo 1500 > $trace_dir/buffer_size_kb
echo 0 > $trace_dir/events/sched/sched_switch/enable
echo 0 > $trace_dir/events/block/block_rq_insert/enable
echo 0 > $trace_dir/events/block/block_rq_complete/enable
echo 0 > $trace_dir/events/cpufreq_interactive/enable

# Scale back CPU if needed to prevent burnout
if [ "$governor" = "performance" ]; then
	echo "ondemand" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
	echo "ondemand" > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor
	echo "ondemand" > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor
	echo "ondemand" > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor
fi

