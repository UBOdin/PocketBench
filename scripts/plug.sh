#!/bin/bash

path=/home/carlnues/old_hd/home/carlnues/platform/pocketdata/PocketBench/scripts

# Only ping wakeup pipe if script is blocking on USB plug event.
# Otherwise, *we* will block and mess up future USB plug events.

# N.b. The udev USB add trigger produces **2** events in quick succession:
# 1 for the newly created USB (2.0) device, and 1 for a USB 1.0 device

if [ -f $path/plugflag.txt ]; then
	echo "phone plugged in" > $path/plug.pipe
	# Remove flag -- only want to ping once; else we will block on 2nd udev USB event (see above)
	rm $path/plugflag.txt
	echo "WAKEUP" >> $path/log.txt
else
	echo "NULL" >> $path/log.txt
fi

# Add the following udev trigger line to a file:  e.g. /etc/udev/rules.d/100-foobar.rules:
# SUBSYSTEMS=="usb", ATTRS{idVendor}=="18d1", ATTRS{idProduct}=="4ee7", ACTION=="add", RUN{program}="/home/carlnues/old_hd/home/carlnues/platform/pocketdata/PocketBench/scripts/plug.sh"

