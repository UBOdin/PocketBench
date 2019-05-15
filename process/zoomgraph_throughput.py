
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

	print("iterations:  %d" % (iteration))

	print(starttime)
	print(endtime)
	print("Latency:  ", endtime - starttime)

	input_file.close()

	return endtime - starttime

#end_def


def get_latency_list(prefix):

	filename = ""
	threads = 6
	latency = 0.0
	perthread_latency_mean_list = []
	perthread_latency_error_list = []
	runs = 6
	pathname = ""
	perrun_latency_list = []
	latency_mean = 0.0
	latency_error = 0.0

	# Can't just use os.walk or get filelist -- order matters
	for i in range(1, threads + 1):

		filename = "YCSB_" + prefix + "_0ms_interactive_none_" + str(i) + ".gz" # "threading/c/sql_c_0.gz"

		perrun_latency_list = []
		for j in range(1, runs + 1):
			pathname = "throughput_" + str(j) + "/" + filename
			print(pathname)


			latency = get_latency(pathname)
			perrun_latency_list.append(latency)

			print(latency)
		#end_for

		latency_mean, latency_error = mean_margin(perrun_latency_list)
		perthread_latency_mean_list.append(latency_mean)
		perthread_latency_error_list.append(latency_error)

		print(perrun_latency_list)

	#end_for

	print(perthread_latency_mean_list)

	return perthread_latency_mean_list

#end_def


def main():

	print("Hello World")

	threadcount = 6

	'''
	sql_b_list = get_latency_list("/b/sql_b_")
	bdb_b_list = get_latency_list("/b/bdb_b_")
	sql_c_list = get_latency_list("/c/sql_c_")
	bdb_c_list = get_latency_list("/c/bdb_c_")
	'''
	sql_a_list = get_latency_list("SQL_A")
	bdb_a_list = get_latency_list("BDB_A")
	sql_b_list = [] #get_latency_list("SQL_B")
	bdb_b_list = [] #get_latency_list("BDB_B")
	sql_c_list = [] #get_latency_list("SQL_C")
	bdb_c_list = [] #get_latency_list("BDB_C")

	name_list = ["SQL A", "BDB A", "SQL B", "BDB_B", "SQL C", "BDB C"]
	latency_list_list = [sql_a_list, bdb_a_list, sql_b_list, bdb_b_list, sql_c_list, bdb_c_list]

	print(sql_b_list)
	print(bdb_b_list)
	print(sql_c_list)
	print(bdb_c_list)

	fig, ax = plt.subplots()

	select = 1 # 0-5
	selected_list = sql_a_list #latency_list_list[select]

	latency_list = [0, 0, 0, 0, 0, 0]
	throughput_list = [0, 0, 0, 0, 0, 0]
	for i in range(0, threadcount):
		latency_list[i] = selected_list[i] * 1000 / (1800 * (i + 1))
		throughput_list[i] = (1800 * (i + 1)) / (selected_list[i] / (i + 1))
	#end_for

	plt.plot(throughput_list, latency_list, color = "blue", marker = "o", markersize = 12, label = "SQLite (number of threads)")

	#'''
	for i in range(0, threadcount):
		plt.annotate(str(i + 1), xy = (throughput_list[i] + 10, latency_list[i] - 0.5), fontsize = 16)
		#plt.annotate(str(i + 1), xy = (throughput_list[i] + 3, latency_list[i] + .1), fontsize = 16)
	#end_for
	#'''


	selected_list = bdb_a_list

	latency_list = [0, 0, 0, 0, 0, 0]
	throughput_list = [0, 0, 0, 0, 0, 0]
	for i in range(0, threadcount):
		latency_list[i] = selected_list[i] * 1000 / (1800 * (i + 1))
		throughput_list[i] = (1800 * (i + 1)) / (selected_list[i] / (i + 1))
	#end_for

	plt.plot(throughput_list, latency_list, color = "red", marker = "o", markersize = 12, label = "BDB (number of threads)")

	#'''
	for i in range(0, threadcount):
		plt.annotate(str(i + 1), xy = (throughput_list[i] + 20, latency_list[i] - 0.4), fontsize = 16)
		#plt.annotate(str(i + 1), xy = (throughput_list[i] + 3, latency_list[i] + .1), fontsize = 16)
	#end_for
	#'''


	plt.annotate("-----Region of Interest", xy = (350, 1.5), fontsize = 16)

	ax.set_title("YCSB Workload A", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Throughput (queries/s)", fontsize = 20, fontweight = "bold")
	ax.set_ylabel("Average Latency (ms)", fontsize = 20, fontweight = "bold")
	
	print(throughput_list)
	print(latency_list)
	#'''

	'''
	sql_list = [0, 0, 0, 0, 0, 0]
	bdb_list = [0, 0, 0, 0, 0, 0]
	thread_list = [0, 0, 0, 0, 0, 0]

	for i in range(0, threadcount):
		sql_list[i] = sql_c_list[i] * 1000 / (1800 * (i + 1))
		bdb_list[i] = bdb_c_list[i] * 1000 / (1800 * (i + 1))
		thread_list[i] = i + 1
	#end_for

	plt.plot(thread_list, sql_list, color = "blue", marker = "o", markersize = 8, label = "SQLite")
	plt.plot(thread_list, bdb_list, color = "red", marker = "s", markersize = 8, label = "Berkely DB")


	plt.legend(loc = "top left")

	ax.set_title("YCSB Workload C", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Database Threads", fontsize = 20, fontweight = "bold")
	ax.set_ylabel("Average Latency ($ms$)", fontsize = 20, fontweight = "bold")
	'''

	#ax.set_aspect(1/220.0)

	ax.axvspan(200, 400, alpha=.5, color="grey")

	fig15 = plt.gcf()
	fig15.tight_layout()

	plt.legend(loc = "lower right")

	plt.axis([200, 1700, 0, 6.5])
	plt.show()

#end_def

main()


