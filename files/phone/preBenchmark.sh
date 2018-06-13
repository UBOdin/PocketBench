
# Disable SELinux:
setenforce 0

# Set up input parameter file to configure app benchmark:
config_file="/data/config.txt"
rm $config_file
echo $1 > $config_file
echo $2 >> $config_file
chmod 777 $config_file

am start -n com.example.benchmark_withjson/com.example.benchmark_withjson.MainActivity
sleep 70
