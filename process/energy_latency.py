
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
	eventtime_list = []
	startfreq_list = []
	ttid = 0.0
	ttfd = 0.0

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

			#if ("friend_flick_end 2" in logline):
			if ("SQL_START" in logline):
				starttime = float(time)
			#end_if

			#if ("friend_flick_start 3" in logline):
			if ("SQL_END" in logline):
				endtime = float(time)
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

			'''
			if ("Cycle data" in logline):
				perfcycles = int(logline.split("Cycle data:  ")[1])
				print("cycles")
			#end_if
			'''
			if ("Macro cycle stats 103" in logline):
				perfcycles_str = logline.split("Macro cycle stats 103:  ")[1][:-1]
				perfcycles_list = perfcycles_str.split(" ")
				perfcycles = 0
				for e in perfcycles_list:
					perfcycles += int(e)
				#end_for
				print("cycles:  " + str(perfcycles))
			#end_if

			if ("CPU FREQ" in logline):
				temp_list = logline.split("CPU FREQ  ")[1].split(" ")
				startfreq_list = [int(temp_list[0]), int(temp_list[1])]
			#end_if

			if ("ActivityTaskManager: Displayed" in logline):
				ttid_str = logline.split(" ")[-1]
				#print(ttid_str)
				temp = ttid_str[1:-3]
				#print(temp)
				if ("s" in temp):
					temp_list = temp.split("s")
					ttid = float(temp_list[0]) + float(temp_list[1]) / 1000.0
				else:
					ttid = float(temp) / 1000.0
				#end_if
				#print(ttid)
			#end_if
			if ("ActivityTaskManager: Fully drawn" in logline):
				ttfd_str = logline.split(" ")[-1]
				#print(ttfd_str)
				temp = ttfd_str[1:-3]
				#print(temp)
				if ("s" in temp):
					temp_list = temp.split("s")
					ttfd = float(temp_list[0]) + float(temp_list[1]) / 1000.0
				else:
					ttfd = float(temp) / 1000.0
				#end_if
				#print(ttfd)
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

	#return endtime - starttime, runtime_list, graphdata_list, perfcycles, eventtime_list, freq_tuple_list_list, startfreq_list
	return endtime - starttime, runtime_list, graphdata_list, perfcycles, eventtime_list, freq_tuple_list_list, startfreq_list, ttid, ttfd

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

	# Reopen file:
	input_file = open(file_name, "r")
	# Skip first line:
	logline = input_file.readline()

	while (True):

		# Keep reading until finished:
		logline = input_file.readline()

		if (logline == ""):
			print("Hit EOF")
			print(file_name)
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


