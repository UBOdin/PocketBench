
import json
import sys
import gzip
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

from matplotlib.lines import Line2D

import math
import statistics


def mean_margin(data_list):

	n = 0
	mean = 0.0
	stdev = 0.0
	zstar = 1.645 # for 90% -- 1.96 # for 95%
	margin = 0.0

	n = len(data_list)
	mean = statistics.mean(data_list)
	stdev = statistics.stdev(data_list) # stdev() or pstdev()
	margin = zstar * (stdev / math.sqrt(n))

	return mean, margin

#end_def


def process_loglines(file_name):  #, trace_list_list):

	# file_name = ""
	trace_list_list = []

	logline = ""
	iteration = 0
	cpu = 0
	pid = 0
	time = 0.0
	index = 0
	timeend = 0
	eventend = 0
	eventtype = ""
	datastart = 0
	freq = 0
	freq_list = [0, 0, 0, 0, 0, 0, 0, 0]
	starttime = 0.0
	endtime = 0.0
	startflag = False
	bench_cpu = 0
	bench_pid = 0
	param = ""
	param_list = []
	fixed_list = []
	trace_list = []
	target_cpu = 0
	sleepstate = 0
	idletime = 0
	idlecount = 0
	perfcycles = 0
	cacherefs = 0
	cachemisses = 0

	offcount = 0
	oncount = 0

	input_file = gzip.open(file_name, "r")

	while (True):

		# Keep reading until finished:
		logline = input_file.readline().decode("ascii")

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
		if (logline[48] != ":"):
			continue
		#end_if

		# Calculate length of timefield (n.b. can vary):
		index = logline.find(":", 34)
		if (index == -1):
			print("Missing timeend")
			sys.exit(1)
		#end_if
		timeend = index

		pid = int(logline[17:23])
		cpu = int(logline[24:27])
		time = float(logline[34:timeend])

		# Find end of ftrace event type:
		index = logline.find(":", timeend + 2)
		if (index == -1):
			print("Invalid ftrace event")
			sys.exit(1)
		#end_if
		eventend = index
		eventtype = logline[timeend + 2:eventend]
		datastart = eventend + 2

		'''
		print("Time end:  " + str(timeend))
		print(eventtype)
		print("Func end:  " + str(eventend))
		print(datastart)
		'''

		if (eventtype == "tracing_mark_write"):
			if (startflag == False):
				if ("SQL_START" in logline):
					startflag = True
					bench_cpu = cpu
					bench_pid = pid
					trace_list = [iteration, time, "start", cpu, freq]
					trace_list_list.append(trace_list)
					starttime = time
				#end_if
			else:
				if ("SQL_END" in logline):
					trace_list = [iteration, time, "end", cpu, freq]
					trace_list_list.append(trace_list)
					endtime = time
					break
				#end_if

				if ("CACHE_REFS" in logline):
					cacherefs = int(logline[datastart + 13:])
				#end_if

				if ("CACHE_MISSES" in logline):
					cachemisses = int(logline[datastart + 15:])
				#end_if

			#end_if
		#end_if

		if (startflag == False):
			continue
		#end_if

		# N.b. for the cpu_frequency event, the cpu field is the CPU# on which the governor
		# runs.  It is *not* necessarily the *target* CPU# for which the speed is set.
		if (eventtype == "cpu_frequency"):

			print("BOMB -- fix this event to remove hardcoded logline timefield assumptions")
			sys.exit(1)

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

			#index = logline.find(" ", index, -1)
			if (logline[index + 1:index + 8] != "cpu_id="):
				print("Invalid run cpu parameter")
				sys.exit(1)
			#end_if
			target_cpu = int(logline[index + 8:-1])  # Fetch the *target* cpu#

			freq_list[target_cpu] = freq
			if (target_cpu == bench_cpu):
				trace_list = [iteration, time, "speed", target_cpu, freq]
				trace_list_list.append(trace_list)
			#end_if
		#end_if

		#'''
		if (eventtype == "cpu_idle"):
			index = logline.find(" ", datastart)
			if (index == -1):
				print("Invalid speed delimiter")
				sys.exit(1)
			#end_if
			if (logline[datastart:datastart + 6] != "state="):
				print("Invalid speed parameter")
				sys.exit(1)
			#end_if
			sleepstate = int(logline[datastart + 6:index])
			if (sleepstate == 4294967295):
				sleepstate = -1
				idletime += time
				idlecount += 1
				offcount += 1
			else:
				idletime -= time
				oncount += 1
			#end_if

			#index = logline.find(" ", index, -1)
			if (logline[index + 1:index + 8] != "cpu_id="):
				print("Invalid idle cpu parameter")
				sys.exit(1)
			#end_if
			target_cpu = int(logline[index + 8:-1])  # Fetch the *target* cpu#

			# Test hypo:
			if (cpu != target_cpu):
				print("cpu mismatch")
				sys.exit(1)
			#end_if

			#freq_list[target_cpu] = freq
			if (target_cpu == bench_cpu):
				trace_list = [iteration, time, "idle", target_cpu, sleepstate]
				trace_list_list.append(trace_list)
			#end_if
		#end_if
		#'''

		if (eventtype == "sched_migrate_task"):
			param_list = logline[datastart:].split(" ")

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

				trace_list = [iteration, time, "migrate", bench_cpu, cpu]
				trace_list_list.append(trace_list)
	
			#end_if


		#end_if

	#end_while

	#print("iterations:  %d" % (iteration))

	input_file.close()

	print("Idle time:  %f" % (idletime))
	print("Idle count:  %d" % (idlecount))
	print(starttime)
	print(endtime)
	print("Latency:  ", endtime - starttime)
	print(cacherefs)
	print(cachemisses)
	print(offcount)
	print(oncount)

	for e in trace_list_list:
		print(e)
	#end_for

	#return perfcycles
	return (endtime - starttime) * 1000.0, cacherefs, cachemisses

