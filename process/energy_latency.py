
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


def process_loglines(file_name):

	# file_name = ""

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
	freq_tuple_list_list = []
	starttime = 0.0
	endtime = 0.0
	startflag = False
	param = ""
	target_cpu = 0
	speed = 0
	idlestate = 0
	idledata_list = []
	startinteracttime = 0.0
	endinteracttime = 0.0
	graphdata_list = []
	runtime_list = []
	perfcycles = 0
	inbench = False
	eventtime_list = []
	startfreq_list = []

	input_file = gzip.open(file_name, "r")

	for i in range(8):
		freq_tuple_list_list.append([])
	#end_for

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
		if (iteration == 100):
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
			if ("SQL_START" in logline):
				starttime = time
				inbench = True
			#end_if

			#if ("End FB" in logline):
			if ("SQL_END" in logline):
				endtime = time
				inbench = False
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

			if ("Cycle data" in logline):
				perfcycles = int(logline.split("Cycle data:  ")[1])
			#end_if

			if ("CPU FREQ" in logline):
				startfreq_list = logline.split("CPU FREQ  ")[1].split(" ")
			#end_if

		#end_if

		# N.b. for the cpu_frequency event, the cpu field is the CPU# on which the governor
		# runs.  It is *not* necessarily the *target* CPU# for which the speed is set.
		if (eventtype == "cpu_frequency"):
			index = logline.find(" ", datastart)
			if (index == -1):
				print("Invalid speed delimiter")
				sys.exit(1)
			#end_if
			if (logline[datastart:datastart + 6] != "state="):
				print("Invalid speed parameter")
				sys.exit(1)
			#end_if
			speed = int(logline[datastart + 6:index])
			if (logline[index + 1:index + 8] != "cpu_id="):
				print("Invalid speed cpu parameter")
				sys.exit(1)
			#end_if
			target_cpu = int(logline[index + 8:-1])  # Fetch the *target* cpu#
			freq_tuple_list_list[target_cpu].append((time, "freq", speed))
		#end_if

		if (eventtype == "cpu_idle"):
			index = logline.find(" ", datastart)
			if (index == -1):
				print("Invalid idle delimiter")
				sys.exit(1)
			#end_if
			if (logline[datastart:datastart + 6] != "state="):
				print("Invalid idle parameter")
				sys.exit(1)
			#end_if
			idlestate = int(logline[datastart + 6:index])
			if (idlestate == 4294967295):
				idlestate = -1
			#end_if
			#index = logline.find(" ", index, -1)
			if (logline[index + 1:index + 8] != "cpu_id="):
				print("Invalid idle cpu parameter")
				sys.exit(1)
			#end_if
			target_cpu = int(logline[index + 8:-1])  # Fetch the *target* cpu#
			freq_tuple_list_list[target_cpu].append((time, "idle", idlestate))
		#end_if


	#end_while

	input_file.close()

	eventtime_list.append(starttime)
	eventtime_list.append(endtime)

	'''
	if (len(idledata_list) != 8 * 3 * 2):
		print("Unexpected length")
		sys.exit(1)
	#end
	'''

	'''
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

	print(idledata_list)
	print(idlefloat_list)
	print(runtime_list)
	'''
	#print("Early exit")
	#sys.exit(0)
	#'''
	#print(endtime - starttime)
	#print(newidle_list)
	#print(runtime_list)

	return endtime - starttime, runtime_list, graphdata_list, perfcycles, eventtime_list, freq_tuple_list_list, startfreq_list

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
			#print("Hit EOF")
			#print(file_name)
			break
			sys.exit(1)
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
			print(logline)
			print(volts)
			print(file_name)
			#break
			sys.exit(1)
		#end_if

		#'''
		if (time <= start):
			continue
		#end_if

		if (time > stop):
			break
		#end_if
		#'''

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