# Plots energy and runtime per policy for microbenchmark
# Tracefiles:  .../20221216/u_curve_vary_time and .../20230102/u_curve_fixed_time
# Summary post-processed data file(s):  graph_u_varylen_multicore.txt and graph_u_fixedlen_multicore.txt
def plot_energy_runtime_micro():

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
	fig.set_size_inches(12, 9)

	#color_list = ["red", "blue", "green", "orange", "brown"]
	color_list = ["0.0", "0.2", "0.4", ".6"]
	linestyle_list = ["solid", "dotted", "dashed", "dashdot"]
	annotate_list = ["default", "30", "40", "50", "60", "70", "80", "90", "100"]
	handle_list = []

	readtraces = False
	#plotfilename = "graph_u_varylen_multicore"
	plotfilename = "graph_u_fixedlen_multicore"
	outputline = ""
	inputline = ""
	inputline_list = []
	if (readtraces == True):
		plotdata_file = open(plotfilename + ".txt", "w")
	else:
		plotdata_file = open(plotfilename + ".txt", "r")
	#end_if

	for x, cputype in zip(range(x_subplots), cputype_list):
		for cpucount, color, linestyle in zip(range(1, 5), color_list, linestyle_list):
			# For baseline workload (0 CPUs), set cputype = 0
			if (cpucount == 0):
				cputype_adj = "00"
			else:
				cputype_adj = cputype
			#end_if
			for governor, annotate, i in zip(governor_list, annotate_list, range(0, 9)):
				if (readtraces == True):
					benchtime_list = []
					cycles_list = []
					energy_list = []
					for run in range(0, 5):
						filename = path + benchtimeprefix + cputype_adj + "-" + str(cpucount) + "_" + governor + "_1_" + str(run) + ".gz"
						print(filename)
						benchtime, _, _, cycles, _, _, _ = process_loglines(filename)
						benchtime_list.append(benchtime)
						cycles_list.append(float(cycles) / (1000 * 1000 * 1000))
						filename = path + energyprefix + cputype_adj + "-" + str(cpucount) + "_" + governor + "_1_" + str(run) + ".csv"
						energy = get_energy(filename, 5.0, benchtime + 10.0)
						energy_list.append(energy)
						print("%f  %f" % (benchtime, energy))
					#end_for
					benchtime_mean, benchtime_err = mean_margin(benchtime_list)
					energy_mean, energy_err = mean_margin(energy_list)

					outputline = str(benchtime_mean) + "," + str(benchtime_err) + "," + str(energy_mean) + "," + str(energy_err) + "\n"
					plotdata_file.write(outputline)
				else:
					inputline = plotdata_file.readline()
					inputline_list = inputline.split(",")
					assert(len(inputline_list) == 4)
					benchtime_mean = float(inputline_list[0])
					benchtime_err = float(inputline_list[1])
					energy_mean = float(inputline_list[2])
					energy_err = float(inputline_list[3])
				#end_if

				#'''
				for y in range(y_subplots):
					if (i == 0):
						ax_list[y][x].scatter(benchtime_mean, energy_mean, s = 70, color = color, marker = "s") #, label = "CPUs:  " + str(cpucount))
					else:
						ax_list[y][x].scatter(benchtime_mean, energy_mean, s = 30, color = color)
					#end_if
					if (i >= 2):
						ax_list[y][x].plot([benchtime_prev, benchtime_mean], [energy_prev, energy_mean], color = color, linestyle = linestyle)
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

			if (x == 0):
				handle_list.append(Line2D([], [], marker = "s", color = color, linestyle = linestyle, label = str(cpucount) + " CPUs"))
			#end_if

		#end_for
	#end_for

	plotdata_file.close()

	handle_list.append(Line2D([], [], marker = "s", markersize = 7, color = "0.0", linewidth = 0, label = "Default"))
	handle_list.append(Line2D([], [], marker = "o", markersize = 5, color = "0.0", linewidth = 0, label = "Fixed Speed"))
	handle_list.append(Line2D([], [], linewidth = 0))
	handle_list.append(Line2D([], [], linewidth = 0))

	ax_list[0][0].tick_params(labelsize = 16)
	ax_list[0][0].axis([0, 70, 0, 3000])
	ax_list[0][0].set_title("Big CPUs", fontsize = 16, fontweight = "bold")
	ax_list[0][0].set_ylabel("Energy ($uAh$)", fontsize = 16, fontweight = "bold")
	ax_list[0][0].legend(handles = handle_list, loc = "upper right", fontsize = 16, ncol = 2)

	ax_list[1][0].tick_params(labelsize = 16)
	ax_list[1][0].set_xlabel("Runtime (s)", fontsize = 16, fontweight = "bold")
	ax_list[1][0].set_ylabel("Energy ($uAh$)", fontsize = 16, fontweight = "bold")

	ax_list[0][1].tick_params(labelsize = 16)
	ax_list[0][1].axis([0, 70, 0, 3000])
	ax_list[0][1].set_title("Little CPUs", fontsize = 16, fontweight = "bold")
	ax_list[0][1].legend(handles = handle_list, loc = "upper right", fontsize = 16, ncol = 2)
	
	ax_list[1][1].tick_params(labelsize = 16)
	ax_list[1][1].set_xlabel("Runtime (s)", fontsize = 16, fontweight = "bold")
	#ax_list[1][1].legend(loc = "upper right", fontsize = 16)

	#fig.suptitle("Runtime and Energy for a Fixed Compute per CPU, Varying CPU policy and CPU Count\n(5 runs) (Variable Energy Measurement)", fontsize = 16, fontweight = "bold")
	fig.suptitle("Runtime and Energy for a Fixed Compute per CPU, Varying CPU policy and CPU Count\n(5 runs) (Fixed 75s Energy Measurement)", fontsize = 16, fontweight = "bold")

	plt.show()
	fig.savefig(plotfilename + ".pdf", bbox_inches = "tight")

	return

#end_def


def make_freqtime_tuple_list_dict(freq_tuple_list, eventtime_list, startfreq, trackidle):

	# freq_tuple_list = []
	# eventtime_list = []
	# startfreq = 0
	# trackidle = False
	prevtime = 0.0
	previdle = 0
	prevfreq = 0
	newtime = 0.0
	newidle = 0
	newfreq = 0
	savefreq = 0
	freqtime_tuple_list_dict = {}
	freqtime_tuple_list = []
	freqtime_tuple = ()

	# Compute a list of (start, stop) times, spent at each freqency, for each CPU:
	prevtime = eventtime_list[0]  # Reset starttime to start of measurement
	freqtime_tuple_list_dict = {}
	previdle = -2  # Reset to uninitialized
	prevfreq = startfreq
	savefreq = prevfreq
	for freq_tuple in freq_tuple_list:
		newtime = freq_tuple[0]

		# If not tracking idle state, short circuit:
		if ((trackidle == False) and (freq_tuple[1] == "idle")):
			previdle = -1
			continue
		#end_if

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

		# Sanity (n.b. very occasionally, tracefiles trip on this -- no idle event before start time):
		if (previdle == -2):
			print("Idle not initialized")
			sys.exit(1)
		#end_if

		# End.  N.b. do not assume current speed (sometimes == start speed, also) is already in dict:
		if (newtime >= eventtime_list[1]):
			freqtime_tuple_list.append((prevfreq, prevtime, eventtime_list[1]))
			if (prevfreq in freqtime_tuple_list_dict):
				freqtime_tuple_list_dict[prevfreq].append((prevtime, eventtime_list[1]))
			else:
				freqtime_tuple_list_dict[prevfreq] = [(prevtime, eventtime_list[1])]
			#end_if
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

		freqtime_tuple_list.append((prevfreq, prevtime, newtime))
		if (prevfreq in freqtime_tuple_list_dict):
			freqtime_tuple_list_dict[prevfreq].append((prevtime, newtime))
		else:
			freqtime_tuple_list_dict[prevfreq] = [(prevtime, newtime)]
		#end_if
		prevtime = newtime
		prevfreq = newfreq
	#end_for

	return freqtime_tuple_list_dict, freqtime_tuple_list

