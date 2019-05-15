
import json
import sys
import gzip
import json
import os

import matplotlib.pyplot as plt
import numpy as np

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

	return mean, margin, margin / mean

#end_def


def get_latency_nonio(filename):

	#print("Hello world %s, %d" % ("bye", 20))

	input_file_name = ""
	logline = ""
	iteration = 0
	starttime = 0.0
	endtime = 0.0

	line_list = []
	subline_list = []
	read_first = 0
	read_last = 0
	read_net = 0
	write_first = 0
	write_last = 0
	write_net = 0
	sync_first = 0
	sync_last = 0
	sync_net = 0
	count = 0
	latency = 0
	nonio = 0

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
			starttime += float(logline[33:46])
		#end_if

		if ("_END" in logline):
			endtime += float(logline[33:46])
		#end_if

		if ("tracing_" in logline):

			if (logline[0:16] != " chmark_withjson"):
				continue
				#print(logline)
			#end_if


			line_list = logline.split("tracing_mark_write: ")
			subline_list = line_list[1].split(" ")

			if (subline_list[0] != "PocketData"):
				pass
				#continue
			#end_if

			if (subline_list[1] == "R"):
				if (read_first == 0):
					read_first = int(subline_list[7])
				#end_if
				read_last = int(subline_list[7])
				count = int(subline_list[9])
			#end_if

			if (subline_list[1] == "W"):
				if (write_first == 0):
					write_first = int(subline_list[7])
				#end_if
				write_last = int(subline_list[7])
			#end_if

			if (subline_list[1] == "S"):
				if (sync_first == 0):
					sync_first = int(subline_list[7])
				#end_if
				sync_last = int(subline_list[7])
			#end_if

		#end_if

	#end_while

	input_file.close()

	read_net = read_last - read_first
	write_net = write_last - write_first
	sync_net = sync_last - sync_first

	latency = int((endtime - starttime) * 1000000)
	nonio = latency - read_net - write_net - sync_net

	print(filename)
	print("iterations:  %d" % (iteration))
	print(starttime)
	print(endtime)
	print("Latency:  ", latency)
	print("Read time:  " + str(read_net))
	print("Write time:  " + str(write_net))
	print("Sync time:  " + str(sync_net))
	print("Count:  " + str(count))
	print("nonio:  " + str(nonio))

	return latency, nonio

#end_def


def main():

	file_list = []
	prefix = "variance_2/" #logs/"
	latency = 0
	latency_list = []
	nonio = 0
	nonio_list = []
	runs = 0

	file_list = os.listdir(prefix)

	for filename in file_list:
		if (filename[0:4] != "log_"): #YCSB"):
			continue
		#end_if
		latency, nonio = get_latency_nonio(prefix + filename)
		latency_list.append(latency)
		nonio_list.append(nonio)
	#end_for

	print(nonio_list)
	print(latency_list)
	print(mean_margin(nonio_list))
	print(mean_margin(latency_list))

	fig, ax = plt.subplots()

	runs = len(latency_list)

	plt.bar(range(1, runs + 1), latency_list, color = "blue", label = "I/O time (both on/off CPU)")
	plt.bar(range(1, runs + 1), nonio_list, color = "red", label = "Non-I/O time (both on/off CPU)")

	plt.axis([0, 21, 0, 15000000])
	plt.legend(loc = "upper center")
	plt.title("Workload A (Saturated CPU)", fontsize = 20, fontweight = "bold")
	ax.set_ylabel("Total Latency (ms)", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Workload run #", fontsize = 20, fontweight = "bold")
	fig15 = plt.gcf()
	fig15.tight_layout()

	plt.show()

#end_def


main()




