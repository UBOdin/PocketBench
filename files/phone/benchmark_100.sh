trace_dir=/sys/kernel/debug/tracing

sync
echo 3 > /proc/sys/vm/drop_caches

# **** ALSO:  comment in/out "ondemand" at bottom ****
stop mpdecision
echo "1" > /sys/devices/system/cpu/cpu2/online
echo "1" > /sys/devices/system/cpu/cpu3/online
echo "1" > /sys/devices/system/cpu/cpu0/online
echo "1" > /sys/devices/system/cpu/cpu1/online
echo "performance" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo "performance" > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor
echo "performance" > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor
echo "performance" > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor
#echo "userspace" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
#echo "2265600" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed
#echo "2265600" > /sys/devices/system/cpu/cpu1/cpufreq/scaling_setspeed
#echo "2265600" > /sys/devices/system/cpu/cpu2/cpufreq/scaling_setspeed 
#echo "2265600" > /sys/devices/system/cpu/cpu3/cpufreq/scaling_setspeed 

#echo 0 > $trace_dir/events/phonelab_syscall_tracing/enable
#echo 0 > $trace_dir/events/sched/plsc_exec/enable
#echo 0 > $trace_dir/events/sched/plsc_fork/enable
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


#am kill-all
am start -n com.example.benchmark_withjson/com.example.benchmark_withjson.MainActivity
#sleep 4000
sleep 100
#sleep 50
#sleep 10

echo 0 > $trace_dir/tracing_on
cat $trace_dir/trace > /data/trace.log
echo 1500 > $trace_dir/buffer_size_kb
echo 0 > $trace_dir/events/sched/sched_switch/enable
echo 0 > $trace_dir/events/block/block_rq_insert/enable
echo 0 > $trace_dir/events/block/block_rq_complete/enable
echo 0 > $trace_dir/events/cpufreq_interactive/enable

echo "ondemand" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo "ondemand" > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor
echo "ondemand" > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor
echo "ondemand" > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor

