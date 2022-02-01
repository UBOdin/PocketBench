
import json
import sys
import gzip
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

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

	return (endtime - starttime) * 1000.0, cycles / (1000.0 * 1000.0)

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


def bargraph_latency(latency_list, benchname):

	# latency_list = []
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

	fig, ax = plt.subplots()

	#ticklabel_list.append("")

	for latency, offset, color, label in zip(latency_list, offset_list, color_list, label_list):

		ax.bar(offset, latency, width = width, color = color)

		offset_list += width

		ticklabel_list.append(label)

	#end_for

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

	ax.set_title("Latency Per Governor" + benchname, fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total latency ($ms$)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()
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

	ax.set_title("Net Energy Per Governor" + benchname, fontsize = 20, fontweight = "bold")
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

	path = sys.argv[1]
	benchname = " Youtube (150s video playback) (no kernel trace)"
	#benchname = " Youtube (150s video playback) (with kernel trace)"

	# Get latency data:

	governors = ["schedutil_none", "userspace_30", "userspace_40", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none"]
	prefix = "/micro_SQL_"
	workload = "A"
	delay = "0ms"

	latency_list = []
	for governor in governors:

		filename = path + prefix + workload + "_" + delay + "_" + governor + "_1_0.gz"
		latency = get_runtime(filename)
		print(filename + " : " + str(latency))

		latency_list.append(latency)

	#end_for

	bargraph_latency(latency_list, benchname)

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


main()

