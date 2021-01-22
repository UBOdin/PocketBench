
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


def plot_graph(latency_list_list):

	# latency_list_list = []

	latency_list = []
	latency = 0.0
	clusterlen = 0
	width = 0
	color_list = ["b", "r", "y", "g"]
	color = ""
	label_list = ["schedutil", "midspeed", "performance", "powersave"]
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
	ticklabel_list[6] = "\n\n\n\n\n                          Workload B"
	ticklabel_list[12] = "\n\n\n\n\n                          Workload C"
	ticklabel_list[18] = "\n\n\n\n\n                          Workload D"
	print(ticklabel_list)

	ax.set_xticks(np.arange(0, offset_list[0]) - 1, False)
	ax.set_xticklabels(ticklabel_list)
	tick_list = ax.get_xticklabels()
	for i in range(len(tick_list)):
		if (i % 6 != 0):
			tick_list[i].set_rotation(-45)
			tick_list[i].set_ha("left")
		#end_if
	#end_for



	ax.set_title("Latency Per Governor and Workload", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor and Workload", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total latency (s)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()

	plt.show()

	return

#end_def


def main():

	filename = ""
	#workloads = ["A", "B", "C", "D", "E", "F"]
	workloads = ["A", "B", "C", "E"]
	governors = ["schedutil_none", "userspace_x", "performance_none", "powersave_none"]
	prefix = "../logs/YCSB_SQL_"
	workload = ""
	governor = ""
	latency = 0.0
	latency_list = []
	latency_list_list = []

	for workload in workloads:

		latency_list = []
		for governor in governors:

			filename = prefix + workload + "_log_" + governor + "_1.gz"

			latency = get_latency(filename)
			print(filename + " : " + str(latency))

			latency_list.append(latency)

		#end_for

		latency_list_list.append(latency_list)

	#end_for

	print(latency_list_list)

	plot_graph(latency_list_list)

	return

#end_def


def quick():

	filename = ""
	latency = 0.0

	filename = "logs/YCSB_SQL_A_log_schedutil_none_1.gz"

	latency = get_latency(filename)

	print("Latency:  %f" %(latency))

	return

#end_def


main()


