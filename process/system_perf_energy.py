
import json
import sys
import gzip
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

from matplotlib.lines import Line2D

import math
import statistics


#label_list = ["interactive", "fixed 30%", "fixed 40%", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance", "powersave"]
label_list = ["schedutil", "fixed 30%", "fixed 40%", "fixed 50%", "fixed 60%", "fixed 70%", "fixed 80%", "fixed 90%", "performance", "powersave"]


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

			if ("Start FB" in logline):
				starttime = time
			#end_if

			if ("End FB" in logline):
				endtime = time
			#end_if

			if ("IDLE DATA" in logline):
				idledata_list = logline[79:-1].split(" ")
				print("IDLE")
				print(idledata_list)
				#break
			#end_if

			if ("GFX DATA" in logline):
				graphdata_list = logline[80:-1].split(" ")
				print("GRAPH")
				print(graphdata_list)
				#break
			#end_if

		#end_if

	#end_while

	input_file.close()

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
		idlestart = idlefloat_list[i * 3] = idlefloat_list[i * 3 + 1] + idlefloat_list[i * 3 + 2]
		idleend = idlefloat_list[i * 3 + 24] = idlefloat_list[i * 3 + 25] + idlefloat_list[i * 3 + 26]
		idledelta = idleend - idlestart
		newidle_list.append(idledelta)
		runtime_list.append(endtime - starttime - idledelta)
	#end_for

	print(endtime - starttime)
	print(newidle_list)
	print(runtime_list)

	return endtime - starttime, runtime_list, graphdata_list

#end_def


def get_energy(file_name):

	# file_name = ""

	logline = ""
	logline_list = []
	iteration = 0
	time = 0.0
	amps = 0.0
	volts = 0.0

	amps_total = 0.0
	start = 0.0
	stop = 0.0

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

		iteration += 1
		if (iteration % 1000 == 0):
			#break
			#print("Iteration:  ", iteration)
			pass
		#end_if

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

		if (time <= start):
			continue
		#end_if

		if (time > stop):
			break
		#end_if

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


def bargraph_latency(latency_list, cacherefs_list, cachemisses_list, benchname):

	# latency_list = []
	# cacheref_list = []
	# cachemiss_list = []
	# benchname = ""
	latency = 0.0
	clusterlen = 0
	width = 0
	#color_list = ["b", "r", "g", "y", "orange"]
	#color_list = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
	color_list = []
	color = ""

	label = ""
	ticklabel_list = []

	clusterlen = len(latency_list)
	width = 1
	offset_list = np.arange(0, clusterlen)

	color_list.append("red")
	for i in range(clusterlen - 1):
		color_list.append("blue")
	#end_for

	fig, ax_list = plt.subplots(2, 1)
	#fig, ax_list = plt.subplots(3, 1)
	bottomgraph = len(ax_list) - 1  # Get the number of the bottom graph

	#ticklabel_list.append("")

	for latency, cacherefs, cachemisses, offset, color, label in zip(latency_list, cacherefs_list, cachemisses_list, offset_list, color_list, label_list):

		ax_list[0].bar(offset, latency, width = width, color = color)
		ax_list[1].bar(offset, cacherefs / 1000000, width = width, color = color)
		#ax_list[2].bar(offset, cachemisses / 1000000, width = width, color = color)
		#ax_list[2].bar(offset, cachemisses, width = width, color = color)

		offset_list += width

		ticklabel_list.append(label)

	#end_for

	print(ticklabel_list)
	#'''
	for i in range(len(ax_list)):
		ax_list[i].set_xticks(np.arange(0, offset_list[0]) * 2, False)
	#end_for
	ax_list[0].set_xticklabels([])
	ax_list[1].set_xticklabels([])
	ax_list[bottomgraph].set_xticklabels(ticklabel_list)
	tick_list = ax_list[bottomgraph].get_xticklabels()
	for i in range(len(tick_list)):
		tick_list[i].set_rotation(-45)
		tick_list[i].set_ha("left")
	#end_for
	#'''

	ax_list[0].set_title("SYSTEM Runtime for different CPU governors:  " + benchname, fontsize = 20, fontweight = "bold")
	ax_list[bottomgraph].set_xlabel("Governor", fontsize = 16, fontweight = "bold")
	ax_list[0].set_ylabel("Total runtime ($s$)", fontsize = 16, fontweight = "bold")
	ax_list[1].set_ylabel("Cycle count ($G$)", fontsize = 16, fontweight = "bold")

	print(latency_list)
	print(cacherefs_list)
	print(cachemisses_list)

	plt.show()
	plt.close("all")

	return

#end_def


