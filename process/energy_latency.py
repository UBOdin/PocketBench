
import json
import sys
import gzip
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

import math
import statistics


#label_list = ["interactive", "fixed 30%", "fixed 40%", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance", "powersave"]
#label_list = ["schedutil", "fixed 30%", "fixed 40%", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance", "powersave"]
#label_list = ["schedutil", "fixed 30%", "fixed 40%", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance"]
label_list = ["schedutil", "fixed 30%", "fixed 40%", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "fixed 100%"]


def mean_margin(data_list):

	n = 0
	mean = 0.0
	stdev = 0.0
	zstar = 1.645 # for 90% -- 1.96 # for 95%
	margin = 0.0

	n = len(data_list)
	# Handle corner case (run size of 1):
	if (n == 1):
		return data_list[0], 0
	#end_if
	mean = statistics.mean(data_list)
	stdev = statistics.stdev(data_list) # stdev() or pstdev()
	margin = zstar * (stdev / math.sqrt(n))

	return mean, margin

#end_def


def process_loglines(file_name):  #, trace_list_list):

	# file_name = ""
	trace_list_list = []

	logline = ""
	iteration = 0
	cpu = 0
	pid = 0
	time = 0.0
	index = 0
	timeend = 0
	eventend = 0
	eventtype = ""
	datastart = 0
	freq = 0
	freq_list = []
	starttime = 0.0
	endtime = 0.0
	startflag = False
	param = ""
	trace_list = []
	target_cpu = 0
	sleepstate = 0
	idletime = 0
	idlecount = 0
	idle_list = []
	timestart_list = []
	timetotal_list = []
	timedelta = 0.0
	cycle_list = []
	offcount = 0
	oncount = 0
	startinteracttime = 0.0
	endinteracttime = 0.0
	graphdata_list = []
	runtime_list = []

	input_file = gzip.open(file_name, "r")

	while (True):

		# Keep reading until finished:
		logline = input_file.readline().decode("ascii")

		if (logline == ""):
			#print(file_name)
			#print(iteration)
			#print(logline)
			#sys.exit(1)
			break
		#end_if

		iteration += 1
		if (iteration % 1000 == 0):
			#print("Iteration:  ", iteration)
			pass
		#end_if

		'''
		if (iteration == 80):
			break
		#end_if
		'''

		# Skip ftrace header lines:
		if (logline[0] == "#"):
			continue
		#end_if

		if (len(logline) < 50):
			continue
		#end_if

		# Calculate length of timefield (n.b. can vary):
		index = logline.find(":", 34)
		if (index == -1):
			print("Missing timeend")
			print(iteration)
			print(logline)
			sys.exit(1)
		#end_if
		timeend = index

		pid = int(logline[17:23])
		cpu = int(logline[24:27])
		time = float(logline[34:timeend])

		# Find end of ftrace event type:
		index = logline.find(":", timeend + 2)
		if (index == -1):
			print("Invalid ftrace event")
			sys.exit(1)
		#end_if
		eventend = index
		eventtype = logline[timeend + 2:eventend]
		datastart = eventend + 2

		'''
		print("Time end:  " + str(timeend))
		print(eventtype)
		print("Func end:  " + str(eventend))
		print(datastart)
		'''

		if (eventtype == "tracing_mark_write"):

			#if ("Start FB" in logline):
			if ("\"SQL_START\"" in logline):
				starttime = time
			#end_if

			#if ("End FB" in logline):
			if ("\"SQL_END\"" in logline):
				endtime = time
			#end_if

			if ("IDLE DATA" in logline):
				idledata_list = logline.split("IDLE DATA  ")[1].split(" ")
				#print("IDLE")
				#print(idledata_list)
				#break
			#end_if

			if ("GFX DATA" in logline):
				graphdata_list = logline.split("GFX DATA:   ")[1].split(" ")
				#print("GRAPH")
				#print(graphdata_list)
				#break
			#end_if

		#end_if

	#end_while

	input_file.close()

	'''
	if (len(idledata_list) != 8 * 3 * 2):
		print("Unexpected length")
		sys.exit(1)
	#end

	idlefloat_list = []
	for e in idledata_list:
		idlefloat_list.append(float(e) / 1000000)
	#end_for

	newidle_list = []
	runtime_list = []
	for i in range(8):
		idlestart = idlefloat_list[i * 3] + idlefloat_list[i * 3 + 1] + idlefloat_list[i * 3 + 2]
		idleend = idlefloat_list[i * 3 + 24] + idlefloat_list[i * 3 + 25] + idlefloat_list[i * 3 + 26]
		idledelta = idleend - idlestart
		newidle_list.append(idledelta)
		runtime_list.append(endtime - starttime - idledelta)
		print("%d  %f  %f  %f  %f  %f  %f" % (i, idlestart, idleend, idledelta, endtime, starttime, endtime - starttime))
	#end_for
	'''

	'''
	print(idledata_list)
	print(idlefloat_list)
	print(runtime_list)

	print("Early exit")
	sys.exit(0)
	'''
	#print(endtime - starttime)
	#print(newidle_list)
	#print(runtime_list)

	return endtime - starttime, runtime_list, graphdata_list

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
	volts = 0.0

	amps_total = 0.0

	'''
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

	# Facebook:  15s - 45s (double check)
	# Temple Run:  15s - 70s
	# microbench (do nothing or sleep for 20s):  5s - 35s

	#start = 7.0  # fixed
	#stop = float(iteration - 2) / 5000.0 - 19.0  # Set stop to 19s before end
	start = 5.0 #08.0 #15.0
	stop = 35.0 #48.0 #45.0
	#start = 8.0
	#stop = start + 150.0
	iteration = 0  # reset counter
	#print("File:  %s  Stop:  %f" % (file_name, stop))
	'''

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

		'''
		iteration += 1
		if (iteration % 1000 == 0):
			#break
			#print("Iteration:  ", iteration)
			pass
		#end_if
		'''

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

		'''
		if (time <= start):
			continue
		#end_if

		if (time > stop):
			break
		#end_if
		'''

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