def crossplot_benchtime_cycles(benchtime_mean_list, benchtime_err_list, cycles_mean_list, cycles_err_list):

	# benchtime_mean_list = []
	# benchtime_err_list = []
	# cycles_mean_list = []
	# cycles_err_list = []

	benchtime = 0
	benchtime_barcount = len(benchtime_mean_list)
	cycles = 0
	cycles_barcount = len(cycles_mean_list)
	if (benchtime_barcount != cycles_barcount):
		print("Unmatched counts")
		sys.exit(1)
	#end_if

	nplots = 2
	fig, ax_list = plt.subplots(nplots, 1)

	#label_list = ["system default", "oscillating speed", "steady mean speed", "low speed", "high speed"]
	label_list = ["schedutil", "70-70", "70-100", "100-100"]
	color_list = ["red", "blue", "green", "orange", "brown"]

	for benchtime_mean, benchtime_err, cycles_mean, cycles_err, label, color in zip(benchtime_mean_list, benchtime_err_list, cycles_mean_list, cycles_err_list, label_list, color_list):
		print("%f  %f" % (benchtime_mean, cycles_mean))
		for i in range(nplots):
			ax_list[i].scatter(benchtime_mean, cycles_mean, s = 100, color = color, label = label)
			ax_list[i].errorbar(benchtime_mean, cycles_mean, xerr = benchtime_err, color = color)
			ax_list[i].errorbar(benchtime_mean, cycles_mean, yerr = cycles_err, color = color)
		#end_for
	#end_for

	#ax_list[0].axis([0, 10, 0, 20])
	ax_list[0].axis([0, 12, 0, 20])
	#ax_list[0].axis([0, 30, 0, 25])
	ax_list[0].tick_params(labelsize = 16)
	#ax_list[0].set_xlabel("Runtime, seconds", fontsize = 16, fontweight = "bold")
	ax_list[0].set_ylabel("Cycles, billions", fontsize = 16, fontweight = "bold")
	ax_list[0].set_title("Runtime and Cycles for Fixed Compute,\n5ms delay (5 runs, 90% confidence)", fontsize = 16, fontweight = "bold")
	ax_list[0].legend(loc = "center left", fontsize = 16)

	#'''
	#ax_list[1].axis([7.2, 7.8, 17.6, 17.8])
	ax_list[1].axis([7.0, 11.0, 17.6, 17.8])
	#ax_list[1].axis([10.0, 30.0, 15.0, 20.0])
	ax_list[1].tick_params(labelsize = 16)
	ax_list[1].set_xlabel("Runtime, seconds", fontsize = 16, fontweight = "bold")
	ax_list[1].set_ylabel("Cycles, billions", fontsize = 16, fontweight = "bold")
	#ax_list[1].set_title("Runtime and Cycles for Fixed Compute,\nVarying CPU Speeds", fontsize = 16, fontweight = "bold")
	#ax_list[1].legend(loc = "center left", fontsize = 16)
	#'''

	plt.show()

	return

#end_def