#end_def


def make_time_list_freq_list(freqtime_tuple_list, starttime):

	# freqtime_tuple_list = []
	# starttime = 0.0
	freqtime_tuple = ()
	time_list = []
	freq_list = []
	prevfreq = 0

	prevfreq = freqtime_tuple_list[0][0]
	for freqtime_tuple in freqtime_tuple_list[1:]:
		time_list.append(freqtime_tuple[1] - starttime)
		freq_list.append(prevfreq)
		time_list.append(freqtime_tuple[1] - starttime)
		freq_list.append(freqtime_tuple[0])
		#prevtime = freqtime_tuple[1]
		prevfreq = freqtime_tuple[0]
	#end_for
	time_list.append(freqtime_tuple[2] - starttime)
	freq_list.append(prevfreq)

	return time_list, freq_list

#end_def


def plot_freq_over_time_fb_all_cpus():

	eventtime_list = []
	freqtuple_list_list = []
	freqtuple_list = []
	startfreq_list = []
	starttime = 0.0
	endtime = 0.0

	filename = sys.argv[1]

	_, _, _, _, eventtime_list, freq_tuple_list_list, startfreq_list = process_loglines(filename)

	fig, ax_list_list = plt.subplots(2, 4)

	for cpu in range(0, 8):

		xplot = cpu % 4
		yplot = int(cpu / 4)
		print("%d  %d"  % (xplot, yplot))

		starttime = eventtime_list[0]
		endtime = eventtime_list[1]

		_, freqtime_tuple_list = make_freqtime_tuple_list_dict(freq_tuple_list_list[cpu], eventtime_list, int(startfreq_list[int(cpu / 4)]), True)
		time_list, freq_list = make_time_list_freq_list(freqtime_tuple_list, starttime)

		ax_list_list[yplot][xplot].plot(time_list, freq_list)
		ax_list_list[yplot][xplot].axis([0, endtime - starttime, 0, 2500000])

		ax_list_list[yplot][xplot].set_title("CPU " + str(cpu), fontsize = 16, fontweight = "bold")
		if (xplot == 0):
			ax_list_list[yplot][xplot].set_ylabel("CPU speed (Hz)", fontsize = 16, fontweight = "bold")
		#end_if
		if (yplot == 1):
			ax_list_list[yplot][xplot].set_xlabel("Time during flick (s)", fontsize = 16, fontweight = "bold")
		#end_if

	#end_for

	fig.suptitle("Frequency Over Time, per CPU, for Interim Between Flicks #2 and #3 on FB Friends", fontsize = 16, fontweight = "bold")
	plt.show()

	return

#end_def


# Plots frequency/time graph for 1s FB interaction (showing constantly changing speed)
# Tracefile:  .../20230214/fb_runs_ioblock/micro_normal_schedutil_none_1.gz
def plot_freq_over_time_fb_one_cpu():

	eventtime_list = []
	freqtuple_list_list = []
	freqtuple_list = []
	startfreq_list = []
	starttime = 0.0
	endtime = 0.0
	time_list = []
	freq_list = []

	filename = sys.argv[1]

	_, _, _, _, eventtime_list, freq_tuple_list_list, startfreq_list = process_loglines(filename)

	nplots = 2
	fig, ax_list = plt.subplots(nplots, 1)
	fig.set_size_inches(12, 8)

	targetcpu = 6

	for cpu in range(targetcpu, targetcpu + 1):

		starttime = eventtime_list[0] + 20
		endtime = eventtime_list[0] + 21

		for i in range(nplots):

			_, freqtime_tuple_list = make_freqtime_tuple_list_dict(freq_tuple_list_list[cpu], [starttime, endtime], int(startfreq_list[int(cpu / 4)]), bool(i))
			time_list, freq_list = make_time_list_freq_list(freqtime_tuple_list, starttime)
			ax_list[i].plot(time_list, freq_list)
			ax_list[i].axis([0, endtime - starttime, 0, 2500000])
			ax_list[i].set_ylabel("CPU speed (Hz)", fontsize = 16, fontweight = "bold")
		#end_for

		ax_list[0].set_title("CPU Speed, Ignoring Idling", fontsize = 16, fontweight = "bold")
		ax_list[1].set_title("CPU Speed, Showing Idling", fontsize = 16, fontweight = "bold")
		ax_list[1].set_xlabel("Time (s)", fontsize = 16, fontweight = "bold")

	#end_for

	fig.suptitle("Frequency Over Time, per CPU, for 1s of Interaction on FB Friends", fontsize = 16, fontweight = "bold")
	plt.show()
	fig.savefig("graph_freqtime_flick.pdf", bbox_inches = "tight")

	return