#end_def


def get_runtime(file_name):

	# file_name = ""

	logline = ""
	iteration = 0
	starttime = 0.0
	endtime = 0.0
	cycles = 0.0
	cacherefs = 0
	cachemisses = 0

	input_file = gzip.open(file_name, "r")

	while (True):

		# Keep reading until finished:
		logline = input_file.readline().decode("ascii")

		if (logline == ""):
			break
		#end_if

		iteration += 1
		if (iteration % 1000 == 0):
			#break
			#print("Iteration:  ", iteration)
			pass
		#end_if

		if ("SQL_START" in logline):
			starttime += float(logline[33:48])
		#end_if

		if ("SQL_END" in logline):
			endtime += float(logline[33:48])
		#end_if

		if ("CACHE_REFS" in logline):
			cacherefs = int(logline[83:])
		#end_if

		if ("CACHE_MISSES" in logline):
			cachemisses = int(logline[85:])
		#end_if

		'''
		if ("Cycle data" in logline):
			cycles = float(logline[79:])
		#end_if
		'''

	#end_while

	#print("iterations:  %d" % (iteration))

	#print(starttime)
	#print(endtime)
	#print("Latency:  ", endtime - starttime)
	print(cacherefs)
	print(cachemisses)

	input_file.close()

	return (endtime - starttime) * 1000.0, cacherefs, cachemisses

#end_def


def get_energy(file_name):

	# file_name = ""

	logline = ""
	logline_list = []
	iteration = 0
	time = 0.0
	amps = 0.0
	volts = 0.0

	amps_total = 0.0
	start = 0.0
	stop = 0.0

	# Get linecount (kludge):
	input_file = open(file_name, "r")
	while (True):
		logline = input_file.readline()
		if (logline == ""):
			break
		#end_if
		iteration += 1
	#end_while
	input_file.close()

	#start = 7.0  # fixed
	#stop = float(iteration - 2) / 5000.0 - 19.0  # Set stop to 19s before end
	start = 8.0
	stop = start + 150.0
	iteration = 0  # reset counter
	#print("File:  %s  Stop:  %f" % (file_name, stop))

	# Reopen file:
	input_file = open(file_name, "r")
	# Skip first line:
	logline = input_file.readline()

	while (True):

		# Keep reading until finished:
		logline = input_file.readline()

		if (logline == ""):
			break
		#end_if

		iteration += 1
		if (iteration % 1000 == 0):
			#break
			#print("Iteration:  ", iteration)
			pass
		#end_if

		logline_list = logline.split(",")
		# Sanity
		if (len(logline_list) != 3):
			print("Error:  Unexpected line length")
			sys.exit(1)
		#end_if

		time = float(logline_list[0])
		amps = float(logline_list[1])
		volts = float(logline_list[2])

		# Sanity
		if ((volts < 3.9) or (volts > 4.1)):
			print("Error:  Unexpected voltage")

			print(file_name)
			print(iteration)

			#sys.exit(1)
		#end_if

		if (time <= start):
			continue
		#end_if

		if (time > stop):
			break
		#end_if

		amps_total += amps

	#end_while


	'''
	print("iterations:  %d" % (iteration))

	factor = 1000.0 / (60.0 * 60.0 * 5000.0)  # Convert .0002s => 1 hour (/ 60 * 60 * 5000) and mA => uA (* 1000)

	print(factor)

	print("total current:  %f" % (amps_total / (3600.0 * 5.0)))
	print("total power:  %f" % (watts_total / (3600.0 * 5.0)))
	'''

	input_file.close()

	return amps_total / (3600.0 * 5.0)