def crossplot_benchtime_energy(benchtime_mean_list, benchtime_err_list, energy_mean_list, energy_err_list):

	# benchtime_mean_list = []
	# benchtime_err_list = []
	# energy_mean_list = []
	# energy_err_list = []

	benchtime = 0
	benchtime_barcount = len(benchtime_mean_list)
	energy = 0
	energy_barcount = len(energy_mean_list)
	if (benchtime_barcount != energy_barcount):
		print("Unmatched counts")
		sys.exit(1)
	#end_if

	nplots = 2
	fig, ax_list = plt.subplots(1, nplots) #nplots, 1)

	#label_list = ["system default", "oscillating speed", "steady mean speed", "low speed", "high speed"]
	#color_list = ["red", "blue", "green", "orange", "brown"]
	#label_list = ["oscillating speed", "steady mean speed", "low speed", "high speed"]
	label_list = ["3 CPUs 70%", "3 CPUs 23%", "1 CPU 70%", "1 CPU 23%"]
	color_list = ["blue", "green", "orange", "brown"]

	'''
	for i, (benchtime_mean, benchtime_err, energy_mean, energy_err, label, color) in enumerate(zip(benchtime_mean_list, benchtime_err_list, energy_mean_list, energy_err_list, label_list, color_list)):
		print("%f  %f" % (benchtime_mean, energy_mean))
		if (i < 4):
			ax_list[0].scatter(benchtime_mean, energy_mean, s = 100, color = color, label = label)
			ax_list[0].errorbar(benchtime_mean, energy_mean, xerr = benchtime_err, color = color)
			ax_list[0].errorbar(benchtime_mean, energy_mean, yerr = energy_err, color = color)
		else:
			ax_list[1].scatter(benchtime_mean, energy_mean, s = 100, color = color, label = label)
			ax_list[1].errorbar(benchtime_mean, energy_mean, xerr = benchtime_err, color = color)
			ax_list[1].errorbar(benchtime_mean, energy_mean, yerr = energy_err, color = color)
		#end_if
	#end_for
	'''

	for i in range(4):

		color = color_list[i]
		label = label_list[i]

		benchtime_mean = benchtime_mean_list[i]
		benchtime_err = benchtime_err_list[i]
		energy_mean = energy_mean_list[i]
		energy_err = energy_err_list[i]
		ax_list[0].scatter(benchtime_mean, energy_mean, s = 100, color = color, label = label)
		ax_list[0].errorbar(benchtime_mean, energy_mean, xerr = benchtime_err, color = color)
		ax_list[0].errorbar(benchtime_mean, energy_mean, yerr = energy_err, color = color)

		benchtime_mean = benchtime_mean_list[i + 4]
		benchtime_err = benchtime_err_list[i + 4]
		energy_mean = energy_mean_list[i + 4]
		energy_err = energy_err_list[i + 4]
		ax_list[1].scatter(benchtime_mean, energy_mean, s = 100, color = color, label = label)
		ax_list[1].errorbar(benchtime_mean, energy_mean, xerr = benchtime_err, color = color)
		ax_list[1].errorbar(benchtime_mean, energy_mean, yerr = energy_err, color = color)

	#end_for


	#'''
	#ax_list[0].axis([0, 10, 0, 2000])
	ax_list[0].axis([0, 100, 0, 1500])
	ax_list[0].tick_params(labelsize = 16)
	ax_list[0].set_xlabel("Runtime, seconds", fontsize = 16, fontweight = "bold")
	ax_list[0].set_ylabel("Energy, $uAh$", fontsize = 16, fontweight = "bold")
	#ax_list[0].set_title("Runtime and Energy for Fixed Compute,\nVarying CPU Speeds (10 runs, 90% confidence)", fontsize = 16, fontweight = "bold")
	ax_list[0].set_title("Big CPUs", fontsize = 16, fontweight = "bold")
	ax_list[0].legend(loc = "lower right", fontsize = 16)

	#ax_list[1].axis([7.2, 7.8, 1050, 1150])
	ax_list[1].axis([0, 100, 0, 1500])
	ax_list[1].tick_params(labelsize = 16)
	ax_list[1].set_xlabel("Runtime, seconds", fontsize = 16, fontweight = "bold")
	#ax_list[1].set_ylabel("Energy, $uAh$", fontsize = 16, fontweight = "bold")
	#ax_list[1].set_title("Runtime and Energy for Fixed Compute,\nVarying CPU Speeds (10 runs, 90% confidence)", fontsize = 16, fontweight = "bold")
	ax_list[1].set_title("Little CPUs", fontsize = 16, fontweight = "bold")
	ax_list[1].legend(loc = "lower right", fontsize = 16)
	#'''

	fig.suptitle("Runtime and Energy for Fixed Compute,\nVarying CPU Speeds and CPU count (5 runs)", fontsize = 16, fontweight = "bold")
	plt.show()

	return

#end_def


