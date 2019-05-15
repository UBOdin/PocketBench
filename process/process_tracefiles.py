
import json
import sys
import gzip
import json

import matplotlib.pyplot as plt
import numpy as np

import math
import statistics


nulltimes_dict = {500000: [1564.7242294777395, 1595.1765554428189, 1669.7928495702693, 1620.5320003296044, 1715.461473335889], 550000: [1600.4479020167478, 1627.64847990463, 1704.3507143738918, 1653.7938166646395, 1749.2191938004794], 600000: [1639.9539755138485, 1667.4842010715363, 1749.0088937080448, 1692.08775879662, 1790.4702978713299], 650000: [1671.8970167900595, 1716.8904899293607, 1798.9363764917587, 1742.1218750642067, 1841.4443802031392], 700000: [1725.4139562390337, 0.0, 0.0, 1779.0527080523582, 1876.4501131665938], 750000: [1760.8833322213964, 0.0, 0.0, 0.0, 0.0], 800000: [1797.0874112901806, 0.0, 0.0, 0.0, 0.0], 850000: [1823.7450706706704, 0.0, 0.0, 0.0, 0.0], 900000: [1846.1918920324952, 0.0, 0.0, 0.0, 0.0], 950000: [1860.5999930220562, 0.0, 0.0, 0.0, 0.0], 1000000: [0.0, 0.0, 0.0, 0.0, 0.0]}


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


def get_latency(input_filename):

	input_file = "" # File object
	logline = ""
	iteration = -1
	starttime = 0.0
	endtime = 0.0
	latency = 0.0

	input_file = gzip.open(input_filename)

	while (True):

		iteration += 1
		if (iteration % 1000 == 0):
			#break
			#print("Iteration:  ", iteration)
			pass
		#end_if

		#logline = str(input_file.readline())[2:-1]
		logline = input_file.readline().decode("ascii")

		if (logline == ""):
			break
		#end_if

		if ("_START" in logline):
			starttime += float(logline[33:46])
		#end_if

		if ("_END" in logline):
			endtime += float(logline[33:46])
		#end_if

	#end_while

	input_file.close()

	latency = endtime - starttime

	'''
	print("iterations:  %d" % (iteration))
	print(starttime)
	print(endtime)
	print("Latency:  ", latency)
	'''

	return latency

#end_def


def get_energy(input_filename, workload):

	filename = ""
	input_file = "" # file obj
	input_line = ""
	iteration = -1
	input_list = []
	amps = 0.0
	volts = 0.0
	watts = 0.0
	amps_total = 0.0
	watts_total = 0.0
	null_total = 0.0
	amps_net = 0.0
	start_line = 0
	end_line = 0

	input_file = gzip.open(input_filename, "r")
	input_file.readline() # Skip drop count

	start_line = 5000 * 10
	end_line = start_line + 5000

	while (True):

		iteration += 1

		#input_line = str(input_file.readline())[2:-1]
		input_line = input_file.readline().decode("ascii")

		if (input_line == ""):
			break
		#end_if

		if (iteration < start_line):
			continue
		#end_if

		'''
		if (iteration == end_line):
			break
		#end_if
		'''

		input_list = input_line.split("\t")

		amps = float(input_list[1])
		volts = float(input_list[2])

		watts = amps * volts
		amps_total += amps
		watts_total += watts

	#end_while

	input_file.close()

	amps_total = amps_total * 1000.0 / (5000.0 * 3600.0)
	watts_total = watts_total * 1000.0 / (5000.0 * 3600.0)

	null_total = (nulltimes_dict[iteration])[workload]

	#'''
	print("Current:  " + str(amps_total))
	print("Energy:  " + str(watts_total))

	print("Null:  " + str(null_total))

	print("Net:  " + str(amps_total - null_total))

	#'''

	return amps_total - null_total

#end_def


def get_mean_error(db_workload_delay):

	latency_prefix = "YCSB_"
	path = ""
	pathname = ""
	latency = 0.0
	latency_list = []
	latency_mean = 0.0
	latency_error = 0.0
	latency_mean_list = []
	latency_error_list = []

	energy_prefix = "monsoon_"
	energy = 0.0
	energy_list = []
	energy_mean = 0.0
	energy_error = 0.0
	energy_mean_list = []
	energy_error_list = []

	governor_list = ["userspace_300000", "userspace_1267200", "userspace_2649600", "interactive_none", "ondemand_none"]

	#directory_list = ["../monsoon_01", "../monsoon_02", "../monsoon_03"]
	#directory_list = ["../monsoon_04", "../monsoon_05", "../monsoon_06"]
	#directory_list = ["../monsoon_01", "../monsoon_02", "../monsoon_03", "../monsoon_04", "../monsoon_05", "../monsoon_06"]
	directory_list = ["../monsoon_11", "../monsoon_12", "../monsoon_13"]
	
	for i in range(len(governor_list)):

		#'''
		latency_list = []
		for directory_prefix in directory_list:
			pathname = directory_prefix + "/" + latency_prefix + db_workload_delay + "_" + governor_list[i] + ".gz"
			latency = get_latency(pathname)
			print(pathname + " " + str(latency))
			latency_list.append(latency)
		#end_for

		latency_mean, latency_error = mean_margin(latency_list)
		latency_mean_list.append(latency_mean * 1000)
		latency_error_list.append(latency_error * 1000)

		print(latency_list)
		print("latency mean:  " + str(latency_mean * 1000))
		print("latency error:  " + str(latency_error * 1000))
		print("latency pct:  " + str(latency_error / latency_mean))
		#'''

		'''
		energy_list = []
		for directory_prefix in directory_list:
			pathname = directory_prefix + "/" + energy_prefix + db_workload_delay + "_" + governor_list[i] + ".gz"
			energy = get_energy(pathname, i)
			print(pathname + " " + str(energy))
			energy_list.append(energy)
		#end_for

		energy_mean, energy_error = mean_margin(energy_list)
		energy_mean_list.append(energy_mean)
		energy_error_list.append(energy_error)

		print(energy_list)
		print("energy mean:  " + str(energy_mean))
		print("energy error:  " + str(energy_error))
		'''

	#end_for

	return latency_mean_list, latency_error_list, energy_mean_list, energy_error_list

