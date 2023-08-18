#!/usr/bin/python

import subprocess
import sys


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
	littlespeed = 0
	bigspeed = 0

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

	if (governor == "schedutil"):
		speed = "none:0-0-0-0" # Don't use slashes (messes with subdirectories) or parentheses (messes with scripting) or semicolons (ditto)
	else:
		'''
		speed_list = speed.split("-")
		lospeed = speed_list[0]
		hispeed = speed_list[1]
		if (lospeed == "def"):
			little_lospeed = 300000
			big_lospeed = 300000
		else:
			little_lospeed = int(lospeed) * 19008  # % of lomax (1900800)
			big_lospeed = int(lospeed) * 24576  # % of himax (2457600)
		#end_if
		if (hispeed == "def"):
			little_hispeed = 1900800
			big_hispeed = 2457600
		else:
			little_hispeed = int(hispeed) * 19008  # % of lomax (1900800)
			big_hispeed = int(hispeed) * 24576  # % of himax (2457600)
		#end_if
		speed = lospeed + "-" + hispeed + ":" + str(little_lospeed) + "-" + str(big_lospeed) + "-" + str(little_hispeed) + "-" + str(big_hispeed)
		'''

		#speed = "70-70:1401600-1728000-1401600-1728000"

		#'''
		# 1824000 little
		# 2342400 big
		# 1747200 1900800 little
		# 2323200 2361600 big
		if (speed == "oscillate"):
			speed = "oscillate:1747200-2323200-1900800-2361600"
		elif (speed == "mid"):
			speed = "mid:1824000-2342400-1824000-2342400"
		elif (speed == "low"):
			speed = "low:1747200-2323200-1747200-2323000"
		elif (speed == "high"):
			speed = "high:1900800-2361600-1900800-2361600"
		else:
			print("bad governor")
			#sys.exit(1)
		#end_if
		#'''
		'''
		#if ((delay == "2000-0-80-3") or (delay == "2000-0-08-3")):
		if (speed == "23"):
			#speed = "70:1324800-1728000-lh-bh"
			speed = "23:441600-576000-lh-bh"
		#end_if
		#if ((delay == "2000-0-e0-3") or (delay == "2000-0-0e-3")):
		if (speed == "70"):
			#speed = "23:441600-576000-lh-bh"
			speed = "70:1324800-1728000-lh-bh"
		#end_if
		'''
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

				#governor_list = ["schedutil x", "userspace 30", "userspace 40", "userspace 50", "userspace 60", "userspace 70", "userspace 80", "userspace 90", "performance x"]
				#governor_list = ["interactive x", "userspace 30", "userspace 40", "userspace 50", "userspace 60", "userspace 70", "userspace 80", "userspace 90", "performance x"]
				#governor_list = ["schedutil x", "userspace oscillate", "userspace mid", "userspace low", "userspace high"]
				#governor_list = ["schedutil x", "userspace 70-100", "userspace 70-70", "userspace 100-100", "performance x"]
				#governor_list = ["userspace 23", "userspace 70"]
				#governor_list = ["schedutil x", "userspace 70-70", "userspace 80-80", "ioblock def-def", "ioblock def-70", "ioblock def-80", "ioblock 40-def", "ioblock 40-80"]
				#governor_list = ["schedutil x", "userspace 70-70"]

				governor_list = ["schedutil x", "userspace 70-70"] #, "userspace low", "userspace mid", "userspace high", "oscillate oscillate"]

				#delay_list = ["normal", "50", "20", "5", "2", "0"]
				#delay_list = ["normal", "boost"]
				#delay_list = ["2000-0-00-0", "2000-0-f0-1", "2000-0-f0-2", "2000-0-f0-3", "2000-0-f0-4", "2000-0-0f-1", "2000-0-0f-2", "2000-0-0f-3", "2000-0-0f-4"]
				#delay_list = ["75-0-f0-1", "75-scale-f0-1"]
				delay_list = ["5000-5-f0-1"] ##### 5 ###, "1000-0-0f-1"]

				run_count = 5

				skip_count = 0

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


