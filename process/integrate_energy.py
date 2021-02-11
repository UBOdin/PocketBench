
import json
import sys
import gzip
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches


def get_latency(file_name):

	# file_name = ""

	logline = ""
	iteration = 0
	starttime = 0.0
	endtime = 0.0

	input_file = gzip.open(file_name, "r")

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

		if ("_START" in logline):
			starttime += float(logline[33:46])
		#end_if

		if ("_END" in logline):
			endtime += float(logline[33:46])
		#end_if

	#end_while

	#print("iterations:  %d" % (iteration))

	#print(starttime)
	#print(endtime)
	#print("Latency:  ", endtime - starttime)

	input_file.close()

	return endtime - starttime

#end_def


def get_energy(file_name, start, stop):

	# file_name = ""
	# start = 0.0
	# stop = 0.0

	logline = ""
	logline_list = []
	iteration = 0
	time = 0.0
	amps = 0.0
	watts = 0.0
	volts = 0.0

	amps_total = 0.0
	watts_total = 0.0

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
		if (len(logline_list) != 4):
			print("Error:  Unexpected line length")
			sys.exit(1)
		#end_if

		time = float(logline_list[0])
		amps = float(logline_list[1])
		watts = float(logline_list[2])
		volts = float(logline_list[3])

		# Sanity
		if ((volts < 3.9) or (volts > 4.1)):
			print("Error:  Unexpected voltage")
			sys.exit(1)
		#end_if

		if (time <= start):
			continue
		#end_if

		if (time > stop):
			break
		#end_if

		amps_total += amps
		watts_total += watts

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


