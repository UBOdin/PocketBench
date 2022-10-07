
trace_dir=/sys/kernel/debug/tracing
echo > $trace_dir/trace
echo 1 > $trace_dir/tracing_on
echo "START FOREGROUND SCRIPT" >> $trace_dir/trace_marker
echo 0 > $trace_dir/tracing_on

# Problem:  We could exit in the foreground before the main script runs nohup
# in the background, in which case the main script will be killed by SIGHUP.
# So:  Set up an IPC pipe to synchronize with the main script:
rm /data/start.pipe
mknod /data/start.pipe p

# Create another pipe to synch end of main script with foreground script:
rm /data/finish.pipe
mknod /data/finish.pipe p

# Launch main benchmark script in the background:
nohup sh /data/benchmark.sh $1 $2 $3 $4 > /data/output.out &

# Save main script pid for later sanity check:
printf "Returned pid:\n$!\n" > /data/start.txt

# Block until we receive signal that background script is running (with nohup)
cat /data/start.pipe >> /data/start.txt

exit 0