def lineplot_frequency_time(eventtime_list, frequency_list):

	# eventtime_list = []
	# frequency_list = []
	time = 0.0
	freq = 0

	print(len(eventtime_list))
	print(len(frequency_list))

	if (len(eventtime_list) != len(frequency_list) + 2):
		print("Mismatched lengths")
		sys.exit(1)
	#end_if


	fig, ax_list = plt.subplots(2, 1)

	#'''
	steptime_list = []
	stepfreq_list = []
	starttime = eventtime_list[-2]
	prevfreq = frequency_list[0]
	for time, freq in zip(eventtime_list, frequency_list):
		#ax.scatter(time / (1000 * 1000) - starttime, freq / (1000 * 1000), color = "black")
		steptime_list.append(time - starttime)
		stepfreq_list.append(prevfreq / (1000 * 1000))
		steptime_list.append(time - starttime)
		stepfreq_list.append(freq / (1000 * 1000))
		prevfreq = freq
	#end_for
	#ax.scatter(eventtime_list[-1] / (1000 * 1000))
	#'''
	steptime_list.append(eventtime_list[-1] - starttime)
	stepfreq_list.append(prevfreq / (1000 * 1000))

	ax_list[0].plot(steptime_list, stepfreq_list)
	ax_list[0].axis([0, 60.0, 0, 3.0])
	#ax_list[0].axis([0, 30.0, 0, 3.0])
	ax_list[0].tick_params(labelsize = 16)
	#ax_list[0].set_xlabel("Runtime, seconds", fontsize = 16, fontweight = "bold")
	ax_list[0].set_ylabel("Frequency, billions", fontsize = 16, fontweight = "bold")
	ax_list[0].set_title("CPU speed for Fixed Compute (5ms delay)", fontsize = 16, fontweight = "bold")

	ax_list[1].plot(steptime_list, stepfreq_list)
	ax_list[1].axis([0, 0.2, 0, 3.0])
	#ax_list[1].axis([0, 0.2, 0, 3.0])
	ax_list[1].tick_params(labelsize = 16)
	ax_list[1].set_xlabel("Runtime, seconds", fontsize = 16, fontweight = "bold")
	ax_list[1].set_ylabel("Frequency, billions", fontsize = 16, fontweight = "bold")
	#ax_list[1].set_title("Runtime and Energy for Fixed Compute,\nVarying CPU Speeds (10 runs, 90% confidence)", fontsize = 16, fontweight = "bold")

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

	cycles = 0
	cycles_list = []
	cycles_mean = 0
	cycles_err = 0
	cycles_mean_list = []
	cycles_err_list = []

	#governor_list = ["80-3_userspace_70", "e0-3_userspace_23", "80-3_userspace_23", "e0-3_userspace_70"]
	#governor_list = ["e0-3_userspace_70", "e0-3_userspace_23", "80-3_userspace_70", "80-3_userspace_23"]
	#governor_list = ["08-3_userspace_70", "0e-3_userspace_23", "0e-3_userspace_70", "08-3_userspace_23"]
	#governor_list = ["0e-3_userspace_70", "0e-3_userspace_23", "08-3_userspace_70", "08-3_userspace_23"]
	#governor_list = ["e0-3_userspace_70", "e0-3_userspace_23", "80-3_userspace_70", "80-3_userspace_23", "0e-3_userspace_70", "0e-3_userspace_23", "08-3_userspace_70", "08-3_userspace_23"]
	governor_list = ["schedutil_none", "userspace_30-30", "userspace_40-40", "userspace_50-50", "userspace_60-60", "userspace_70-70", "userspace_80-80", "userspace_90-90", "performance_none"]

	benchtimeprefix = "/micro_2000-0-"
	energyprefix = "/monsoon_2000-0-"

	path = sys.argv[1]

	#'''
	for governor in governor_list:
		benchtime_list = []
		cycles_list = []
		energy_list = []
		for run in range(0, 1):
			filename = path + benchtimeprefix + "f0-1_" + governor + "_1_" + str(run) + ".gz"
			print(filename)
			benchtime, coretime_list, graphdata_list, cycles, _, _ = process_loglines(filename)
			benchtime_list.append(benchtime)
			cycles_list.append(float(cycles) / (1000 * 1000 * 1000))
			filename = path + energyprefix + governor + "_1_" + str(run) + ".csv"
			energy = 0 #get_energy(filename, 5.0, benchtime + 15.0)
			energy_list.append(energy)
			print("%f  %f" % (benchtime, energy))
		#end_for
		benchtime_mean, benchtime_err = mean_margin(benchtime_list)
		benchtime_mean_list.append(benchtime_mean)
		benchtime_err_list.append(benchtime_err)

		cycles_mean, cycles_err = mean_margin(cycles_list)
		cycles_mean_list.append(cycles_mean)
		cycles_err_list.append(cycles_err)

		energy_mean, energy_err = mean_margin(energy_list)
		energy_mean_list.append(energy_mean)
		energy_err_list.append(energy_err)
	#end_for

	'''
	print("Early exit")
	sys.exit(0)
	'''

	print(benchtime_mean_list)

	bargraph_benchtime(benchtime_mean_list)
	bargraph_energy(energy_mean_list)
	crossplot_benchtime_energy(benchtime_mean_list, benchtime_err_list, energy_mean_list, energy_err_list)
	#crossplot_benchtime_cycles(benchtime_mean_list, benchtime_err_list, cycles_mean_list, cycles_err_list)
	#'''

	'''
	benchtimeprefix = "/micro_"
	governor = "4000-8_schedutil_none"
	run = 0
	filename = path + benchtimeprefix + governor + "_1_" + str(run) + ".gz"
	_, _, _, _, eventtime_list, frequency_list = process_loglines(filename)

	lineplot_frequency_time(eventtime_list, frequency_list)
	'''

	'''
	benchtimeprefix = "/micro_"
	governor = "_schedutil_none"
	run = 0
	batch_list = ["500", "1000", "2000", "4000"]
	sleep_list = ["0", "1", "2", "4", "8"]

	fig, ax_list = plt.subplots(len(sleep_list), len(batch_list))

	for x, batch in enumerate(batch_list):
		for y, sleep in enumerate(sleep_list):
			filename = path + benchtimeprefix + batch + "-" + sleep + governor + "_1_" + str(run) + ".gz"
			_, _, _, _, eventtime_list, frequency_list = process_loglines(filename)
			print(filename)


			steptime_list = []
			stepfreq_list = []
			starttime = eventtime_list[-2]
			prevfreq = frequency_list[0]
			for time, freq in zip(eventtime_list, frequency_list):
				#ax.scatter(time / (1000 * 1000) - starttime, freq / (1000 * 1000), color = "black")
				steptime_list.append(time - starttime)
				stepfreq_list.append(prevfreq / (1000 * 1000))
				steptime_list.append(time - starttime)
				stepfreq_list.append(freq / (1000 * 1000))
				prevfreq = freq
			#end_for
			#ax.scatter(eventtime_list[-1] / (1000 * 1000))
			steptime_list.append(eventtime_list[-1] - starttime)
			stepfreq_list.append(prevfreq / (1000 * 1000))

			ax_list[y, x].plot(steptime_list, stepfreq_list)
			ax_list[y, x].axis([0, 60.0, 0, 3.0])

		#end_for
	#end_for

	plt.show()
	'''

	return