#end_def


def bargraph_latency(latency_list, cacherefs_list, cachemisses_list, benchname):

	# latency_list = []
	# cacheref_list = []
	# cachemiss_list = []
	# benchname = ""
	latency = 0.0
	clusterlen = 0
	width = 0
	#color_list = ["b", "r", "g", "y", "orange"]
	#color_list = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
	color_list = []
	color = ""
	label_list = ["schedutil", "fixed 30%", "fixed 40%", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance", "powersave"]
	label = ""
	ticklabel_list = []

	clusterlen = len(latency_list)
	width = 1
	offset_list = np.arange(0, clusterlen)

	color_list.append("red")
	for i in range(clusterlen - 1):
		color_list.append("blue")
	#end_for

	fig_list, ax_list = plt.subplots(3, 1)

	#ticklabel_list.append("")

	for latency, cacherefs, cachemisses, offset, color, label in zip(latency_list, cacherefs_list, cachemisses_list, offset_list, color_list, label_list):

		ax_list[0].bar(offset, latency, width = width, color = color)
		ax_list[1].bar(offset, cacherefs / 1000000, width = width, color = color)
		ax_list[2].bar(offset, cachemisses / 1000000, width = width, color = color)

		offset_list += width

		ticklabel_list.append(label)

	#end_for

	print(ticklabel_list)
	#'''
	for i in range(len(ax_list)):
		ax_list[i].set_xticks(np.arange(0, offset_list[0]) * 2, False)
	#end_for
	ax_list[0].set_xticklabels([])
	ax_list[1].set_xticklabels([])
	ax_list[2].set_xticklabels(ticklabel_list)
	tick_list = ax_list[2].get_xticklabels()
	for i in range(len(tick_list)):
		tick_list[i].set_rotation(-45)
		tick_list[i].set_ha("left")
	#end_for
	#'''

	ax_list[0].set_title("Runtime for different CPU governors:  " + benchname, fontsize = 20, fontweight = "bold")
	ax_list[2].set_xlabel("Governor", fontsize = 16, fontweight = "bold")
	ax_list[0].set_ylabel("Total runtime ($ms$)", fontsize = 16, fontweight = "bold")
	ax_list[1].set_ylabel("Cache refs (M)", fontsize = 16, fontweight = "bold")
	ax_list[2].set_ylabel("Cache misses (M)", fontsize = 16, fontweight = "bold")

	plt.show()
	plt.close("all")


	fig_list, ax_list = plt.subplots(2, 1)

	handle_list = []
	for latency, cacherefs, cachemisses, color, i, label in zip(latency_list, cacherefs_list, cachemisses_list, color_list, range(clusterlen), label_list):
		ax_list[0].scatter(cachemisses / 1000000, latency, color = color, s = 50)
		ax_list[0].annotate(str(i), (cachemisses / 1000000 + .1, latency + 10), fontweight = "bold")
		ax_list[1].scatter(cacherefs / 1000000, latency, color = color, s = 50)
		ax_list[1].annotate(str(i), (cacherefs / 1000000 + 2, latency + 10), fontweight = "bold")
		handle_list.append(Line2D([], [], label = str(i) + " = " + label, linewidth = 0))
	#end_for

	ax_list[0].set_title("Runtime and Cache Misses for a Given CPU Governor", fontsize = 10, fontweight = "bold")
	ax_list[0].set_xlabel("Cache misses (M)", fontsize = 16, fontweight = "bold")
	ax_list[0].set_ylabel("Total runtime ($ms$)", fontsize = 16, fontweight = "bold")
	ax_list[0].legend(handles = handle_list)
	ax_list[1].set_xlabel("Cache references (M)", fontsize = 16, fontweight = "bold")
	ax_list[1].set_ylabel("Total runtime ($ms$)", fontsize = 16, fontweight = "bold")
	ax_list[1].legend(handles = handle_list)

	plt.show()

	return

#end_def


def bargraph_energy(energy_list, benchname):

	# energy_list = []
	# benchname = ""
	energy = 0.0
	clusterlen = 0
	width = 0
	#color_list = ["b", "r", "g", "y", "orange"]
	#color_list = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
	color_list = []
	color = ""
	label_list = ["schedutil", "fixed 30", "fixed 40", "fixed 50", "fixed 60", "fixed 70", "fixed 80", "fixed 90", "performance"]
	label = ""
	ticklabel_list = []
	output_file = ""  # file obj

	clusterlen = len(energy_list)
	width = 1
	offset_list = np.arange(0, clusterlen)

	color_list.append("red")
	for i in range(clusterlen - 1):
		color_list.append("blue")
	#end_for

	output_file = open("data.tex", "w")

	fig, ax = plt.subplots()

	#ticklabel_list.append("")

	for energy, offset, color, label in zip(energy_list, offset_list, color_list, label_list):

		ax.bar(offset, energy, width = width, color = color)

		offset_list += width

		ticklabel_list.append(label + "\n" + str(int(energy)))

		output_file.write("%s & %f \\\\\n" % (label, energy))

	#end_for

	output_file.close()

	print(ticklabel_list)
	#'''
	ax.set_xticks(np.arange(0, offset_list[0]) * 2, False)
	ax.set_xticklabels(ticklabel_list)
	tick_list = ax.get_xticklabels()
	for i in range(len(tick_list)):
		tick_list[i].set_rotation(-45)
		tick_list[i].set_ha("left")
	#end_for
	#'''

	ax.set_title("Net Energy for different CPU governors:  " + benchname, fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Net energy ($\mu Ah$)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()
	plt.show()

	return

#end_def


def main():

	path = ""
	filename = ""
	workloads = []
	governors = []
	prefix = ""
	workload = ""
	governor = ""
	latency = 0.0
	latency_list = []
	energy = 0.0
	energy_list = []
	delay = ""
	saturation = ""
	benchname = ""
	cacherefs_list = []
	cacherefs = 0
	cachemisses_list = []
	cachemisses = 0

	path = sys.argv[1]
	benchname = "Bubblesort (10k ints, 64 per 4k page):\nRuntime for different CPU policies"
	#benchname = " Youtube (150s video playback) (with kernel trace)"

	# Get latency data:

	governors = ["schedutil_none", "userspace_30", "userspace_40", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none"]
	prefix = "/micro_SQL_"
	workload = "A"
	delay = "0ms"

	latency_list = []
	for governor in governors:

		filename = path + prefix + workload + "_" + delay + "_" + governor + "_1_0.gz"
		latency, cacherefs, cachemisses = get_runtime(filename)
		latency = process_loglines(filename)
		print(filename + " : " + str(latency))

		latency_list.append(latency)
		cacherefs_list.append(cacherefs)
		cachemisses_list.append(cachemisses)

	#end_for

	bargraph_latency(latency_list, cacherefs_list, cachemisses_list, benchname)

	return

	# Get energy data:

	prefix = "/monsoon_SQL_"
	workload = "A"
	delay = "0ms"

	energy_list = []
	for governor in governors:

		filename = path + prefix + workload + "_" + delay + "_" + governor + "_1_0.csv"
		energy = get_energy(filename)
		print(filename + " : " + str(energy))

		energy_list.append(energy)

	#end_for

	bargraph_energy(energy_list, benchname)

	return

#end_def


def quick():

	filename = ""

	filename = sys.argv[1]

	process_loglines(filename)

	return

#end_def


main()
#quick()

