
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

	return (endtime - starttime) * 1000.0

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

	start = 7.0  # fixed
	stop = float(iteration - 2) / 5000.0 - 19.0  # Set stop to 19s before end
	iteration = 0  # reset counter
	print("File:  %s  Stop:  %f" % (file_name, stop))

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


def bargraph_latency(latency_list_list, saturation):

	# latency_list_list = []
	# saturation = ""
	latency_list = []
	latency = 0.0
	clusterlen = 0
	width = 0
	#color_list = ["b", "r", "g", "y", "orange"]
	color_list = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
	color = ""
	#label_list = ["schedutil", "fixed 50%", "fixed 80%", "performance", "powersave"]
	label_list = ["schedutil", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance", "powersave"]
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


	ax.set_title("Latency Per Governor and Workload:\n" + saturation + " CPU", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor and Workload", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total latency ($ms$)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()
	plt.show()

	return

#end_def


def bargraph_energy(energy_list_list, saturation):

	# energy_list_list = []
	# saturation = ""
	energy_list = []
	energy = 0.0
	clusterlen = 0
	width = 0
	#color_list = ["b", "r", "g", "y", "orange"]
	color_list = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
	color = ""
	#label_list = ["schedutil", "fixed 50%", "fixed 80%", "performance", "powersave"]
	label_list = ["schedutil", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance", "powersave"]
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


	ax.set_title("Net Energy Per Governor and Workload:\n" + saturation + " CPU", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor and Workload", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Net energy ($\mu Ah$)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()
	plt.show()

	return

#end_def


def scatterplot_latency_energy(latency_list_list, energy_list_list, saturation):

	# latency_list_list = []
	# energy_list_list = []
	# saturation = ""
	latency_list = []
	latency = 0.0
	latency_max = 0.0
	energy_list = []
	energy = 0.0
	energy_max = 0.0

	#latency_list = latency_list_list[0]
	#energy_list = energy_list_list[0]

	marker_list = ['o', 's', 'd', '>', '<']
	#label_list = ["schedutil", "fixed 50%", "fixed 80%", "performance", "powersave"]
	label_list = ["schedutil", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance", "powersave"]

	workload_list = ["A", "B", "C", "D", "E", "F"]

	fig, ax_list_list = plt.subplots(2, 3)
	ax = "" # pyplot object

	for latency_list, energy_list, workload, i in zip(latency_list_list, energy_list_list, workload_list, range(len(workload_list))):

		latency_max = max(latency_list)
		energy_max = max(energy_list)

		ax = ax_list_list[(i / 3), (i % 3)]
		#ax = ax_list_list[i]

		print(i)
		print(latency_list)
		print(energy_list)

		for latency, energy, marker, label in zip(latency_list, energy_list, marker_list, label_list):
			ax.plot(latency, energy, marker = marker, markersize = 12, label = label)
		#end_for

		ax.axis([0, latency_max * 1.1, 0, energy_max * 1.1])

		ax.legend(loc = "lower right", handlelength = .8)

		ax.set_title("Workload " + workload + " -- " + saturation + " CPU", fontsize = 16, fontweight = "bold")
		ax.set_xlabel("Total workload runtime ($ms$)\n", fontsize = 16, fontweight = "bold")
		ax.set_ylabel("Net energy cost ($\mu Ah$)", fontsize = 16, fontweight = "bold")

	#end_for

	#plt.tight_layout()
	plt.subplots_adjust(hspace = .3)
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
	delay = ""
	saturation = ""

	#delay = "0ms"  # Kludge -- 0ms or lognormal delay
	delay = "0ms"
	if (delay == "0ms"):
		saturation = "Saturated"
	elif (delay == "log"):
		saturation = "Unsaturated"
	else:
		print("Error:  Unexpected delay")
		sys.exit(1)
	#end_if

	# Get latency data:

	workloads = ["A", "B", "C", "D", "E", "F"]
	#workloads = ["A", "B", "C", "E"]
	#governors = ["schedutil_none", "userspace_50", "userspace_80", "performance_none", "powersave_none"]
	governors = ["schedutil_none", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none", "powersave_none"]
	prefix = "../logs/newdir/YCSB_SQL_"

	for workload in workloads:

		latency_list = []
		for governor in governors:

			filename = prefix + workload + "_" + delay + "_" + governor + "_1.gz"

			latency = get_latency(filename)
			print(filename + " : " + str(latency))

			latency_list.append(latency)

		#end_for

		latency_list_list.append(latency_list)

	#end_for

	bargraph_latency(latency_list_list, saturation)


	# Get energy data:

	prefix = "../logs/combined/monsoon_SQL_"

	for workload in workloads:

		energy_list = []
		for governor in governors:

			filename = prefix + workload + "_" + delay + "_" + governor + "_1.csv"
			energy = get_energy(filename)
			print(filename + " : " + str(energy))

			energy_list.append(energy)

		#end_for

		energy_list_list.append(energy_list)

	#end_for

	bargraph_energy(energy_list_list, saturation)


	scatterplot_latency_energy(latency_list_list, energy_list_list, saturation)

	return

#end_def


def bargraph_ex1():

	prefix = ""
	energy_list = []
	energy = 0.0
	energy_mean_list = []
	energy_mean = 0.0
	energy_err = 0.0
	governor_list = []
	offset_list = []
	color_list = []
	color = ""
	runcount = 0
	runno = 0

	#prefix = "../logs/save_runs_20210618/experiment_1/monsoon_SQL_"
	#prefix = "../logs/save_runs_20210618/experiment_2_500/monsoon_SQL_"
	prefix = "../logs/save_runs_20210618/experiment_2_1000/monsoon_SQL_"
	governor_list = ["schedutil_none", "userspace_30", "userspace_40", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none"]
	workload = "F"  # N.b. N/A for micro experiments
	delay = "0ms"  # N.b. N/A for micro experiments

	runcount = 3
	for governor in governor_list:
		energy_list = []
		for runno in range(runcount):
			filename = prefix + workload + "_" + delay + "_" + governor + "_1_" + str(runno) + ".csv"
			energy = get_energy(filename)
			print(filename + " : " + str(energy))
			energy_list.append(energy)
		#end_for
		energy_mean, energy_err = mean_margin(energy_list)
		energy_mean_list.append(energy_mean)
		if (governor == "schedutil_none"):
			color = "red"
		else:
			color = "blue"
		#end_if
		color_list.append(color)
	#end_for


	label_list = ["default", "fixed 30", "fixed 40", "fixed 50", "fixed 60", "fixed 70", "fixed 80", "fixed 90", "performance"]
	listlen = len(energy_mean_list)
	offset_list = np.arange(0, listlen)

	print("Len:  " + str(listlen))

	fig, ax = plt.subplots()

	for offset, energy_mean, color, label in zip(offset_list, energy_mean_list, color_list, label_list):
		ax.bar(offset, energy_mean, color = color) #, width = width, color = color)
	#end_for

	ax.set_xticks(np.arange(0, listlen), minor = False)
	ax.set_xticklabels(label_list)
	#ax.set_title("Experiment 1:  Energy Per Run (Average of 3)", fontsize = 20, fontweight = "bold")
	#ax.set_title("Experiment 2 (.5ms sleep):  Energy Per Run (Average of 3)", fontsize = 20, fontweight = "bold")
	ax.set_title("Experiment 2 (1ms sleep):  Energy Per Run (Average of 3)", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor policy", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total energy ($\mu Ah$)", fontsize = 16, fontweight = "bold")

	plt.show()

	return

#end_def


def quick():

	filename = ""
	energy = 0.0

	filename = sys.argv[1]

	energy = get_energy(filename)

	print("Energy:  %f" % (energy))

	return

#end_def


#main()
#quick()
bargraph_ex1()