#end_def


def main():

	print("Hello World")

	db_workload_delay = ""
	param_list = []
	latency_mean_list = []
	latency_error_list = []
	energy_mean_list = []
	energy_error_list = []
	workload = "" # A, B, C, E
	delay = ""
	delay_dict = {"0ms":"Saturated", "log":"Unsaturated"}
	marker_list = ['o', 's', 'd', '>', '<']
	marker_label_list = ["Powersave", "Userspace", "Performance", "Interactive", "Ondemand"]
	smallsize = 12 # 8
	largesize = 12

	db_workload_delay = sys.argv[1] # "SQL_C_0ms"
	param_list = db_workload_delay.split("_")
	workload = param_list[1]
	delay = delay_dict[param_list[2]]

	latency_mean_list, latency_error_list, energy_mean_list, energy_error_list = get_mean_error(db_workload_delay)

	print(latency_mean_list)
	print(latency_error_list)
	print(energy_mean_list)
	print(energy_error_list)

	sys.exit(4)

	fig, ax = plt.subplots()

	for i in range(0, 5):

		plt.errorbar(latency_mean_list[i], energy_mean_list[i], xerr = latency_error_list[i], yerr = energy_error_list[i], marker = marker_list[i], color= "black" , markersize = smallsize, label = marker_label_list[i])
		#plt.errorbar(plug_mean_list[i], energy_mean_list[i], xerr = plug_error_list[i], yerr = energy_error_list[i], marker = marker_list[i], color = "orange", markersize = smallsize)

		'''
		print(energy_mean_list[i])
		print(energy_error_list[i])
		print("energy")
		print(marker_label_list[i])
		print(100.0 * energy_error_list[i] / energy_mean_list[i])

		print(latency_mean_list[i])
		print(latency_error_list[i])
		print("latency")
		print(marker_label_list[i])
		print(100.0 * latency_error_list[i] / latency_mean_list[i])
		'''
		energy_error = 100.0 * energy_error_list[i] / energy_mean_list[i]
		latency_error = 100.0 * latency_error_list[i] / latency_mean_list[i]
		print("%s & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f \\\\" % (marker_label_list[i], latency_mean_list[i], latency_error_list[i], latency_error, energy_mean_list[i], energy_error_list[i], energy_error))

	#end_for

	#plt.legend(numpoints=1)
	plt.legend(loc = "upper left", numpoints = 1, handlelength = .8)

	ax.set_title("Workload " + workload + " -- " + delay + " CPU",fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Workload Latency ($ms$)", fontsize = 20, fontweight = "bold")
	ax.set_ylabel("Net Energy Cost ($\mu Ah$)", fontsize = 20, fontweight = "bold")

	#ax.set_aspect(1/220.0)

	fig15 = plt.gcf()
	fig15.tight_layout()

	#plt.legend(loc = "center right") #upper center")

	print("DONT FORGET SAT / UNSAT delay setting for label")

	plt.show()

#

#end_def


def other():

	file = ""
	latency = 0.0
	latency_list = []
	latency_mean = 0.0
	latency_error = 0.0

	'''
	file_list = ["YCSB_SQL_A_0ms_userspace_1267200_20190310193504.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190310194122.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190310194711.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190310195259.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190310200506.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190310202233.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190310202820.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190310203407.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190310203958.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190310204546.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190310205135.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190310205723.gz"]
	'''

	file_list = ["YCSB_SQL_A_0ms_userspace_1267200_20190505013253.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190505013744.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190505014255.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190505014754.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190505015307.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190505015816.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190505020329.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190505021838.gz", \
		"YCSB_SQL_A_0ms_userspace_1267200_20190505025250.gz", "YCSB_SQL_A_0ms_userspace_1267200_20190505025750.gz"]

	#file_list = range(1, 7)

	for file in file_list:

		#pathname = "../repeat_batt/" + file
		pathname = "../logs/" + file
		#pathname = "../variance/A_0ms_12672_plug_" + str(file) + ".gz"

		latency = get_latency(pathname)
		print(pathname + " " + str(latency))
	
		latency_list.append(latency)

	#end_for

	latency_mean, latency_error = mean_margin(latency_list)

	print(latency_mean, latency_error)

	print(latency_list)
	print("latency mean:  " + str(latency_mean * 1000))
	print("latency error:  " + str(latency_error * 1000))
	print("latency pct:  " + str(latency_error / latency_mean))
	
#end_def


other() #main()


