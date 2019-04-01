
# Remove DB files on phone:
rm /data/data/com.example.benchmark_withjson/databases/SQLBenchmark
rm /data/data/com.example.benchmark_withjson/databases/SQLBenchmark-journal
rm /data/data/com.example.benchmark_withjson/databases/BDBBenchmark
rm /data/data/com.example.benchmark_withjson/databases/BDBBenchmark-journal/*

if [ -e /data/DB_CONFIG ]; then
	mv /data/DB_CONFIG /data/data/com.example.benchmark_withjson/databases/BDBBenchmark-journal/
fi

# Paranoia...
rm /data/DB_CONFIG

# Disable SELinux:
setenforce 0

# Set up input parameter file to configure app benchmark (1 parameter per line):
config_file="/data/config.txt"
rm $config_file
printf "%s\n%s\n%s\n%s\n%s\n%s\n" $1 $2 $3 $4 $5 $6 > $config_file
chmod 777 $config_file

am start -n com.example.benchmark_withjson/com.example.benchmark_withjson.MainActivity
sleep 70
pm disable com.example.benchmark_withjson
sleep 5
pm enable com.example.benchmark_withjson

