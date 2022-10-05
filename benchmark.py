#!/usr/bin/python

import subprocess
import sys

#android_id = "02c566fa093765eb" # Grant's main test phone
#android_id = "ZX1G22TKW7" # Ed's old phone
#android_id = "199020104301402615" # Dragonboard 8074
#android_id = "ZX1G22LXTH" # Nexus 6 wired for Monsoon
#android_id = "FA7A21A02869" # Pixel 2 wired for Monsoon
#android_id = "FA7AK1A06424" # Pixel 2 (unmodded)
android_id = "(dummy)"  # placeholder -- scripts expect as first parameter

def help_message():
	print '\nCommand List:\n'
	print '	[quit/q/exit] exits the program'
	print

def setup_app(name):
	subprocess.call(['sh','scripts/setup/' + name + '.sh'])

def command(string_array):

	databases = ["SQL", "WAL", "NULL"]
	#workloads = ["A", "B", "C", "D", "E", "F"]
	workloads = ["A", "B", "C", "D", "E", "F", "N"]
	governors = ["userspace", "powersave", "performance", "schedutil"]
	#governors = ["userspace", "powersave", "performance", "interactive", "ondemand"]
	# 300000 364800 441600 518400 595200 672000 748800 825600 883200 960000 1036800 1094400 1171200 1248000 1324800 1401600 1478400 1555200 1670400 1747200 1824000 1900800
	# 300000 345600 422400 499200 576000 652800 729600 806400 902400 979200 1056000 1132800 1190400 1267200 1344000 1420800 1497600 1574400 1651200 1728000 1804800 1881600 1958400 2035200 2112000 2208000 2265600 2323200 2342400 2361600 2457600
	speeds = []  # Skip this sanity for now
	delays = ["0ms", "1ms", "lognormal", "null"]

	database = ""
	workload = ""
	governor = ""
	speed = "" # Only valid if governor == "userspace"
	delay = ""
	threads = ""
	runno = ""
	littlespeed = 0
	bigspeed = 0

	result = 0

	database = string_array[0].upper()
	workload = string_array[1].upper()
	governor = string_array[2]
	speed = string_array[3]
	delay = string_array[4]
	threads = "1"  # string_array[5]
	if (len(string_array) > 6):
		runno = string_array[6]
	else:
		runno = "0"
	#end_if

	print("PARAMETERS:")
	print(string_array)

	# Parameter validity check:
	if ((database not in databases) or (workload not in workloads) or (governor not in governors)):  # or (delay not in delays)):
		print("Invalid benchmark request")
		return 1
	#end_if

	if (governor != "userspace"):
		speed = "none:0-0" # Don't use slashes (messes with subdirectories) or parentheses (messes with scripting) or semicolons (ditto)
	else:
		#'''
		little_speed = int(speed) * 19008  # % of lomax (1900800)
		big_speed = int(speed) * 24576  # % of himax (2457600)
		speed = speed + ":" + str(little_speed) + "-" + str(big_speed)
		#'''
		#speed = speed + ":" + str(int(speed) * 26496)
	#end_if
	print("Speed:  " + speed)

	print("Running " + database + " " + workload)
	check = device_connected()
	if (check == False):
		print("No Device Connected!")
		return 0
	#end_if

	print("Run number:  " + runno)

	print("setting up phone...")
	subprocess.call(['sh', 'scripts/phone_setup.sh', android_id])
	print("success")

	print("building and installing app...")
	##result = subprocess.call(['sh', 'scripts/build.sh'])
	if (result != 0):
		print("Error on build");
		sys.exit(1)
	#end_if
	print("success")

	print("running...")
	result = subprocess.call(['sh', 'scripts/run.sh', android_id, database, workload, governor, speed, delay, threads, runno])
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
				#workload_list = ["sql a", "sql b", "sql c", "sql d", "sql e", "sql f"]
				#workload_list = ["sql a", "sql b", "sql c", "sql e"]
				#workload_list = ["sql a", "sql f"]
				workload_list = ["sql a"]

				#governor_list = ["schedutil x", "userspace 70", "performance x"]
				governor_list = ["schedutil x", "userspace 30", "userspace 40", "userspace 50", "userspace 60", "userspace 70", "userspace 80", "userspace 90", "performance x"]
				#governor_list = ["interactive x", "userspace 30", "userspace 40", "userspace 50", "userspace 60", "userspace 70", "userspace 80", "userspace 90", "performance x"]



				#delay_list = ["0ms", "lognormal"]
				#delay_list = ["0ms"]
				delay_list = ["normal", "50", "20", "5", "2", "0"]

				threads_list = ["1"]

				run_count = 3

				skip_count = 0

				iteration = 0

				for delay in delay_list:
					for governor in governor_list:
						for workload in workload_list:
							for threads in threads_list:
								for runno in range(run_count):
									parameters = workload + " " + governor + " " + delay + " " + threads + " " + str(runno)
									if (iteration < skip_count):
										print("Skipping workload %d:  %s" % (iteration, parameters))
									else:
										result = command(parameters.split())
									#end_if
									iteration += 1
								#end_for
							#end_for
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