def bargraph_benchtime(benchtime_list):

	# benchtime_list = []

	benchtime = 0
	barcount = len(benchtime_list)
	offset_list = np.arange(0, barcount)
	offset = 0
	color_list = []
	color = ""

	color_list.append("red")
	for i in range(barcount - 1):
		color_list.append("blue")
	#end_for


	fix, ax = plt.subplots()

	for offset, benchtime, color in zip(offset_list, benchtime_list, color_list):
		ax.bar(offset, benchtime, width = .5, color = color)
	#end_for

	plt.show()

	return

#end_def


def bargraph_energy(energy_list):

	# energy_list = []

	energy = 0
	barcount = len(energy_list)
	offset_list = np.arange(0, barcount)
	offset = 0
	color_list = []
	color = ""

	color_list.append("red")
	for i in range(barcount - 1):
		color_list.append("blue")
	#end_for


	fig, ax = plt.subplots()

	for offset, energy, color in zip(offset_list, energy_list, color_list):
		ax.bar(offset, energy, width = .5, color = color)
	#end_for

	plt.show()

	return

#end_def


def crossplot_benchtime_energy(benchtime_list, energy_list):

	# benchtime_list = []
	# energy_list = []

	benchtime = 0
	benchtime_barcount = len(benchtime_list)
	energy = 0
	energy_barcount = len(energy_list)
	if (benchtime_barcount != energy_barcount):
		print("Unmatched counts")
		sys.exit(1)
	#end_if

	fig, ax = plt.subplots()

	label_list = ["identical frequencies", "oscillating frequencies"]
	color_list = ["red", "blue"]

	for benchtime, energy, label, color in zip(benchtime_list, energy_list, label_list, color_list):
		print("%f  %f" % (benchtime, energy))
		ax.scatter(benchtime, energy, s = 100, color = color, label = label)
	#end_for

	ax.axis([0, 10, 0, 2000])
	ax.tick_params(labelsize = 16)
	ax.set_xlabel("Runtime, seconds", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Energy, $uAh$", fontsize = 16, fontweight = "bold")
	ax.set_title("Runtime and Energy for Fixed Compute,\nVarying CPU Speeds", fontsize = 16, fontweight = "bold")

	plt.legend(loc = "center left", fontsize = 16)
	plt.show()

	return

#end_def


def main():

	benchtime = 0
	benchtime_list = []
	benchtime_mean = 0
	benchtime_err = 0
	benchtime_mean_list = []
	benchtime_err_list = []
	energy = 0
	energy_list = []
	energy_mean = 0
	energy_err = 0
	energy_mean_list = []
	energy_err_list = []
	coretime_list = []
	graphdata_list = []

	#governor_list = ["schedutil_none", "userspace_30", "userspace_40", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none"]
	#governor_list = ["schedutil_none", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none"]
	governor_list = ["steady_userspace_20", "oscillate_userspace_20"]
	runcount = 10
	#benchtimeprefix = "/micro_SQL_A_normal_"
	#energyprefix = "/monsoon_SQL_A_normal_"
	benchtimeprefix = "/micro_SQL_A_"
	energyprefix = "/monsoon_SQL_A_"

	workload = "A"
	#delay = "0ms"
	path = sys.argv[1]


	for governor in governor_list:
		benchtime_list = []
		energy_list = []
		for run in range(20):
			filename = path + benchtimeprefix + governor + "_1_" + str(run) + ".gz"
			benchtime, coretime_list, graphdata_list = process_loglines(filename)
			benchtime_list.append(benchtime)
			filename = path + energyprefix + governor + "_1_" + str(run) + ".csv"
			energy = get_energy(filename, 8.0, 14.0 + benchtime)
			energy_list.append(energy)
			print("%f  %f" % (benchtime, energy))
		#end_for
		benchtime_mean, benchtime_err = mean_margin(benchtime_list)
		benchtime_mean_list.append(benchtime_mean)
		benchtime_err_list.append(benchtime_err)

		energy_mean, energy_err = mean_margin(energy_list)
		energy_mean_list.append(energy_mean)
		energy_err_list.append(energy_err)
	#end_for

	print(benchtime_mean_list)

	bargraph_benchtime(benchtime_mean_list)
	bargraph_energy(energy_mean_list)
	crossplot_benchtime_energy(benchtime_mean_list, energy_mean_list)

	return

#end_def


def quick():

	filename = ""

	filename = sys.argv[1]

	process_loglines(filename)

	return

#end_def


main()
#quick()