def bargraph_percore(timetotal_list_list, benchname):

	# benchname = ""
	# timetotal_list_list = []
	color_list = []
	color = ""

	graphcount = len(timetotal_list_list)

	color_list.append("red")
	for i in range(graphcount - 1):
		color_list.append("blue")
	#end_for

	#offset_list = np.arange(0, clusterlen)




	fig, ax_list = plt.subplots(5, 2)

	for i, timetotal_list, label, color in zip(range(graphcount), timetotal_list_list, label_list, color_list):

		offset_list = np.arange(0, len(timetotal_list))

		x = i % 2
		y = int(i / 2)

		'''
		# Normalize to (0,1):
		for j in range(len(timetotal_list)):
			timetotal_list[j] = timetotal_list[j] / 35
		#end_for
		'''

		ax_list[y, x].bar(offset_list, timetotal_list, color = color)
		ax_list[y, x].axis([-.5, 7.5, 0, 35])
		#ax_list[y, x].axis([-.5, 7.5, 0, 1])
		ax_list[y, x].set_title(label, fontsize = 12, fontweight = "bold")

		if (x == 0):
			ax_list[y, x].set_ylabel("Runtime ($s$)", fontsize = 12, fontweight = "bold")
			#ax_list[y, x].set_ylabel("Runtime (%)", fontsize = 12, fontweight = "bold")
		else:
			ax_list[y, x].set_yticklabels([])
		#end_if

		if (i >= 7):
			ax_list[y, x].set_xlabel("Core number", fontsize = 12, fontweight = "bold")
		else:
			ax_list[y, x].set_xticklabels([])
		#end_if

	#end_for

	ax_list[4, 1].set_visible(False)

	#fig.suptitle("Per-core Runtime (Non-Idle) for Facebook (35s App Run) For Different Governors", fontsize = 20, fontweight = "bold")
	fig.suptitle("Per-core Percent Runtime (Non-Idle) for Facebook (35s App Run) For Different Governors", fontsize = 20, fontweight = "bold")

	fig.subplots_adjust(hspace = .4)
	plt.show()

	return

#end_def


def bargraph_sorted_bigsmall(timetotal_list_list, ubertime_list, benchname):

	# benchname = ""
	# timetotal_list_list = []
	# ubertime_list = []
	color_list = []
	color = ""
	timetotal_list = []
	timelittle = 0
	timebig = 0
	subtime = 0
	ubertime = 0.0
	ticklabel_list = []
	graphcount = 0

	graphcount = len(timetotal_list_list)
	#print("Graph count:  %s" % (graphcount))

	# Compute time sums for each of the 4 big and little core clusters:
	for timetotal_list, ubertime, label in zip(timetotal_list_list, ubertime_list, label_list):
		timelittle = 0
		timebig = 0

		#'''
		# Normalize time range to (0,1):
		for j in range(len(timetotal_list)):
			timetotal_list[j] = timetotal_list[j] / (ubertime * 4)
		#end_for
		#'''

		for i in range(0, 4):
			timelittle += timetotal_list[i]
		#end_for
		for i in range(4, 8):
			timebig += timetotal_list[i]
		#end_for
		timetotal_list.append(timelittle)
		timetotal_list.append(timebig)
		timetotal_list.append(label)

		print(label)
		print(timetotal_list)
		print(ubertime)
		print(timelittle)
		print(timebig)

	#end_for

	#print(timetotal_list_list)


	fig, ax_list = plt.subplots(2, 1)

	color_list = ["red", "blue", "green", "orange"]
	offset_list = np.arange(0, graphcount)

	# Sort by total time for little cores:
	timetotal_list_list.sort(key = lambda timetotal_list : timetotal_list[8])

	ticklabel_list = []
	for i, timetotal_list in zip(range(graphcount), timetotal_list_list):
		subtime = 0
		for j in range(0, 4):
			ax_list[0].bar(i, timetotal_list[j], color = color_list[j], bottom = subtime)
			subtime += timetotal_list[j]
		#end_for
		ticklabel_list.append(timetotal_list[10])
	#end_for

	ax_list[0].axis([-.5, graphcount - .5, 0, 1])
	ax_list[0].set_xticks(offset_list)
	ax_list[0].set_xticklabels(ticklabel_list)
	ax_list[0].set_title("Little Cores (Total of 4)", fontsize = 12, fontweight = "bold")
	ax_list[0].set_xlabel("Governor Policy", fontsize = 12, fontweight = "bold")
	ax_list[0].set_ylabel("Busy Ratio (0,1)", fontsize = 12, fontweight = "bold")


	# Sort by total time for little cores:
	timetotal_list_list.sort(key = lambda timetotal_list : timetotal_list[9])

	ticklabel_list = []
	for i, timetotal_list in zip(range(graphcount), timetotal_list_list):
		subtime = 0
		for j in range(0, 4):
			ax_list[1].bar(i, timetotal_list[j + 4], color = color_list[j], bottom = subtime)
			subtime += timetotal_list[j + 4]
		#end_for
		ticklabel_list.append(timetotal_list[10])
	#end_for

	ax_list[1].axis([-.5, graphcount - .5, 0, 1])
	ax_list[1].set_xticks(offset_list)
	ax_list[1].set_xticklabels(ticklabel_list)
	ax_list[1].set_title("Big Cores (Total of 4)", fontsize = 12, fontweight = "bold")
	ax_list[1].set_xlabel("Governor Policy", fontsize = 12, fontweight = "bold")
	ax_list[1].set_ylabel("Busy Ratio (0,1)", fontsize = 12, fontweight = "bold")


	fig.subplots_adjust(hspace = .4)
	fig.suptitle("CPU Cluster Usage (Non-Idle) for Facebook (~22s User Interaction) For Different Governors", fontsize = 20, fontweight = "bold")
	plt.show()

	return