#end_def


def u_curve():

	benchtime = 0
	benchtime_list = []
	benchtime_mean = 0
	benchtime_err = 0

	cycles = 0
	cycles_list = []
	cycles_mean = 0
	cycles_err = 0

	energy = 0
	energy_list = []
	energy_mean = 0
	energy_err = 0

	benchtimeprefix = "/micro_2000-0-"
	energyprefix = "/monsoon_2000-0-"

	cputype_list = ["f0", "0f"]
	governor_list = ["schedutil_none", "userspace_30-30", "userspace_40-40", "userspace_50-50", "userspace_60-60", "userspace_70-70", "userspace_80-80", "userspace_90-90", "performance_none"]


	path = sys.argv[1]

	x_subplots = 2
	y_subplots = 2
	fig, ax_list = plt.subplots(y_subplots, x_subplots)

	color_list = ["red", "blue", "green", "orange", "brown"]
	annotate_list = ["def", "30", "40", "50", "60", "70", "80", "90", "100"]

	for x, cputype in zip(range(x_subplots), cputype_list):
		for cpucount, color in zip(range(1, 5), color_list):
			# For baseline workload (0 CPUs), set cputype = 0
			if (cpucount == 0):
				cputype_adj = "00"
			else:
				cputype_adj = cputype
			#end_if
			for governor, annotate, i in zip(governor_list, annotate_list, range(0, 9)):
				benchtime_list = []
				cycles_list = []
				energy_list = []
				for run in range(0, 5):
					filename = path + benchtimeprefix + cputype_adj + "-" + str(cpucount) + "_" + governor + "_1_" + str(run) + ".gz"
					print(filename)
					benchtime, coretime_list, graphdata_list, cycles, _, _ = process_loglines(filename)
					benchtime_list.append(benchtime)
					cycles_list.append(float(cycles) / (1000 * 1000 * 1000))
					filename = path + energyprefix + cputype_adj + "-" + str(cpucount) + "_" + governor + "_1_" + str(run) + ".csv"
					energy = get_energy(filename, 5.0, benchtime + 10.0)
					energy_list.append(energy)
					print("%f  %f" % (benchtime, energy))
				#end_for
				benchtime_mean, benchtime_err = mean_margin(benchtime_list)
				energy_mean, energy_err = mean_margin(energy_list)

				#'''
				for y in range(y_subplots):
					if (i == 0):
						ax_list[y][x].scatter(benchtime_mean, energy_mean, s = 50, color = color, marker = "s", label = "CPUs:  " + str(cpucount))
					else:
						ax_list[y][x].scatter(benchtime_mean, energy_mean, s = 50, color = color)
					#end_if
					if (i >= 2):
						ax_list[y][x].plot([benchtime_prev, benchtime_mean], [energy_prev, energy_mean], color = color)
					#end_if
					ax_list[y][x].errorbar(benchtime_mean, energy_mean, xerr = benchtime_err, yerr = energy_err, color = color)
					if (y != 0):
						ax_list[y][x].annotate(annotate, xy = (benchtime_mean + .015, energy_mean + 10), fontsize = 12)
					#end_for
				#end_for
				benchtime_prev = benchtime_mean
				energy_prev = energy_mean
				#'''

			#end_for
		#end_for
	#end_for


	ax_list[0][0].tick_params(labelsize = 16)
	ax_list[0][0].axis([0, 70, 0, 3000])
	ax_list[0][0].set_title("Big CPUs", fontsize = 16, fontweight = "bold")
	ax_list[0][0].set_ylabel("Energy ($uAh$)", fontsize = 16, fontweight = "bold")
	ax_list[0][0].legend(loc = "upper right", fontsize = 16)

	ax_list[1][0].tick_params(labelsize = 16)
	ax_list[1][0].set_xlabel("Runtime (s)", fontsize = 16, fontweight = "bold")
	ax_list[1][0].set_ylabel("Energy ($uAh$)", fontsize = 16, fontweight = "bold")

	ax_list[0][1].tick_params(labelsize = 16)
	ax_list[0][1].axis([0, 70, 0, 3000])
	ax_list[0][1].set_title("Little CPUs", fontsize = 16, fontweight = "bold")
	ax_list[0][1].legend(loc = "upper right", fontsize = 16)
	
	ax_list[1][1].tick_params(labelsize = 16)
	ax_list[1][1].set_xlabel("Runtime (s)", fontsize = 16, fontweight = "bold")
	ax_list[1][1].legend(loc = "upper right", fontsize = 16)
	
	fig.suptitle("Runtime and Energy to Complete a Fixed Compute for Each CPU (no delay), Varying CPU policy and CPU Count\n(5 runs) (Variable energy measurement)", fontsize = 16, fontweight = "bold")
	plt.show()

	return

