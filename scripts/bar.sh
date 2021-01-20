
echo "Start Meta Script:  $1 $2"

echo "Script pid:  $$"

#exit 22

#adb shell 'nohup > data/output.out sh /data/benchmark.sh $4 $5 $2 $3 $6 $7 & echo $!' &

#adb shell "nohup > data/output.out sh /data/foo.sh $1 $2 & echo \$!" &
#adb shell "sleep .006; nohup > data/output.out sh /data/foo.sh $1 $2 & echo \$!" &
#adb shell "nohup > data/output.out sh /data/foo.sh $1 $2" &

#adb shell "nohup > data/output.out /data/foo.exe $1 $2 & echo \$!" &
adb shell "/data/foo.exe $1 $2 & echo \$! ; sleep .1" &


sleep 5

echo "End sleep"

adb shell cat /data/pid.txt

echo "End Meta Script"