#end_def


def bargraph_graphdata(jank_mean_list, jank_err_list, benchname):

	# jank_mean_list = []
	# jank_err_list = []
	# benchname = ""
	jank_mean = 0.0
	jank_err = 0.0
	barcount = 0
	offset_list = []
	color_list = []
	ticklabel_list = []

	barcount = len(jank_mean_list)
	offset_list = np.arange(0, barcount)
	color_list.append("red")
	for i in range(barcount - 1):
		color_list.append("blue")
	#end_for

	fix, ax = plt.subplots()

	for offset, jank_mean, jank_err, color, label in zip(offset_list, jank_mean_list, jank_err_list, color_list, label_list):
		ax.bar(offset, jank_mean, color = color)
		ax.errorbar(offset, jank_mean, color = "black", yerr = jank_err, elinewidth = 2, capsize = 10, capthick = 2)
		ticklabel_list.append(label)
	#end_for

	ax.axis([-.5, barcount - .5, 0, .10])
	ax.set_xticks(offset_list)
	ax.set_xticklabels(ticklabel_list)
	ax.set_title("Frame Jank Per CPU Policy, ~:24s FB Interaction (10 Runs, 90% Confidence)", fontsize = 12, fontweight = "bold")
	ax.set_xlabel("Governor Policy", fontsize = 12, fontweight = "bold")
	ax.set_ylabel("Frame Jank Proportion (0,1)", fontsize = 12, fontweight = "bold")

	plt.show()

	return

#end_def