def plot_latency_bargraph(latency_list_list):

	# latency_list_list = []

	latency_list = []
	latency = 0.0
	clusterlen = 0
	width = 0
	color_list = ["b", "r", "g", "y", "orange"]
	color = ""
	#label_list = ["schedutil", "midspeed", "performance", "powersave"]
	label_list = ["schedutil", "fixed 50%", "fixed 80%", "performance", "powersave"]
	label = ""
	ticklabel_list = []

	clusterlen = len(latency_list_list[0])
	width = 1
	offset_list = np.arange(0, clusterlen)

	fig, ax = plt.subplots()

	ticklabel_list.append("")
	for latency_list in latency_list_list:

		for latency, offset, color, label in zip(latency_list, offset_list, color_list, label_list):

			ax.bar(offset, latency, width = width, color = color)

			offset_list += width

			ticklabel_list.append(label)

		#end_for

		ticklabel_list.append("")
		ticklabel_list.append("")

		offset_list += 2

	#end_for

	print("offset:  %f" % (offset_list[0]))

	ticklabel_list[0] = "\n\n\n\n\n                          Workload A"
	ticklabel_list[7] = "\n\n\n\n\n                          Workload B"
	ticklabel_list[14] = "\n\n\n\n\n                          Workload C"
	ticklabel_list[21] = "\n\n\n\n\n                          Workload D"
	ticklabel_list[28] = "\n\n\n\n\n                          Workload E"
	ticklabel_list[35] = "\n\n\n\n\n                          Workload F"

	print(ticklabel_list)

	ax.set_xticks(np.arange(0, offset_list[0]) - 1, False)
	ax.set_xticklabels(ticklabel_list)
	tick_list = ax.get_xticklabels()
	for i in range(len(tick_list)):
		if (i % 7 != 0):
			tick_list[i].set_rotation(-45)
			tick_list[i].set_ha("left")
		#end_if
	#end_for


	ax.set_title("Latency Per Governor and Workload:\nSaturated CPU", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor and Workload", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total latency ($s$)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()
	plt.show()

	return

#end_def


def plot_energy_bargraph(energy_list_list):

	# energy_list_list = []

	energy_list = []
	energy = 0.0
	clusterlen = 0
	width = 0
	color_list = ["b", "r", "g", "y", "orange"]
	color = ""
	label_list = ["schedutil", "fixed 50%", "fixed 80%", "performance", "powersave"]
	label = ""
	ticklabel_list = []

	clusterlen = len(energy_list_list[0])
	width = 1
	offset_list = np.arange(0, clusterlen)

	fig, ax = plt.subplots()

	ticklabel_list.append("")
	for energy_list in energy_list_list:

		for energy, offset, color, label in zip(energy_list, offset_list, color_list, label_list):

			ax.bar(offset, energy, width = width, color = color)

			offset_list += width

			ticklabel_list.append(label)

		#end_for

		ticklabel_list.append("")
		ticklabel_list.append("")

		offset_list += 2

	#end_for

	print("offset:  %f" % (offset_list[0]))

	ticklabel_list[0] = "\n\n\n\n\n                          Workload A"
	ticklabel_list[7] = "\n\n\n\n\n                          Workload B"
	ticklabel_list[14] = "\n\n\n\n\n                          Workload C"
	ticklabel_list[21] = "\n\n\n\n\n                          Workload D"
	ticklabel_list[28] = "\n\n\n\n\n                          Workload E"
	ticklabel_list[35] = "\n\n\n\n\n                          Workload F"

	print(ticklabel_list)

	ax.set_xticks(np.arange(0, offset_list[0]) - 1, False)
	ax.set_xticklabels(ticklabel_list)
	tick_list = ax.get_xticklabels()
	for i in range(len(tick_list)):
		if (i % 7 != 0):
			tick_list[i].set_rotation(-45)
			tick_list[i].set_ha("left")
		#end_if
	#end_for


	ax.set_title("Net Energy Per Governor and Workload:\nSaturated CPU", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor and Workload", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Net energy ($\mu Ah$)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()
	plt.show()

	return

#end_def


def main():

	filename = ""
	workloads = []
	governors = []
	prefix = ""
	workload = ""
	governor = ""
	latency = 0.0
	latency_list = []
	latency_list_list = []
	energy = 0.0
	energy_list = []
	energy_list_list = []


	# Get latency data:

	workloads = ["A", "B", "C", "D", "E", "F"]
	#workloads = ["A", "B", "C", "E"]
	governors = ["schedutil_none", "userspace_50", "userspace_80", "performance_none", "powersave_none"]
	#prefix = "../logs/save0ms/YCSB_SQL_"
	prefix = "../logs/save_latency/YCSB_SQL_"

	for workload in workloads:

		latency_list = []
		for governor in governors:

			filename = prefix + workload + "_0ms_" + governor + "_1.gz"
			#filename = prefix + workload + "_log_" + governor + "_1.gz"

			latency = get_latency(filename)
			print(filename + " : " + str(latency))

			latency_list.append(latency)

		#end_for

		latency_list_list.append(latency_list)

	#end_for

	plot_latency_bargraph(latency_list_list)


	# Get energy data:

	workloads = ["a", "b", "c", "d", "e", "f"]
	governors = ["schedutil", "fix50", "fix80", "performance", "powersave"]
	prefix = "../logs/energy_csv/sql_"

	# Really awful kludge:  manually observed start/stop times, to nearest second:
	# 0ms
	start_list_list = [[24, 24, 24, 23, 24], [24, 24, 24, 24, 25], [24, 18, 24, 21, 24], [24, 22, 25, 24, 24], [25, 24, 25, 23, 23], [25, 24, 24, 24, 25]]
	stop_list_list =  [[32, 32, 30, 29, 43], [31, 31, 31, 29, 44], [33, 25, 31, 26, 43], [31, 30, 31, 29, 43], [38, 39, 38, 32, 61], [32, 32, 31, 30, 43]]
	# log
	#start_list_list = [[24, 22, 23, 18, 25], [24, 23, 26, 24, 24], [25, 26, 25, 24, 15], [23, 25, 21, 24, 22], [23, 24, 24, 18, 19], [24, 25, 24, 23, 24]]
	#stop_list_list =  [[103, 85, 84, 89, 108], [91, 83, 77, 56, 93], [90, 81, 74, 71, 85], [87, 81, 71, 68, 90], [119, 94, 95, 62, 127], [102, 88, 83, 72, 108]]

	start_list = []
	stop_list = []
	start = 0.0
	stop = 0.0

	null_list = [23, 25, 23, 25, 24]
	null_start = 0.0
	null_energy = 0.0

	for workload, start_list, stop_list in zip(workloads, start_list_list, stop_list_list):

		energy_list = []
		for governor, start, stop, null_start in zip(governors, start_list, stop_list, null_list):

			filename = prefix + workload + "_0ms_" + governor + ".csv"
			#filename = prefix + workload + "_log_" + governor + ".csv"
			energy = get_energy(filename, start, stop)
			print(filename + " : " + str(energy))

			print("Times:  %d %d %d" % (start, stop, stop - start))

			# Get null energy:
			filename = "../logs/energy_csv/sql_n_null_" + governor + ".csv"
			null_energy = get_energy(filename, null_start, null_start + (stop - start))
			print("Null energy:  %f" % (null_energy))

			energy_list.append(energy - null_energy)

		#end_for

		energy_list_list.append(energy_list)

	#end_for

	plot_energy_bargraph(energy_list_list)

	return

#end_def


def quick():

	filename = ""
	energy = 0.0

	filename = "sql_a_0ms_fix50.csv"

	energy = get_energy(filename)

	print("Energy:")

	return

#end_def


main()
#quick()