#end_def


# Plots frequency/time graph for microbenchmarks (different delays)
# Tracefile:  .../20230221/microbench_different_delays/*
def plot_freq_over_time_micro():

	eventtime_list = []
	freqtuple_list_list = []
	freqtuple_list = []
	startfreq_list = []
	starttime = 0.0
	endtime = 0.0
	time_list = []
	freq_list = []

	fig, ax_list_list = plt.subplots(2, 2)
	fig.set_size_inches(12, 8)

	targetcpu = 7

	path = sys.argv[1]
	prefix = "/micro_1000-"
	postfix = "-f0-1_schedutil_none_0.gz"
	delay_list = ["0", "5"]

	for yplot, delay in enumerate(delay_list):

		filename = path + prefix + delay + postfix
		print(filename)
		_, _, _, _, eventtime_list, freq_tuple_list_list, startfreq_list = process_loglines(filename)

		for cpu in range(targetcpu, targetcpu + 1):
			starttime = eventtime_list[0]
			endtime = eventtime_list[1]
			for i in range(2):
				xplot = i
				_, freqtime_tuple_list = make_freqtime_tuple_list_dict(freq_tuple_list_list[cpu], [starttime, endtime], int(startfreq_list[int(cpu / 4)]), False)
				time_list, freq_list = make_time_list_freq_list(freqtime_tuple_list, starttime)
				ax_list_list[yplot][xplot].plot(time_list, freq_list)
			#end_for
			ax_list_list[yplot][0].axis([0, 26, 0, 2600000])
		#end_for

	#end_for

	ax_list_list[0][1].axis([0, .5, 0, 2600000])
	ax_list_list[1][1].axis([5, 7, 0, 2600000])
	#ax_list_list[i].set_ylabel("CPU speed (Hz)", fontsize = 16, fontweight = "bold")
	ax_list_list[0][0].set_title("Full Run", fontsize = 16, fontweight = "bold")
	ax_list_list[0][1].set_title("Zoomed Time Slice", fontsize = 16, fontweight = "bold")
	ax_list_list[1][0].set_xlabel("Time (s)", fontsize = 16, fontweight = "bold")
	ax_list_list[1][1].set_xlabel("Time (s)", fontsize = 16, fontweight = "bold")
	ax_list_list[0][0].set_ylabel("CPU speed (Hz)\n(No Delays)", fontsize = 16, fontweight = "bold")
	ax_list_list[1][0].set_ylabel("CPU speed (Hz)\n(1000 5ms Delays)", fontsize = 16, fontweight = "bold")

	fig.suptitle("CPU Speed Over Time, for a Fixed Compute, and Different Delays", fontsize = 16, fontweight = "bold")
	plt.show()
	fig.savefig("graph_freqtime_micro.pdf", bbox_inches = "tight")

	return

#end_def


def plot_time_perfreq_percpu(filename, freqtimetotalcluster_dict_list, perfcycles_list):

	# filename = ""
	# freqtimetotalcluster_dict_list = [{}, {}]
	freqtimetotalcluster_dict = {}
	eventtime_list = []
	freq_tuple_list_list = []
	startfreq_list = []
	timedelta = 0.0
	timetotal = 0.0


	maxspeed_dict = {0:190080, 1:245760}  # 10% CPU freq to norm speeds


	_, _, _, perfcycles, eventtime_list, freq_tuple_list_list, startfreq_list, _, _ = process_loglines(filename)

	perfcycles_list.append(perfcycles)

	#startfreq_list = ["364800", "979200"]  # kludge

	fig, ax_list_list = plt.subplots(2, 4)

	for cpu in range(0, 8):
		#'''
		xplot = cpu % 4
		yplot = int(cpu / 4)
		print("%d  %d"  % (xplot, yplot))
		#'''

		# Construct a per-speed dict of all (start, stop) periods at a speed:
		freqtime_tuple_list_dict, _ = make_freqtime_tuple_list_dict(freq_tuple_list_list[cpu], eventtime_list, int(startfreq_list[int(cpu / 4)]), True)

		# Compute total time spent on a given speed, for each CPU:
		for key in freqtime_tuple_list_dict:
			timetotal = 0.0
			for freqtime_tuple in freqtime_tuple_list_dict[key]:
				timedelta = freqtime_tuple[1] - freqtime_tuple[0]
				timetotal += timedelta
				#print("cpu %d:  %d  %f  %f" % (cpu, key, freqtime_tuple[0], freqtime_tuple[1]))
			#end_for
			#ax_list_list[yplot][xplot].bar(float(key) / 245760, timetotal, color = "blue", width = .1)
			ax_list_list[yplot][xplot].bar(float(key) / maxspeed_dict[yplot], timetotal, color = "blue", width = .1)

			# Add total time for this CPU to appropriate CPU cluster:
			freqtimetotalcluster_dict = freqtimetotalcluster_dict_list[(int(cpu / 4))]
			if (key in freqtimetotalcluster_dict):
				freqtimetotalcluster_dict[key] += timetotal
			else:
				freqtimetotalcluster_dict[key] = timetotal
			#end_if

		#end_for
		#'''
		ax_list_list[yplot][xplot].axis([-0.5, 10.5, 0, 32])
		ax_list_list[yplot][xplot].set_title("CPU " + str(cpu), fontsize = 16, fontweight = "bold")
		if (xplot == 0):
			ax_list_list[yplot][xplot].set_ylabel("Time spent at speed (s)", fontsize = 16, fontweight = "bold")
		#end_if
		if (yplot == 1):
			ax_list_list[yplot][xplot].set_xlabel("CPU frequency (decade)", fontsize = 16, fontweight = "bold")
		#end_if
		#'''

	#end_for

	#'''
	fig.suptitle("Time Spent at a Given Speed, per CPU, for FB (32s script)\n(Showing CPU Idling)", fontsize = 16, fontweight = "bold")
	plt.show()
	plt.close("all")
	#'''