def bargraph_energy(energy_mean_list, energy_err_list, benchname):

	# energy_mean_list = []
	# energy_err_list = []
	# benchname = ""
	energy_mean = 0.0
	energy_err = 0.0
	barcount = 0
	offset_list = []
	color_list = []
	ticklabel_list = []

	barcount = len(energy_mean_list)
	offset_list = np.arange(0, barcount)
	color_list.append("red")
	for i in range(barcount - 1):
		color_list.append("blue")
	#end_for

	fig, ax = plt.subplots()
	fig.set_size_inches(8, 4)

	for offset, energy_mean, energy_err, color, label in zip(offset_list, energy_mean_list, energy_err_list, color_list, label_list):
		ax.bar(offset, energy_mean, color = color)
		ax.errorbar(offset, energy_mean, color = "black", yerr = energy_err, elinewidth = 2, capsize = 10, capthick = 2)
		ticklabel_list.append(label)
	#end_for

	#ax.set_xticks(np.arange(0, offset_list[0]) * 2, False)
	ax.set_xticks(offset_list)
	ax.set_xticklabels(ticklabel_list)
	tick_list = ax.get_xticklabels()
	for i in range(len(tick_list)):
		tick_list[i].set_rotation(-45)
		tick_list[i].set_ha("left")
	#end_for
	ax.axis([-.5, barcount - .5, 0, 2000])

	#ax.set_title("Total Energy per CPU Policy, Fixed :40s (~24s Facebook Interaction) (10 Runs, 90% Confidence)", fontsize = 20, fontweight = "bold")
	ax.set_title("Total Energy per CPU Policy, Fixed :30s\n (Single Task Sleeping) (3 Runs, 90% Confidence)", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor Policy", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total Energy ($\mu Ah$)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()
	plt.show()

	#fig.savefig("figure123.pdf", bbox_inches = "tight")

	return

#end_def


def lineplot_energy(energy_mean_list_list, energy_err_list_list):

	# energy_mean_list_list = []
	# energy_err_list_list = []
	energy_mean_list = []
	energy_err_list = []
	energy_mean = 0.0
	energy_err = 0.0
	xcount = 0
	offset = 0
	color_list = []

	xcount = len(energy_mean_list_list[0])
	offset_list = np.arange(0, xcount)
	color_list = ["blue", "red", "green"]
	legendlabel_list = ["thread sleeping", "thread busy ~50%", "thread busy 100%"]

	fig, ax = plt.subplots()
	#fig.set_size_inches(8, 4)

	# Get per-CPU saturation level clusters of runs:
	for energy_mean_list, energy_err_list, color, legendlabel in zip(energy_mean_list_list, energy_err_list_list, color_list, legendlabel_list):

		ax.plot(offset_list, energy_mean_list, color = color, marker = ".", markersize = 12, label = legendlabel)
		ax.errorbar(offset_list, energy_mean_list, yerr = energy_err_list)

	#end_for

	print(label_list)
	print(label_list[:-1])

	ax.set_xticks(offset_list)
	ax.set_xticklabels(label_list[:-1])
	tick_list = ax.get_xticklabels()

	print(len(tick_list))

	for i in range(len(tick_list)):
		tick_list[i].set_rotation(-45)
		tick_list[i].set_ha("left")
	#end_for
	#ax.axis([-.5, xcount - .5, 0, 2000])

	ax.set_title("Total Energy per CPU Policy, :30s Process\n (3 Runs, 90% Confidence)", fontsize = 16, fontweight = "bold")
	ax.set_xlabel("Governor Policy", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total Energy ($\mu Ah$)", fontsize = 16, fontweight = "bold")

	plt.legend(loc = "upper center")
	plt.show()

	fig.savefig("figure123.pdf", bbox_inches = "tight")

	#print(energy_mean_list_list)
	#print(energy_err_list_list)

	return

#end_def


def main():

	path = ""
	filename = ""
	workloads = []
	governors = []
	prefix = ""
	workload = ""
	governor = ""
	benchtime = 0.0
	benchtime_list = []
	runtime_list = []
	runtime_list_list = []
	energy = 0.0
	energy_list = []
	delay = ""
	saturation_list = []
	saturation = ""
	benchname = ""
	interacttime = 0

	timetotal_list = []
	jank_list = []
	jank_mean = 0.0
	jank_mean_list = []
	jank_err = 0.0
	jank_err_list = []
	energy_list = []
	energy_mean = 0.0
	energy_mean_list = []
	energy_mean_list_list = []
	energy_err = 0.0
	energy_err_list = []
	energy_err_list_list = []
	runcount = 0

	path = sys.argv[1]
	#benchname = " Youtube (150s video playback) (with kernel trace)"
	benchname = "Facebook (35s user interaction scrolling)"
	#benchname = "Calculator (10s user interaction keypresses)"
	#benchname = "Temple Run (55s launch and game start)"

	# Get benchtime data:
	#governors = ["interactive_none", "userspace_30", "userspace_40", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none"]
	governors = ["schedutil_none", "userspace_30", "userspace_40", "userspace_50", "userspace_60", "userspace_70", "userspace_80", "userspace_90", "performance_none"]
	prefix = "/micro_SQL_"
	workload = "A"
	delay = "0ms"

	runcount = 1

	#'''
	for governor in governors:
		jank_list = []
		for run in range(runcount):
			filename = path + prefix + workload + "_" + delay + "_" + governor + "_1_" + str(run) + ".gz"
			print(filename)
			benchtime, runtime_list, graphdata_list = process_loglines(filename)
			benchtime_list.append(benchtime)
			runtime_list_list.append(runtime_list)
			jank_list.append(float(graphdata_list[1]) / float(graphdata_list[0]))
		#end_for
		jank_mean, jank_err = mean_margin(jank_list)
		jank_mean_list.append(jank_mean)
		jank_err_list.append(jank_err)
	#end_for

	bargraph_sorted_bigsmall(runtime_list_list, benchtime_list, benchname)
	bargraph_graphdata(jank_mean_list, jank_err_list, benchname)
	#'''

	return

	# Get energy data for several runs each of for different governor policies AND for different CPU saturation levels:

	saturation_list = ["sleep", "mixed", "saturated"]
	prefix = "/monsoon_SQL_"
	workload = "A"
	delay = "0ms"

	#'''
	for saturation in saturation_list:
		energy_mean_list = []
		energy_err_list = []

		for governor in governors:
			energy_list = []
			for run in range(runcount):
				filename = path + "/bench_fixtime_" + saturation + "/" + prefix + workload + "_" + delay + "_" + governor + "_1_" + str(run) + ".csv"
				energy = get_energy(filename)
				print(filename + " : " + str(energy))
				energy_list.append(energy)
			#end_for
			energy_mean, energy_err = mean_margin(energy_list)
			energy_mean_list.append(energy_mean)
			energy_err_list.append(energy_err)
		#end_for

		energy_mean_list_list.append(energy_mean_list)
		energy_err_list_list.append(energy_err_list)

	#end_for
	#'''

	#bargraph_energy(energy_mean_list, energy_err_list, benchname)
	lineplot_energy(energy_mean_list_list, energy_err_list_list)

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

