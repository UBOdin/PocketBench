
import json
import sys
import gzip
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches


def process_loglines(file_name, trace_list_list):

	# file_name = ""
	# trace_list_list = []

	logline = ""
	iteration = 0
	cpu = 0
	pid = 0
	time = 0.0
	index = 0
	func = ""
	freq = 0
	freq_list = [0, 0, 0, 0, 0, 0, 0, 0]
	startflag = False
	bench_cpu = 0
	bench_pid = 0
	param = ""
	param_list = []
	fixed_list = []
	trace_list = []

	input_file = gzip.open(file_name, "r")

	while (True):

		# Keep reading until finished:
		logline = input_file.readline()

		if (logline == ""):
			print("Never hit endmark")
			sys.exit(1)
			break
		#end_if

		iteration += 1
		if (iteration % 1000 == 0):
			#print("Iteration:  ", iteration)
			pass
		#end_if

		'''
		if (iteration == 80):
			break
		#end_if
		'''

		if (len(logline) < 50):
			continue
		#end_if
		if (logline[46] != ":"):
			continue
		#end_if

		pid = int(logline[17:23])
		cpu = int(logline[24:27])
		time = float(logline[33:46])

		index = logline.find(":", 48, -1)
		if (index == -1):
			print("Invalid ftrace function")
			sys.exit(1)
		#end_if
		func = logline[48:index]

		#print("%d  %d  %f  %s" % (pid, cpu, time, func))

		if (func == "tracing_mark_write"):
			if (startflag == False):
				if ("SQL_START" in logline):
					startflag = True
					bench_cpu = cpu
					bench_pid = pid
					trace_list = [iteration, time, "start", cpu, freq]
					trace_list_list.append(trace_list)
					#starttime += float(logline[33:46])
				#end_if
			else:
				if ("SQL_END" in logline):
					trace_list = [iteration, time, "end", cpu, freq]
					trace_list_list.append(trace_list)
					break
					#endtime += float(logline[33:46])
				#end_if
			#end_if
		#end_if

		if (startflag == False):
			continue
		#end_if

		if (func == "cpu_frequency"):
			index = logline.find(" ", 63, -1)
			if (index == -1):
				print("Invalid speed delimiter")
				sys.exit(1)
			#end_if
			if (logline[63:69] != "state="):
				print("Invalid speed parameter")
				sys.exit(1)
			#end_if
			freq = int(logline[69:index])
			freq_list[cpu] = freq
			#print("SPEED:  " + str(freq))
			if (cpu == bench_cpu):
				trace_list = [iteration, time, "speed", cpu, freq]
				trace_list_list.append(trace_list)
			#end_if
		#end_if

		if (func == "sched_migrate_task"):
			param_list = logline[68:].split(" ")

			# Kludge to sanitize for task names containing spaces:
			fixed_list = []
			for param in param_list:
				if ("=" in param):
					fixed_list.append(param)
				#end_if
			#end_for
			param_list = fixed_list

			if (param_list[1][0:4] != "pid="):
				print("Invalid migrate parameter")
				sys.exit(1)
			#end_if

			if (int(param_list[1][4:]) == bench_pid):

				if (param_list[3][0:9] != "orig_cpu="):
					print("Invalid origin parameter")
					sys.exit(1)
				#end_if
				if (int(param_list[3][9:]) != bench_cpu):
					print("Invalid origin cpu")
					sys.exit(1)
				#end_if
				if (param_list[4][0:9] != "dest_cpu="):
					print("Invalid destination parameter")
					sys.exit(1)
				#end_if

				'''
				print(iteration)
				print(time)
				print(bench_cpu)
				print(str(int(param_list[4][9:])))
				'''

				bench_cpu = int(param_list[4][9:])

				trace_list = [iteration, time, "migrate", bench_cpu, freq]
				trace_list_list.append(trace_list)
	
			#end_if


		#end_if

	#end_while

	#print("iterations:  %d" % (iteration))

	input_file.close()

	return

#end_def


def graph_freq_time(trace_list_list):

	# trace_list_list = []
	time_list = []
	speed_list = []
	time = 0.0
	speed = 0
	oldtime = 0.0
	oldspeed = 0
	basetime = 0.0
	maxtime = 0.0
	maxspeed = 0
	cycles = 0

	fig, ax = plt.subplots()

	for trace_list, i in zip(trace_list_list, range(len(trace_list_list))):
		time = trace_list[1]
		speed = trace_list[4]
		if (i == 0):
			basetime = time
		else:
			time_list.append(time - basetime)
			speed_list.append(oldspeed)
			time_list.append(time - basetime)
			speed_list.append(speed)
			cycles += oldspeed * (time - oldtime)
		#end_if
		if (speed > maxspeed):
			maxspeed = speed
		#end_if
		oldtime = time
		oldspeed = speed
	#end_for
	maxtime = trace_list_list[-1][1] - basetime

	print(maxtime)
	print(maxspeed)
	print(cycles)
	print(cycles / maxtime)

	#ax.scatter(time_list, speed_list, s = 5, color = "black")
	ax.plot(time_list, speed_list, color = "black")
	ax.axis([0, maxtime * 1.1, 0, maxspeed * 1.1])
	ax.set_title("Workload A, Unsaturated System", fontsize = 16, fontweight = "bold")
	ax.set_xlabel("Benchmark runtime (s)", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Benchmark CPU speed (kHz)", fontsize = 16, fontweight = "bold")

	plt.show()

	return



#end_def


def main():

	filename = ""
	trace_list_list = []

	print(sys.version_info)

	filename = sys.argv[1]

	print(filename)

	process_loglines(filename, trace_list_list)

	graph_freq_time(trace_list_list);

	print(len(trace_list_list))

	#'''
	for e in trace_list_list:
		print(e)
	#end_for
	#'''

#end_def


main()


