# setup phone

printf "Pushing files for device\n"
 
adb root
adb push files/phone/benchmark.sh /data/benchmark.sh
adb push files/phone/start_benchmark.sh /data/start_benchmark.sh

