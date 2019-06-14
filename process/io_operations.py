
import json
import sys
import gzip
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


def get_latency(filename):

	#print("Hello world %s, %d" % ("bye", 20))

	input_file_name = ""
	logline = ""
	iteration = 0
	starttime = 0.0
	endtime = 0.0

	line_list = []
	subline_list = []
	pid = 0
	time = 0.0
	timestamp_list = []
	operation_list = []
	operation = ""

	input_file = gzip.open(filename)

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

		if ("_START" in logline):

			pid = logline[17:21]
			time = float(logline[33:46])

			starttime += time
			track = True

		#end_if

		if ("_END" in logline):

			time = float(logline[33:46])

			endtime += time
			track = False

			break

		#end_if

		if ("tracing_" in logline):

			if (pid != logline[17:21]):
				continue
				#print(logline)
			#end_if

			time = float(logline[33:46])

			line_list = logline.split("tracing_mark_write: ")
			subline_list = line_list[1].split(" ")
			operation = subline_list[0]

			if ((operation != "R") and (operation != "W") and (operation != "S")):
				continue
			#end_if

			timestamp_list.append(time)
			operation_list.append(subline_list[0]) # R W S

		#end_if

	#end_while

	input_file.close()

	return timestamp_list, operation_list

#end_def


def main():

	print("Hello World")

	filename = ""
	subname = []
	workload = ""
	delay = ""
	timestamp_list = []
	base_time = 0.0
	max_count = 0.0
	io_type_list = []
	io_count_list = []
	marker_dict = {"R":".", "W":"+", "S":"s"}
	color_dict = {"R":"red", "W":"orange", "S":"blue"}

	filename = sys.argv[1]
	timestamp_list, io_type_list = get_latency(filename)	

	subname_list = filename.split("YCSB_")[1].split("_")
	workload = subname_list[1]
	delay = subname_list[2]

	base_time = timestamp_list[0]
	timestamp_list = [ e - base_time for e in timestamp_list ]
	max_time = timestamp_list[-1]

	max_count = len(io_type_list)
	for i in range(max_count):
		io_count_list.append(i)
	#end_for

	print(len(io_type_list))
	print(len(io_count_list))
	print(len(timestamp_list))

	fig, ax = plt.subplots()

	operation = ""
	marker = ""

	#ax.plot(timestamp_list, io_count_list)
	for i in range(0, len(timestamp_list)):
		operation = io_type_list[i]
		#print(operation)
		marker = marker_dict[operation]
		#print(marker)
		ax.scatter(timestamp_list[i], io_count_list[i], s = 20, color = color_dict[io_type_list[i]], marker = marker_dict[io_type_list[i]])
	#end_for

	ax.set_title("YCSB Workload " + workload + " (" + delay + " delay)", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Time since first query ($s$)", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Number of IO events", fontsize = 16, fontweight = "bold")
	#ax.set_ylim([0, 2.7])
	#ax.set_xlim([0, max_time])

	legend_read = mlines.Line2D([], [], linewidth = 0, marker = ".", label = "Reads", color = "red")
	legend_write = mlines.Line2D([], [], linewidth = 0, marker = "+", label = "Writes", color = "orange")
	legend_sync = mlines.Line2D([], [], linewidth = 0, marker = "s", label = "Syncs", color = "blue")

	plt.legend(handles = [legend_read, legend_write, legend_sync], loc = "lower right")

	plt.show()

	fig.savefig("graphs/frequency_" + workload + "_" + delay + ".pdf", bbox_inches = "tight")

#end_def


main()




