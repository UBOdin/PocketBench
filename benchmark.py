#!/usr/bin/python

import subprocess
import sys

# 300000 574000 738000 930000 1098000 1197000 1328000 1401000 1598000 1704000 1803000
little_dict = {"0":"300000", "30":"574000", "40":"738000", "50":"930000", "60":"1098000", "70":"1328000", "80":"1598000", "90":"1704000", "100":"1803000"}
# 400000 553000 696000 799000 910000 1024000 1197000 1328000 1491000 1663000 1836000 1999000 2130000 2253000 2348000
mid_dict = {"0":"400000", "30":"799000", "40":"1024000", "50":"1197000", "60":"1491000", "70":"1663000", "80":"1999000", "90":"2130000", "100":"2348000"}
# 500000 851000 984000 1106000 1277000 1426000 1582000 1745000 1826000 2048000 2188000 2252000 2401000 2507000 2630000 2704000 2802000 2850000
big_list = {"0":"500000", "30":"984000", "40":"1277000", "50":"1426000", "60":"1745000", "70":"2048000", "80":"2401000", "90":"2630000", "100":"2850000"}


def command(string_array):

	governors = ["userspace", "powersave", "performance", "schedutil"]
	governor = ""
	speed = "" # Only valid if governor == "userspace"
	delay = ""
	runno = ""

	result = 0

	governor = string_array[0]
	speed = string_array[1]
	delay = string_array[2]
	if (len(string_array) > 3):
		runno = string_array[3]
	else:
		runno = "0"
	#end_if

	print("PARAMETERS:")
	print(string_array)

	#speed = "none:0-0-0-0" # Don't use slashes (messes with subdirectories) or parentheses (messes with scripting) or semicolons (ditto)
	if (speed == "userspace"):
		speed_list = speed.split("-")
		assert(len(speed_list) == 2)
		lospeed = speed_list[0]
		hispeed = speed_list[1]
		if (lospeed == "def"):
			little_lospeed = little_dict["0"]
			mid_lospeed = mid_dict["0"]
			big_lospeed = big_dict["0"]
		else:
			little_lospeed = little_dict[lospeed]
			mid_lospeed = mid_dict[lospeed]
			big_lospeed = big_dict[lospeed]
		#end_if
		if (hispeed == "def"):
			little_hispeed = little_dict["100"]
			mid_hispeed = mid_dict["100"]
			big_hispeed = big_dict["100"]
		else:
			little_hispeed = little_dict[hispeed]
			mid_hispeed = mid_dict[hispeed]
			big_hispeed = big_dict[hispeed]
		#end_if
		speed = lospeed + "-" + hispeed + ":" + str(little_lospeed) + "-" + str(mid_lospeed) + "-" + str(big_lospeed) + "-" + str(little_hispeed) + "" + str(mid_hispeed) + "-" + str(big_hispeed)
	#end_if

	print("Speed:  " + speed)
	print("Run number:  " + runno)

	print("setting up phone...")
	subprocess.call(['sh', 'scripts/phone_setup.sh'])
	print("success")

	print("running...")
	result = subprocess.call(['sh', 'scripts/run.sh', governor, speed, delay, runno])
	print("log is present in the logs directory.")
	if (result != 0):
		print("Error on script:  " + str(result))
		sys.exit(1)
	#end_if

	return result

#end_def


def main():

	while (True):
		input = raw_input('benchmark...$ ')
		try:
			input = input.split()
			if input[0].lower() == 'quit' or input[0].lower() == 'exit' or input[0].lower() == 'q':
				break

			if (input[0].lower() == "what"):

				#governor_list = ["userspace 23", "userspace 70"]
				#governor_list = ["schedutil x", "userspace 70-70", "userspace 80-80", "ioblock def-def", "ioblock def-70", "ioblock def-80", "ioblock 40-def", "ioblock 40-80"]
				#governor_list = ["schedutil def-def", "userspace 30-30", "userspace 40-40", "userspace 50-50", "userspace 60-60", "userspace 70-70", "userspace 80-80", "userspace 90-90", "performance def-def"]
				governor_list = ["schedutil def-def"]

				#governor_list = ["schedutil x", "userspace low", "userspace mid", "userspace high", "oscillate oscillate"]

				#governor_list = ["schedutil def-def", "schedutil 70-def", "schedutil 75-def", "userspace 70-70", "ioblock 70-def", "ioblock 75-def", "ioblock 70-70", "performance def-def"]
				#governor_list = ["schedutil def-def"]


				#delay_list = ["normal", "50", "20", "5", "2", "0"]
				#delay_list = ["normal", "boost"]
				#delay_list = ["2000-0-00-0", "2000-0-f0-1", "2000-0-f0-2", "2000-0-f0-3", "2000-0-f0-4", "2000-0-0f-1", "2000-0-0f-2", "2000-0-0f-3", "2000-0-0f-4"]
				#delay_list = ["2000-0-f0-1", "2000-0-f0-2", "2000-0-f0-3", "2000-0-f0-4", "2000-0-0f-1", "2000-0-0f-2", "2000-0-0f-3", "2000-0-0f-4"]
				#delay_list = ["2000-5-f0-1", "2000-5-f0-2", "2000-5-f0-3", "2000-5-f0-4", "2000-5-0f-1", "2000-5-0f-2", "2000-5-0f-3", "2000-5-0f-4"]
				delay_list = ["normal"]


				#delay_list = ["normal"]
				#delay_list = ["2000-0-f0-1"]

				run_count = 10
				iteration = 0
				skip_count = 3

				for runno in range(run_count):
					for delay in delay_list:
						for governor in governor_list:
							parameters = governor + " " + delay + " " + str(runno)
							if (iteration < skip_count):
									print("Skipping workload %d:  %s" % (iteration, parameters))
							else:
								result = command(parameters.split())
							#end_if
							iteration += 1
							#end_for
						#end_for
					#end_for
				#end_if

		except IndexError:
			pass
		#end_try
		code = 1
		try:
			code = command(input)
		except IndexError:
			pass
		#end_try
		if code == 0:
			continue
		#end_if
		if code < 0:
			print 'Program exited with error code: ' + str(code)
			break
		#end_if
		print 'invalid command'

	#end_while
#end_def


main()


