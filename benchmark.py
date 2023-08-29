#!/usr/bin/python

import subprocess
import sys

little_dict = {"0":"300000", "30":"595200", "40":"825600", "50":"960000", "60":"1171200", "70":"1401600", "80":"1555200", "90":"1747200", "100":"1900800"}
big_dict = {"0":"300000", "30":"806400", "40":"1056000", "50":"1267200", "60":"1497600", "70":"1728000", "80":"2035200", "90":"2265600", "100":"2457600"}


def help_message():
	print '\nCommand List:\n'
	print '	[quit/q/exit] exits the program'
	print

def setup_app(name):
	subprocess.call(['sh','scripts/setup/' + name + '.sh'])

def command(string_array):

	governors = ["userspace", "powersave", "performance", "schedutil"]
	#governors = ["userspace", "powersave", "performance", "interactive", "ondemand"]
	# 300000 364800 441600 518400 595200 672000 748800 825600 883200 960000 1036800 1094400 1171200 1248000 1324800 1401600 1478400 1555200 1670400 1747200 1824000 1900800
	# 300000 345600 422400 499200 576000 652800 729600 806400 902400 979200 1056000 1132800 1190400 1267200 1344000 1420800 1497600 1574400 1651200 1728000 1804800 1881600 1958400 2035200 2112000 2208000 2265600 2323200 2342400 2361600 2457600

	speeds = []  # Skip this sanity for now

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
	# 1824000 little
	# 2342400 big
	# 1747200 1900800 little
	# 2323200 2361600 big
	if (speed == "oscillate"):
		assert(governor == "userspace")
		speed = "oscillate:1747200-2323200-1900800-2361600"
	elif (speed == "mid"):
		assert(governor == "userspace")
		speed = "mid:1824000-2342400-1824000-2342400"
	elif (speed == "low"):
		assert(governor == "userspace")
		speed = "low:1747200-2323200-1747200-2323000"
	elif (speed == "high"):
		assert(governor == "userspace")
		speed = "high:1900800-2361600-1900800-2361600"
	else:
		speed_list = speed.split("-")
		assert(len(speed_list) == 2)
		lospeed = speed_list[0]
		hispeed = speed_list[1]
		if (lospeed == "def"):
			little_lospeed = little_dict["0"]
			big_lospeed = big_dict["0"]
		elif (lospeed == "75"):
			little_lospeed = little_dict["70"]
			big_lospeed = big_dict["50"]
		else:
			little_lospeed = little_dict[lospeed]
			big_lospeed = big_dict[lospeed]
		#end_if
		if (hispeed == "def"):
			little_hispeed = little_dict["100"]
			big_hispeed = big_dict["100"]
		else:
			little_hispeed = little_dict[hispeed]
			big_hispeed = big_dict[hispeed]
		#end_if
		speed = lospeed + "-" + hispeed + ":" + str(little_lospeed) + "-" + str(big_lospeed) + "-" + str(little_hispeed) + "-" + str(big_hispeed)
	#end_if

	print("Speed:  " + speed)

	check = device_connected()
	if (check == False):
		print("No Device Connected!")
		return 0
	#end_if

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
	
def device_connected():
	temp_file = open("temp.txt",'w')
	subprocess.call(['adb', 'devices'], stdout=temp_file, stderr=temp_file)
	temp_file.close()
	tester = 1
	with open("temp.txt",'r') as log:
		for line in log:
			if 'device\n' in line:
				tester = 0
	subprocess.call(['rm', 'temp.txt'])
	if tester == 1:
		return False
	else:
		return True


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
				governor_list = ["schedutil def-def", "userspace 30-30", "userspace 40-40", "userspace 50-50", "userspace 60-60", "userspace 70-70", "userspace 80-80", "userspace 90-90", "performance def-def"]

				#governor_list = ["schedutil x", "userspace low", "userspace mid", "userspace high", "oscillate oscillate"]

				#governor_list = ["schedutil def-def", "schedutil 70-def", "schedutil 75-def", "userspace 70-70", "ioblock 70-def", "ioblock 75-def", "ioblock 70-70", "performance def-def"]
				#governor_list = ["schedutil def-def"]


				#delay_list = ["normal", "50", "20", "5", "2", "0"]
				#delay_list = ["normal", "boost"]
				#delay_list = ["2000-0-00-0", "2000-0-f0-1", "2000-0-f0-2", "2000-0-f0-3", "2000-0-f0-4", "2000-0-0f-1", "2000-0-0f-2", "2000-0-0f-3", "2000-0-0f-4"]
				delay_list = ["normal"]

				run_count = 10

				skip_count = 75
				iteration = 0

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

			if input[0].lower() == 'help' or input[0].lower() == 'menu':
				help_message()
				continue
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


