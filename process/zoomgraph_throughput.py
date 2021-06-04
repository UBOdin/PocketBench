
import json
import sys
import gzip

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

	if (n == 1):
		return data_list[0], 0
	#end_if

	mean = statistics.mean(data_list)
	stdev = statistics.stdev(data_list) # stdev() or pstdev()
	margin = zstar * (stdev / math.sqrt(n))

	return mean, margin

#end_def


def get_latency(file_name):

	input_file = "" # file handle
	logline = ""
	iteration = 0
	starttime = 0.0
	endtime = 0.0

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

		if ("_START" in logline):
			starttime += float(logline[33:46])
		#end_if

		if ("_END" in logline):
			endtime += float(logline[33:46])
		#end_if

	#end_while

	'''
	print("iterations:  %d" % (iteration))
	print(starttime)
	print(endtime)
	print("Latency:  ", endtime - starttime)
	'''
	#print(file_name + "  " + str(endtime - starttime))


	input_file.close()

	return endtime - starttime

#end_def


def get_latency_list(prefix, threads):

	filename = ""
	raw_latency = 0.0
	latency = 0.0
	throughput = 0.0
	runs = 5
	pathname = ""
	perrun_latency_list = []
	perrun_throughput_list = []
	latency_mean = 0.0
	latency_error = 0.0
	throughput_mean = 0.0
	throughput_error = 0.0
	perthread_latency_mean_list = []
	perthread_latency_error_list = []
	perthread_throughput_mean_list = []
	perthread_throughput_error_list = []

	# Can't just use os.walk or get filelist -- order matters
	for i in range(1, threads + 1):

		filename = "YCSB_" + prefix + "_0ms_interactive_none_" + str(i) + ".gz" # "threading/c/sql_c_0.gz"

		perrun_latency_list = []
		for j in range(1, runs + 1):
			#pathname = "throughput_" + str(j) + "/" + filename
			pathname = "logs/run_" + str(j) + "/" + filename
			#print(pathname)
			raw_latency = get_latency(pathname)

			#latency = raw_latency * 1000 / (1800 * (i))
			#throughput = (1800 * (i)) / (raw_latency / (i))

			latency = (raw_latency * 1000 ) / 1800
			throughput = 1800 / (raw_latency / (i))

			perrun_latency_list.append(latency)
			perrun_throughput_list.append(throughput)

			print("Threads:  " + str(i) + "  Per thread latency:  " + str(raw_latency))
			#print(latency, throughput)
		#end_for

		latency_mean, latency_error = mean_margin(perrun_latency_list)
		perthread_latency_mean_list.append(latency_mean)
		perthread_latency_error_list.append(latency_error)

		throughput_mean, throughput_error = mean_margin(perrun_throughput_list)
		perthread_throughput_mean_list.append(throughput_mean)
		perthread_throughput_error_list.append(throughput_error)

		print(prefix + " " + str(i) + " threads:  " + str(perrun_latency_list))

	#end_for

	print("\nMean latency of 6 runs, for each of threadcounts 1-8:")
	print(perthread_latency_mean_list)
	print()

	return perthread_latency_mean_list, perthread_latency_error_list, perthread_throughput_mean_list, perthread_throughput_error_list

#end_def


def main():

	#print("Hello World")

	workload = ""
	threadcount = 10

	workload = sys.argv[1]  # "A"

	fig, ax = plt.subplots()


	latency_mean_list, latency_error_list, throughput_mean_list, throughput_error_list = get_latency_list("SQL_" + workload, threadcount)

	plt.plot(throughput_mean_list, latency_mean_list, color = "blue", marker = "o", markersize = 12, label = "SQLite (number of threads)")

	#'''
	for i in range(0, threadcount):
		plt.annotate(str(i + 1), xy = (throughput_mean_list[i] + 7, latency_mean_list[i] + 0.3), fontsize = 16)
	#end_for
	#'''

	print()
	print("SQLite mean throughput (threads 1-8):  " + str(throughput_mean_list))
	print("SQLite mean latency (threads 1-8):  " + str(latency_mean_list))
	print()

	latency_mean_list, latency_error_list, throughput_mean_list, throughput_error_list = get_latency_list("BDB_" + workload, threadcount)

	plt.plot(throughput_mean_list, latency_mean_list, color = "red", marker = "o", markersize = 12, label = "BDB (number of threads)")

	#'''
	for i in range(0, threadcount):
		plt.annotate(str(i + 1), xy = (throughput_mean_list[i] + 5, latency_mean_list[i] + 0.5), fontsize = 16)
	#end_for
	#'''

	print()
	print("BDB mean throughput (threads 1-8):  " + str(throughput_mean_list))
	print("BDB mean latency (threads 1-8):  " + str(latency_mean_list))


	#plt.annotate("-----Region of Interest", xy = (350, 1.5), fontsize = 16)

	ax.set_title("YCSB Workload " + workload, fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Throughput (queries/s)", fontsize = 20, fontweight = "bold")
	ax.set_ylabel("Average Latency (ms)", fontsize = 20, fontweight = "bold")

	#ax.set_aspect(1/220.0)

	#ax.axvspan(200, 400, alpha=.5, color="grey")

	fig15 = plt.gcf()
	fig15.tight_layout()

	plt.legend(loc = "top right")


	#plt.axis([200, 1700, 0, 6.5])
	plt.show()

#end_def

main()


