
import json
import sys
import gzip

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches


def get_latency(file_name):

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
	file_list = []
	threads = 6
	latency = 0.0
	latency_list = []

	# Can't just use os.walk or get filelist -- order matters
	for i in range(1, threads + 1):
		file_list.append("threading/" + prefix + str(i) + ".gz") # "threading/c/sql_c_0.gz"
	#end_for

	for filename in file_list:
		print(filename)
		latency = get_latency(filename)
		latency_list.append(latency)
	#end_for

	return latency_list

#end_def


def main():

	print("Hello World")

	threadcount = 6

	sql_b_list = get_latency_list("/b/sql_b_")
	bdb_b_list = get_latency_list("/b/bdb_b_")
	sql_c_list = get_latency_list("/c/sql_c_")
	bdb_c_list = get_latency_list("/c/bdb_c_")

	name_list = ["SQL B", "BDB_B", "SQL C", "BDB C"]
	latency_list_list = [sql_b_list, bdb_b_list, sql_c_list, bdb_c_list]

	print(sql_b_list)
	print(bdb_b_list)
	print(sql_c_list)
	print(bdb_c_list)

	fig, ax = plt.subplots()

	'''
	sql_b_list = [1.4589359999999942, 19.30026399999997, 60.349137999999925, 107.5009839999999, 173.480732, 248.4793239999999]
	bdb_b_list = [1.6219830000000002, 5.911546000000044, 16.59620899999993, 30.439315999999963, 45.828306, 63.59014400000001]
	sql_c_list = [1.053826000000015, 16.93775099999999, 52.724956000000134, 93.53971100000001, 155.4908509999999, 221.12334299999998]
	bdb_c_list = [1.469553000000019, 6.34669800000006, 19.831015999999977, 21.747877000000017, 41.57758899999999, 56.297688999999764]
	'''

	#'''
	select = 0 # 0-3
	selected_list = latency_list_list[select]
	latency_list = [0, 0, 0, 0, 0, 0]
	throughput_list = [0, 0, 0, 0, 0, 0]

	for i in range(0, threadcount):
		latency_list[i] = selected_list[i] * 1000 / (1800 * (i + 1))
		throughput_list[i] = (1800 * (i + 1)) / (selected_list[i] / (i + 1))
	#end_for

	plt.plot(throughput_list, latency_list, color = "blue", marker = "o", markersize = 12, label = "Threadcount")

	#'''
	for i in range(0, threadcount):
		plt.annotate(str(i + 1), xy = (throughput_list[i] + 25, latency_list[i] + .5), fontsize = 16)
		#plt.annotate(str(i + 1), xy = (throughput_list[i] + 3, latency_list[i] + .1), fontsize = 16)
	#end_for
	#'''

	ax.set_title("YCSB " + name_list[select], fontsize = 20, fontweight = "bold")
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

	fig15 = plt.gcf()
	fig15.tight_layout()

	plt.legend(loc = "upper right") #upper center")

	#plt.axis([13800, 23200, 100, 600])
	plt.show()

#end_def

main()