#end_def



# Plots time spent per frequency for fb (default policy)
# Tracefile:  .../20230206/fb_runs/* OR .../20230214/fb_runs_ioblock/*
# (n.b. filename tweak to latter directory -- started omitting threadcount parameter
def plot_time_perspeed_fb():

	filename = ""
	freqtimetotalcluster_dict_list = [{}, {}]
	freqtimetotalcluster_dict = {}
	maxspeed_dict = {}
	perfcycles_list = []

	maxspeed_dict = {0:1900800, 1:2457600}  # 10% CPU freq to norm speeds

	prefix = ""
	#prefix = "/micro_normal_schedutil_none_"
	#prefix = "/micro_normal_schedutil_none_1_"
	#prefix = "/micro_normal_performance_none_1_"
	#prefix = "/micro_normal_userspace_60-60_1_"
	path = sys.argv[1]

	runcount = 9
	for run in range(0, runcount):
		filename = path + prefix + str(run) + ".gz"
		plot_time_perfreq_percpu(filename, freqtimetotalcluster_dict_list, perfcycles_list)
	#end_for
	cpucount = runcount * 4

	perfcycles_mean, _ = mean_margin(perfcycles_list)
	print("Cyclecount mean:  %d" % (perfcycles_mean))

	fig, ax_list_list = plt.subplots(2, 2)
	fig.set_size_inches(12, 8)

	xprop = 100  # CPU speed proportion (out of)
	for xplot in range(0, 2):
		freqtimetotalcluster_dict = freqtimetotalcluster_dict_list[xplot]
		for key in freqtimetotalcluster_dict:
			for yplot in range(0, 2):
				ax_list_list[yplot][xplot].bar((float(key) * xprop) / maxspeed_dict[xplot], freqtimetotalcluster_dict[key] / cpucount, color = "blue", width = .01 * xprop)
				if (yplot == 0):
					ymax = 30
				elif (yplot == 1):
					ymax = 3.5
				#end_if
				ax_list_list[yplot][xplot].axis([-.05 * xprop, 1.05 * xprop, 0, ymax])
			#end_for
		#end_for
	#end_for

	ax_list_list[0][0].set_title("Little core cluster", fontsize = 16, fontweight = "bold")
	ax_list_list[0][1].set_title("Big core cluster", fontsize = 16, fontweight = "bold")
	ax_list_list[0][0].set_ylabel("Full", fontsize = 16, fontweight = "bold")
	ax_list_list[1][0].set_ylabel("Zoom", fontsize = 16, fontweight = "bold")

	fig.suptitle("Average Time Spent at a Given Speed, per Cluster, Default Policy\n(32s FB script) (3 Runs, 4 CPUs per Cluster)", fontsize = 16, fontweight = "bold")
	fig.supxlabel("CPU speed (%)", fontsize = 16, fontweight = "bold")
	fig.supylabel("Average time per CPU at a speed (s)", fontsize = 16, fontweight = "bold")
	fig.subplots_adjust(left = .09, bottom = .07)
	fig.savefig("graph_time_per_freq_fb.pdf", bbox_inches = "tight")

	plt.show()
	plt.close("all")

	for cluster in range(2):
		freqtimetotalcluster_dict = freqtimetotalcluster_dict_list[cluster]
		tt = 0
		for key in freqtimetotalcluster_dict:
			tt += freqtimetotalcluster_dict[key]
		#end_for
		print("total time:  %d" % (tt))
		for key in freqtimetotalcluster_dict:
			print("cluster:  %d  speed:  %s  %f" % (cluster, key, freqtimetotalcluster_dict[key] / tt))
		#end_for
	#end_for

	return

#end_def