#end_def


def macro_speed_pertime():

	eventtime_list = []
	freq_tuple_list_list = []
	startfreq_list = []
	startfreqbig = 0
	startfreqlittle = 0
	filename = ""
	prevtime = 0.0
	prevfreq = 0
	newtime = 0.0
	newfreq = 0
	freqtime_tuple_list_dict_list = []
	freqtime_tuple_list_dict = {}
	freqtime_tuple_list = []
	freqtime_tuple = ()

	freqtimetotal_dict = {}
	freqtimetotal_dict_list = []
	timedelta = 0.0
	timetotal = 0.0

	filename = sys.argv[1]

	_, _, _, _, eventtime_list, freq_tuple_list_list, startfreq_list = process_loglines(filename)

	for cpu in range(8):
		freqtimetotal_dict_list.append({})
	#end_for

	maxspeed_dict = {0:190080, 1:245760}  # 10% CPU freq to norm speeds

	fig, ax_list_list = plt.subplots(2, 4)

	for cpu in range(0, 8):
		xplot = cpu % 4
		yplot = int(cpu / 4)
		print("%d  %d"  % (xplot, yplot))

		# Compute a list of (start, stop) times, spent at each freqency, for each CPU:
		prevtime = eventtime_list[0]  # Reset starttime to start of measurement
		freqtime_tuple_list_dict = {}
		previdle = -2  # Reset to uninitialized
		prevfreq = int(startfreq_list[int(cpu / 4)])  # Fetch initial CPU speed
		savefreq = prevfreq
		for freq_tuple in freq_tuple_list_list[cpu]:
			newtime = freq_tuple[0]

			# Until the benchmark start time, just update the CPU speed and idle state but don't save any events:
			if (newtime < eventtime_list[0]):
				if (freq_tuple[1] == "idle"):
					previdle = freq_tuple[2]
					if (previdle == -1):
						prevfreq = savefreq
					elif (previdle >= 0):
						prevfreq = 0
					else:
						print("Unexpected init idle")
						sys.exit(1)
					#end_if
				#end_if
				if (freq_tuple[1] == "freq"):
					savefreq = freq_tuple[2]
					if (previdle == -1):
						prevfreq = savefreq
					#end_if
				#end_if
				continue
			#end_if
			if (previdle == -2):
				print("Idle not initialized")
				sys.exit(1)
			#end_if

			if (newtime >= eventtime_list[1]):
				freqtime_tuple_list_dict[prevfreq].append([prevtime, eventtime_list[1]])
				break
			#end_if

			if (freq_tuple[1] == "idle"):
				newidle = freq_tuple[2]
				if ((newidle >= 0) and (previdle == -1)):
					newfreq = 0
					assert(prevfreq == savefreq)
				elif ((newidle == -1) and (previdle >= 0)):
					newfreq = savefreq
					assert(prevfreq == 0)
				elif ((newidle >= 0) and (previdle >= 0)):
					newfreq = 0
					assert(prevfreq == 0)
				else:
					print("Unexpected idle")
					sys.exit(1)
				#end_if
				previdle = newidle
			#end_if

			if (freq_tuple[1] == "freq"):
				savefreq = freq_tuple[2]
				if (previdle == -1):
					newfreq = savefreq
				#end_if
			#end_if

			if (prevfreq in freqtime_tuple_list_dict):
				freqtime_tuple_list_dict[prevfreq].append((prevtime, newtime))
			else:
				freqtime_tuple_list_dict[prevfreq] = [(prevtime, newtime)]
			#end_if

			prevtime = newtime
			prevfreq = newfreq
		#end_for
		freqtime_tuple_list_dict_list.append(freqtime_tuple_list_dict)

		# Compute total time spent on a given speed, for each CPU:
		freqtimetotal_dict = {}
		tt = 0.0

		for key in freqtime_tuple_list_dict:
			timetotal = 0.0
			for freqtime_tuple in freqtime_tuple_list_dict[key]:
				timedelta = freqtime_tuple[1] - freqtime_tuple[0]
				timetotal += timedelta
				#print("cpu %d:  %d  %f  %f" % (cpu, key, freqtime_tuple[0], freqtime_tuple[1]))
			#end_for

			print("cpu %d:  %d  %f" % (cpu, key, timetotal))

			freqtimetotal_dict[key] = timetotal
			tt += timetotal
			#ax_list_list[yplot][xplot].bar(float(key) / 245760, timetotal, color = "blue", width = .1)
			ax_list_list[yplot][xplot].bar(float(key) / maxspeed_dict[yplot], timetotal, color = "blue", width = .1)

		#end_for

		freqtimetotal_dict_list[cpu] = freqtimetotal_dict
		print("time total:  %d  %f" % (cpu, tt))

		ax_list_list[yplot][xplot].axis([-0.5, 10.5, 0, 32])
		ax_list_list[yplot][xplot].set_title("CPU " + str(cpu), fontsize = 16, fontweight = "bold")
		if (xplot == 0):
			ax_list_list[yplot][xplot].set_ylabel("Time spent at speed (s)", fontsize = 16, fontweight = "bold")
		#end_if
		if (yplot == 1):
			ax_list_list[yplot][xplot].set_xlabel("CPU frequency (decade)", fontsize = 16, fontweight = "bold")
		#end_if

	#end_for
	
	fig.suptitle("Time Spent at a Given Speed, per CPU, for FB (32s script)\n(Showing CPU Idling)", fontsize = 16, fontweight = "bold")
	plt.show()
	plt.close("all")

	freqtimetotallittle_dict = {}
	freqtimetotalbig_dict = {}
	# Compute total time spent on a given speed, for each cluster:
	for cpu in range(0, 4):
		freqtimetotal_dict = freqtimetotal_dict_list[cpu]
		for key in freqtimetotal_dict:
			freqtimetotal = freqtimetotal_dict[key]
			if (key in freqtimetotallittle_dict):
				freqtimetotallittle_dict[key] += freqtimetotal
			else:
				freqtimetotallittle_dict[key] = freqtimetotal
			#end_if
		#end_for
	#end_for
	for cpu in range(4, 8):
		freqtimetotal_dict = freqtimetotal_dict_list[cpu]
		for key in freqtimetotal_dict:
			freqtimetotal = freqtimetotal_dict[key]
			if (key in freqtimetotalbig_dict):
				freqtimetotalbig_dict[key] += freqtimetotal
			else:
				freqtimetotalbig_dict[key] = freqtimetotal
			#end_if
		#end_for
	#end_for

	fig, ax = plt.subplots()

	for key in freqtimetotallittle_dict:
		ax.bar(float(key) / maxspeed_dict[0], freqtimetotallittle_dict[key], color = "blue", width = .1)
	#end_for

	plt.show()

	return

#end_def


def quick():

	filename = ""

	filename = sys.argv[1]

	process_loglines(filename)

	return

#end_def


#main()
#quick()
#u_curve()
macro_speed_pertime()

