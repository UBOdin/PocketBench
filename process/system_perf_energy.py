
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

	for i in range(8):
		freq_list.append(300000)
		idle_list.append(-1)
		timestart_list.append(-1)
		timetotal_list.append(0)
		cycle_list.append(0)
	#end_for

	while (True):

		# Keep reading until finished:
		logline = input_file.readline().decode("ascii")

		if (logline == ""):
			print("Never hit endmark")
			print(file_name)
			print(iteration)
			print(logline)
			sys.exit(1)
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
			if (startflag == False):
				if ("SQL_START" in logline):
				#if ("FLAG123 Start App" in logline):
					startflag = True
					trace_list = [iteration, time, "start", cpu, freq]
					trace_list_list.append(trace_list)
					starttime = time
				#end_if
			#'''
			else:
				if ("SQL_END" in logline):
				#if ("FLAG123 End App" in logline):
					trace_list = [iteration, time, "end", cpu, freq]
					trace_list_list.append(trace_list)
					endtime = time
					break
				#end_if
				if ("FLAG123 Start App" in logline):
					startinteracttime = time
				#end_if
				if ("FLAG123 End App" in logline):
					endinteracttime = time
				#end_if
			#end_if
			#'''
		#end_if

		'''
		if ((startflag == True) and (time > starttime + 35.0)):
			print("Exit logline:  " + str(iteration))
			break
		#end_if
		'''

		if (startflag == False):
			continue
		#end_if

		# N.b. for the cpu_frequency event, the cpu field is the CPU# on which the governor
		# runs.  It is *not* necessarily the *target* CPU# for which the speed is set.
		if (eventtype == "cpu_frequency"):

			index = logline.find(" ", datastart)
			if (index == -1):
				print("Invalid speed delimiter")
				sys.exit(1)
			#end_if

			if (logline[index + 1:index + 8] != "cpu_id="):
				print("Invalid run cpu parameter")
				sys.exit(1)
			#end_if
			target_cpu = int(logline[index + 8:-1])  # Fetch the *target* cpu#

			if (logline[datastart:datastart + 6] != "state="):
				print("Invalid speed parameter")
				sys.exit(1)
			#end_if
			freq = int(logline[datastart + 6:index])

			freq_list[target_cpu] = freq

			'''
			if (target_cpu == bench_cpu):
				trace_list = [iteration, time, "speed", target_cpu, freq]
				trace_list_list.append(trace_list)
			#end_if
			'''

		#end_if

		if (eventtype == "cpu_idle"):

			index = logline.find(" ", datastart)
			if (index == -1):
				print("Invalid index delimiter")
				sys.exit(1)
			#end_if

			if (logline[index + 1:index + 8] != "cpu_id="):
				print("Invalid idle cpu parameter")
				sys.exit(1)
			#end_if
			target_cpu = int(logline[index + 8:-1])  # Fetch the *target* cpu#

			if (logline[datastart:datastart + 6] != "state="):
				print("Invalid idle parameter")
				sys.exit(1)
			#end_if
			sleepstate = int(logline[datastart + 6:index])
			if (sleepstate == 4294967295):
				sleepstate = -1
				idletime += time
				idlecount += 1
				offcount += 1

				if (timestart_list[target_cpu] != -1):
					assert timestart_list[target_cpu] != 0
					timedelta = time - timestart_list[target_cpu]
					timestart_list[target_cpu] = 0

					timetotal_list[target_cpu] += timedelta

					cycle_list[target_cpu] += (timedelta * freq_list[target_cpu])

					#print("%d  %f  %f  %d  %f" % (iteration, time, timedelta, freq_list[target_cpu], timedelta * freq_list[target_cpu]))

				#end_if

			else:
				idletime -= time
				oncount += 1

				# Start time delta, *if* cpu is moving off idle
				# (not if it is moving from one non-idle to another non-idle
				if (idle_list[target_cpu] == -1):
					if (timestart_list[target_cpu] != -1):
						assert timestart_list[target_cpu] == 0, "ERROR " + str(iteration) + "\n" + logline
					#end_if
					timestart_list[target_cpu] = time
				#end_if

				#end_if

			#end_if
			idle_list[target_cpu] = sleepstate

			# Test hypo:
			if (cpu != target_cpu):
				print("cpu mismatch")
				sys.exit(1)
			#end_if

			#freq_list[target_cpu] = freq

			'''
			if (target_cpu == bench_cpu):
				trace_list = [iteration, time, "idle", target_cpu, sleepstate]
				trace_list_list.append(trace_list)
			#end_if
			'''

		#end_if

		#end_if

	#end_while

	#print("iterations:  %d" % (iteration))

	# Continue reading tracefile to extract summary GFX data (injected into trace after run):
	while (True):

		# Keep reading until finished:
		logline = input_file.readline().decode("ascii")

		if (logline == ""):
			print("Never hit endmark")
			print(file_name)
			print(iteration)
			print(logline)
			sys.exit(1)
			break
		#end_if

		if ("GFX DATA" in logline):
			graphdata_list = logline[80:-1].split(" ")
			print("GRAPH")
			print(graphdata_list)
			break
		#end_if

	#end_while

	input_file.close()

	print("")
	print("Idle time:  %f" % (idletime))
	print("Idle count:  %d" % (idlecount))
	print(starttime)
	print(endtime)
	print("Latency:  ", endtime - starttime)
	print(offcount)
	print(oncount)

	print(timetotal_list)
	print(cycle_list)

	'''
	for e in trace_list_list:
		print(e)
	#end_for
	'''

	#print("EARLY exit")
	#sys.exit(0)

	timetotal = 0
	cycletotal = 0
	for time in timetotal_list:
		timetotal += time
	#end_for

	if ("schedutil" in file_name):
		for cycle in cycle_list:
			cycletotal += cycle
		#end_for
	#end_if

	if ("userspace" in file_name):
		for i in range(0, 4):
			cycletotal += timetotal_list[i] * freq_list[0]
			cycle_list[i] = timetotal_list[i] * freq_list[0]
		#end_for
		for i in range(4, 8):
			cycletotal += timetotal_list[i] * freq_list[4]
			cycle_list[i] = timetotal_list[i] * freq_list[4]
		#end_for
	#end_if

	if ("performance" in file_name):
		for i in range(0, 4):
			cycletotal += timetotal_list[i] * 1900800
			cycle_list[i] = timetotal_list[i] * 1900800
		#end_for
		for i in range(4, 8):
			cycletotal += timetotal_list[i] * 2457600
			cycle_list[i] = timetotal_list[i] * 2457600
		#end_for
	#end_if

	print("PROCESSED FILE:  " + file_name)
	print("WALLCLOCK TIME:  " + str(endtime - starttime))
	print("TEST RUNNER TIME:  " + str(endinteracttime - startinteracttime))

	#return timetotal, cycletotal, timetotal_list
	return endtime - starttime, endinteracttime - startinteracttime, timetotal_list, graphdata_list


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

	#start = 7.0  # fixed
	#stop = float(iteration - 2) / 5000.0 - 19.0  # Set stop to 19s before end
	start = 15.0
	stop = 45.0
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

	#ax_list[0].axis([-.5, graphcount - .5, 0, 1])
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

	#ax_list[1].axis([-.5, graphcount - .5, 0, 1])
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

	ax.axis([-.5, barcount - .5, 0, .16])
	ax.set_xticks(offset_list)
	ax.set_xticklabels(ticklabel_list)
	ax.set_title("Frame Jank Per CPU Policy, :30s FB Interaction", fontsize = 12, fontweight = "bold")
	ax.set_xlabel("Governor Policy", fontsize = 12, fontweight = "bold")
	ax.set_ylabel("Frame Jank (0,1)", fontsize = 12, fontweight = "bold")

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

	ax.set_title("Net Energy for different CPU governors:  " + benchname, fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Governor", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Net energy ($\mu Ah$)", fontsize = 16, fontweight = "bold")

	plt.tight_layout()
	plt.show()

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
	energy = 0.0
	energy_list = []
	delay = ""
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
	energy_err = 0.0
	energy_err_list = []
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

	runcount = 5

	'''
	for governor in governors:
		jank_list = []
		for run in range(runcount):
			filename = path + prefix + workload + "_" + delay + "_" + governor + "_1_" + str(run) + ".gz"
			benchtime, interacttime, timetotal_list, graphdata_list = process_loglines(filename)
			print(filename + " : " + str(benchtime))
			jank_list.append(float(graphdata_list[1]) / float(graphdata_list[0]))
		#end_for
		jank_mean, jank_err = mean_margin(jank_list)
		jank_mean_list.append(jank_mean)
		jank_err_list.append(jank_err)
	#end_for

	#bargraph_graphdata(jank_list, benchname)
	bargraph_graphdata(jank_mean_list, jank_err_list, benchname)
	'''


	# Get energy data:

	prefix = "/monsoon_SQL_"
	workload = "A"
	delay = "0ms"

	for governor in governors:
		energy_list = []
		for run in range(runcount):
			filename = path + prefix + workload + "_" + delay + "_" + governor + "_1_" + str(run) + ".csv"
			energy = get_energy(filename)
			print(filename + " : " + str(energy))
			energy_list.append(energy)
		#end_for
		energy_mean, energy_err = mean_margin(energy_list)
		energy_mean_list.append(energy_mean)
		energy_err_list.append(energy_err)
	#end_for

	bargraph_energy(energy_mean_list, energy_err_list, benchname)

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