# Plots time energy and screendrops per CPU policy (Second plot:  energy and cycles per CPU policy)
# Tracefile:  .../20230214/fb_runs_ioblock/*
# Summary post-processed data file:  graph_energy_jank_fb.txt  
def plot_energy_drops_perpol_fb():

	benchtime = 0
	jank = 0.0
	jank_list = []
	jank_mean = 0.0
	jank_err = 0.0
	energy = 0.0
	energy_list = []
	energy_mean = 0.0
	energy_err = 0.0
	cycles = 0
	cycles_list = []

	governor_list = ["schedutil_none", "userspace_70-70", "userspace_80-80", "ioblock_def-70", "ioblock_def-80", "ioblock_40-def", "ioblock_40-80"]
	ftraceprefix = "/micro_normal_"
	energyprefix = "/monsoon_normal_"
	runcount = 3

	path = sys.argv[1]

	color_list = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive"]
	marker_list = ["o", "1", "2", "v", "^", ">", "<"]
	label_list = ["Default", "Fixed 70", "Fixed 80", "Range 0-70", "Range 0-80", "Range 40-100", "Range 40-80"]
	#linestyle_list = ["solid", "dashdotted", "dashdotdotted", "long dash with offset", "densely dashed", "dashed", "loosely dashed" ]

	nsubplots = 2
	fig, ax_list = plt.subplots(1, nsubplots) #nsubplots, 1)
	fig.set_size_inches(12, 8)
	fig2, ax2_list = plt.subplots(1, nsubplots)
	fig2.set_size_inches(12, 8)

	readtraces = False
	plotfilename = "graph_energy_jank_fb"
	outputline = ""
	inputline = ""
	inputline_list = []
	if (readtraces == True):
		plotdata_file = open(plotfilename + ".txt", "w")
	else:
		plotdata_file = open(plotfilename + ".txt", "r")
	#end_if

	for governor, color, marker in zip(governor_list, color_list, marker_list):

		if (readtraces == True):

			jank_list = []
			energy_list = []
			cycles_list = []
			for run in range(0, 10):
				ftracefilename = path + ftraceprefix + governor + "_" + str(run) + ".gz"
				print(ftracefilename)
				benchtime, _, graphdata_list, cycles, _, _, _ = process_loglines(ftracefilename)
				jank = 100.0 * (float(graphdata_list[1]) / float(graphdata_list[0]))
				jank_list.append(jank)
				cycles_list.append(cycles)
				energyfilename = path + energyprefix + governor + "_" + str(run) + ".csv"
				energy = get_energy(energyfilename, 5.0, 55.0) #benchtime + 15.0)
				energy_list.append(energy)
				print("%f  %f  %f  %f" % (benchtime, jank, cycles, energy))
			#end_for
			jank_mean, jank_err = mean_margin(jank_list)
			energy_mean, energy_err = mean_margin(energy_list)
			cycles_mean, cycles_err = mean_margin(cycles_list)

			outputline = str(jank_mean) + "," + str(jank_err) + "," + str(cycles_mean) + "," + str(cycles_err) + "," + str(energy_mean) + "," + str(energy_err) + "\n"
			plotdata_file.write(outputline)

		else:
			inputline = plotdata_file.readline()
			inputline_list = inputline.split(",")
			assert(len(inputline_list) == 6)
			jank_mean = float(inputline_list[0])
			jank_err = float(inputline_list[1])
			cycles_mean = float(inputline_list[2])
			cycles_err = float(inputline_list[3])
			energy_mean = float(inputline_list[4])
			energy_err = float(inputline_list[5])
		#end_if

		for i in range(nsubplots):
			ax_list[i].scatter(jank_mean, energy_mean, marker = marker, s = 200, color = color)
			ax_list[i].errorbar(jank_mean, energy_mean, xerr = jank_err, yerr = energy_err, color = color)
			ax2_list[i].scatter(cycles_mean, energy_mean, marker = marker, s = 200, color = color)
			ax2_list[i].errorbar(cycles_mean, energy_mean, xerr = cycles_err, yerr = energy_err, color = color)
		#end_for

	#end_for

	plotdata_file.close()

	handle_list = []
	for governor, color, marker, label in zip(governor_list, color_list, marker_list, label_list):
		#handle_list.append(Patch(color = color, label = governor))
		handle_list.append(Line2D([], [], marker = marker, markersize = 15, color = color, label = label, linewidth = 0))
	#end_for

	ax_list[0].set_title("Zero centered", fontsize = 16, fontweight = "bold")
	ax_list[1].set_title("Zoomed", fontsize = 16, fontweight = "bold")
	ax_list[0].axis([0, 8.0, 0, 6000])
	ax_list[1].axis([1.5, 5.0, 4600, 5800])
	ax_list[0].legend(handles = handle_list, loc = "lower right", fontsize = 16)
	ax_list[0].set_ylabel("Energy (mAh)", fontsize = 16, fontweight = "bold")

	fig.suptitle("Energy and Screendrops for Different CPU Policies, for FB (10 runs)", fontsize = 16, fontweight = "bold")
	fig.supxlabel("Screen Drop (%)", fontsize = 16, fontweight = "bold")
	fig.subplots_adjust(top = 0.90, bottom = 0.07)
	fig.savefig(plotfilename + ".pdf", bbox_inches = "tight")

	ax2_list[0].set_title("Zero centered", fontsize = 16, fontweight = "bold")
	ax2_list[1].set_title("Zoomed", fontsize = 16, fontweight = "bold")
	ax2_list[0].axis([0, 80000000000, 0, 6000])
	ax2_list[0].legend(handles = handle_list, loc = "lower left", fontsize = 16)
	ax2_list[0].set_ylabel("Energy (mAh)", fontsize = 16, fontweight = "bold")

	fig2.suptitle("Energy and CPU Cyclecount for Different CPU Policies, for FB (10 runs)", fontsize = 16, fontweight = "bold")
	fig2.supxlabel("Cycles, total", fontsize = 16, fontweight = "bold")
	fig2.subplots_adjust(top = 0.90, bottom = 0.09)
	fig2.savefig("graph_energy_cycles_fb.pdf", bbox_inches = "tight")

	plt.show()

	return

