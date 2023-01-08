
cpu_dir=/sys/devices/system/cpu

freq_little_lo=$1
freq_big_lo=$2
freq_little_hi=$3
freq_big_hi=$4

interval=".02"

trace_log=/sys/kernel/debug/tracing/trace_marker
echo "little lo:  $freq_little_lo  big lo:  $freq_big_lo  little hi:  $freq_little_hi  big hi:  $freq_big_hi" >> $trace_log

while [ "1" = "1" ]; do

	sleep $interval

	echo "$freq_little_hi" > $cpu_dir/cpufreq/policy0/scaling_setspeed
	echo "$freq_big_hi" > $cpu_dir/cpufreq/policy4/scaling_setspeed
	
	sleep $interval

	echo "$freq_little_lo" > $cpu_dir/cpufreq/policy0/scaling_setspeed
	echo "$freq_big_lo" > $cpu_dir/cpufreq/policy4/scaling_setspeed

done
			