#end_def


def plot_energy_hintperf_spot():

	governor_list = ["normal_schedutil_none", "normal_userspace_70-70", "boost_schedutil_none", "boost_userspace_70-70"]
	ftraceprefix = "/micro_"
	energyprefix = "/monsoon_"

	benchtime = 0
	ttid = 0.0
	ttid_list = []
	ttid_mean = 0.0
	ttid_err = 0.0
	ttfd = 0.0
	ttfd_list = []
	ttfd_mean = 0.0
	ttfd_err = 0.0
	energy = 0.0
	energy_list = []
	energy_mean = 0.0
	energy_err = 0.0

	color_list = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive"]
	marker_list = ["v", "^", ">", "<"]
	label_list = ["Default, no hint", "Fixed 70, no hint", "Default, with hint", "Fixed 70, with hint"]

	path = sys.argv[1]

	fig, ax_list_list = plt.subplots(2, 2)

	for governor, color, marker, label in zip(governor_list, color_list, marker_list, label_list):

		ttid_list = []
		ttfd_list = []
		energy_list = []

		for run in range(5):

			ftracefilename = path + ftraceprefix + governor + "_" + str(run) + ".gz"
			print(ftracefilename)
			benchtime, _, _, _, _, _, _, ttid, ttfd = process_loglines(ftracefilename)
			ttid_list.append(ttid)
			ttfd_list.append(ttfd)

			#'''
			energyfilename = path + energyprefix + governor + "_" + str(run) + ".csv"
			print(energyfilename)
			#energy = get_energy(energyfilename, 5.0, 55.0) #benchtime + 15.0)
			energy = get_energy(energyfilename, 12.0, 12.0 + ttfd + 10.0)
			energy_list.append(energy)
			#'''

			print(ttid)
			print(ttfd)
			print(energy)

		#end_for

		ttid_mean, ttid_err = mean_margin(ttid_list)
		ttfd_mean, ttfd_err = mean_margin(ttfd_list)
		energy_mean, energy_err = mean_margin(energy_list)

		for yplot in range(0, 2):
			ax_list_list[yplot, 0].scatter(ttid_mean, energy_mean, marker = marker, s = 200)
			ax_list_list[yplot, 0].errorbar(ttid_mean, energy_mean, xerr = ttid_err, yerr = energy_err)
			ax_list_list[yplot, 1].scatter(ttfd_mean, energy_mean, marker = marker, s = 200)
			ax_list_list[yplot, 1].errorbar(ttfd_mean, energy_mean, xerr = ttfd_err, yerr = energy_err)
		#end_for

	#end_for

	handle_list = []
	for governor, color, marker, label in zip(governor_list, color_list, marker_list, label_list):
		handle_list.append(Line2D([], [], marker = marker, markersize = 15, color = color, label = label, linewidth = 0))
	#end_for


	ax_list_list[0, 0].tick_params(labelsize = 16)
	ax_list_list[0, 1].tick_params(labelsize = 16)
	ax_list_list[1, 0].tick_params(labelsize = 16)
	ax_list_list[1, 1].tick_params(labelsize = 16)

	ax_list_list[0, 0].axis([0, 2.5, 0, 1200])
	ax_list_list[0, 1].axis([0, 2.5, 0, 1200])

	ax_list_list[0, 0].set_title("Zero Centered", fontsize = 16, fontweight = "bold")
	ax_list_list[0, 1].set_title("Zero Centered", fontsize = 16, fontweight = "bold")
	ax_list_list[1, 0].set_title("Zoomed", fontsize = 16, fontweight = "bold")
	ax_list_list[1, 1].set_title("Zoomed", fontsize = 16, fontweight = "bold")

	ax_list_list[1, 0].set_xlabel("Time to initial display (s)", fontsize = 16, fontweight = "bold")
	ax_list_list[1, 1].set_xlabel("Time to fully drawn (s)", fontsize = 16, fontweight = "bold")
	ax_list_list[0, 0].set_ylabel("Energy (uAh)", fontsize = 16, fontweight = "bold")
	ax_list_list[1, 0].set_ylabel("Energy (uAh)", fontsize = 16, fontweight = "bold")

	ax_list_list[0, 0].legend(handles = handle_list, loc = "lower left", fontsize = 16)
	ax_list_list[0, 1].legend(handles = handle_list, loc = "lower left", fontsize = 16)

	fig.suptitle("Runtime and Energy Use for Spotify App Coldstart (5 runs)", fontsize = 16, fontweight = "bold")

	plt.show()

	return

#end_def


# Plots energy per CPU policy for each of several CPU load levels
# Tracefiles:  .../20220712/bench_fixtime_* (3 subdirectories)
def plot_energy_varying_sleep_micro():

	path = ""
	filename = ""
	prefix = ""
	governor = ""
	governor_list = []
	saturation = ""
	saturation_list = []
	energy = 0.0
	energy_list = []
	energy_mean = 0.0
	energy_err = 0.0
	runcount = 0

	path = sys.argv[1]

	readtraces = False
	plotfilename = "graph_energy_varying_sleep"
	outputline = ""
	inputline = ""
	inputline_list = []
	if (readtraces == True):
		plotdata_file = open(plotfilename + ".txt", "w")
	else:
		plotdata_file = open(plotfilename + ".txt", "r")
	#end_if

	# Get energy data for several runs each of for different governor policies AND for different CPU saturation levels:

	governor_list = ["schedutil_none", "userspace_30", "userspace_40", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none"]
	saturation_list = ["saturated", "mixed", "sleep"]
	ftraceprefix = "/micro_SQL_A_0ms_"
	energyprefix = "/monsoon_SQL_A_0ms_"
	runcount = 3

	offset_list = np.arange(0, len(governor_list))

	fig, ax = plt.subplots()

	color_list = ["0.0", "0.3", "0.6"]
	marker_list = ["o", "s", "D"]
	legendlabel_list = ["thread sleeping", "thread busy ~50%", "thread busy 100%"]
	xticklabel_list = ["default", "fixed 30", "fixed 40", "fixed 50", "fixed 60", "fixed 70", "fixed 80", "fixed 90", "fixed 100"]
	linestyle_list = ["solid", "dotted", "dashed"]
	handle_list = []

	for saturation, color, marker, linestyle, legendlabel in zip(saturation_list, color_list, marker_list, linestyle_list, legendlabel_list):
		energy_mean_list = []
		energy_err_list = []
		for i, (governor, offset) in enumerate(zip(governor_list, offset_list)):

			if (readtraces == True):
				energy_list = []
				for run in range(runcount):
					filename = path + "/bench_fixtime_" + saturation + ftraceprefix + governor + "_1_" + str(run) + ".gz"
					#benchtime, _, _, _, _, _, _, _, _ = process_loglines(filename)
					filename = path + "/bench_fixtime_" + saturation + energyprefix + governor + "_1_" + str(run) + ".csv"
					energy = get_energy(filename, 5.0, 35.0)  # N.b. all runs fixed 20s
					print(filename + " : " + str(energy))
					energy_list.append(energy)
				#end_for
				energy_mean, energy_err = mean_margin(energy_list)
				outputline = str(energy_mean) + "," + str(energy_err) + "\n"
				plotdata_file.write(outputline)
			else:
				inputline = plotdata_file.readline()
				inputline_list = inputline.split(",")
				assert(len(inputline_list) == 2)
				energy_mean = float(inputline_list[0])
				energy_err = float(inputline_list[1])
			#end_if

			ax.scatter(offset, energy_mean, color = color, marker = marker, s = 50)
			ax.errorbar(offset, energy_mean, yerr = energy_err, color = color)
			if (i >= 2):
				ax.plot([offset_prev, offset], [energy_mean_prev, energy_mean], color = color, linestyle = linestyle)
			#end_if
			offset_prev = offset
			energy_mean_prev = energy_mean

		#end_for
		handle_list.append(Line2D([], [], color = color, marker = marker, markersize = 10, linestyle = linestyle, label = legendlabel)) #, linewidth = ))
	#end_for

	plotdata_file.close()

	ax.set_xticks(offset_list)
	ax.set_xticklabels(xticklabel_list)
	tick_list = ax.get_xticklabels()
	for i in range(len(tick_list)):
		tick_list[i].set_rotation(-45)
		tick_list[i].set_ha("left")
	#end_for
	ax.tick_params(labelsize = 16)

	ax.set_title("Total Energy per CPU Policy, :30s Process\n (3 Runs, 90% Confidence)", fontsize = 16, fontweight = "bold")
	ax.set_xlabel("Governor Policy", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total Energy ($\mu Ah$)", fontsize = 16, fontweight = "bold")
	ax.legend(handles = handle_list, loc = "upper center", fontsize = 16)

	plt.show()
	fig.savefig(plotfilename + ".pdf", bbox_inches = "tight")

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
#plot_energy_runtime_micro()
#plot_time_perspeed_fb()
#plot_freq_over_time_fb_one_cpu()
#plot_freq_over_time_all()
#plot_freq_over_time_micro()
#plot_energy_drops_perpol_fb()
#plot_energy_hintperf_spot()
plot_energy_varying_sleep_micro()

