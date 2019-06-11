
import sys
import gzip
import os
import matplotlib.pyplot as plt
import numpy as np

def get_latency(file_name):

	input_file = "" # file handle
	logline = ""
	iteration = 0
	starttime = 0.0
	endtime = 0.0
	track = False
	pid = ""
	core = 0
	time = 0.0
	oncore_list = [False, False, False, False]
	coretime_list = [0.0, 0.0, 0.0, 0.0]
	coretime_total = 0.0

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

			pid = logline[17:21]

			core = int(logline[24:27]) # 0-3
			time = float(logline[33:46])

			starttime += time
			track = True

			oncore_list[core] = True
			coretime_list[core] -= time

		#end_if

		if ("_END" in logline):

			core = int(logline[24:27]) # 0-3
			time = float(logline[33:46])

			endtime += time
			track = False

			oncore_list[core] = False
			coretime_list[core] += time

			break

		#end_if

		#'''
		if (track == True):

			if (logline[48:60] == "sched_switch"):

				core = int(logline[24:27]) # 0-3
				time = float(logline[33:46])

				if ("prev_pid=" + pid in logline):
					#print("swapout")
					if (oncore_list[core] == False):
						print("Swapout on already offcore")
						sys.exit(1)
					#end_if
					oncore_list[core] = False
					coretime_list[core] += time
				#end_if

				if ("next_pid=" + pid in logline):
					#print("swapin")
					if (oncore_list[core] == True):
						print("Swapin on already oncore_list")
						sys.exit(1)
					#end_if
					oncore_list[core] = True
					coretime_list[core] -= time
				#end_if

			#end_if

		#end_if
		#'''

	#end_while

	input_file.close()

	for e in coretime_list:
		coretime_total += e
	#end_for

	print("File:  %s" % file_name)

	'''
	print("iterations:  %d" % (iteration))

	print(starttime)
	print(endtime)
	print("Latency:  ", endtime - starttime)

	print(oncore_list)
	print(coretime_list)

	print("Oncore time:  %f" % coretime_total)
	print("Offcore time:  %f" % (endtime - starttime - coretime_total))
	'''

	return (endtime - starttime) * 1000, coretime_total * 1000

#end_def


def main():

	print("Hello World")

	filename = ""
	prefix = "tracefiles/nexus6_aosp601/no_delaytags/real_vs_clean/YCSB_SQL_C_"
	latency = 0.0
	coretime = 0.0
	time_list = ["0ms", "1ms", "log"]
	width = 0.25

	fig, ax = plt.subplots()

	suffix = "_userspace_2649600_1.gz"  # for cleanroom (pinned) runs
	offset = 0.25

	for time in time_list:
		filename = prefix + time + suffix
		latency, coretime = get_latency(filename)
		ax.bar(offset, latency, width = width, color = "blue", edgecolor = "black", label = "Unscheduled Time")
		ax.bar(offset, coretime, width = width, color = "red", edgecolor = "black", label = "CPU Time")
		offset += .25
	#end_for

	suffix = "_interactive_none_1.gz"  # for realworld (unpinned) runs
	offset = 1.25

	for time in time_list:
		filename = prefix + time + suffix
		latency, coretime = get_latency(filename)
		ax.bar(offset, latency, width = width, color = "blue", edgecolor = "black")
		ax.bar(offset, coretime, width = width, color = "red", edgecolor = "black")
		offset += .25
	#end_for

	ax.set_title("YCSB Workload C", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Query Delay Time and CPU State", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Total Latency ($ms$)", fontsize = 20, fontweight = "bold")

	plt.xticks(fontsize = 16)
	plt.yticks(fontsize = 16)

	ax.set_xticks(np.arange(0.0625, 0.0625 + 2.125, 0.125))

	x_labels = ["", "0ms", "", "1ms", "", "lognormal", "", "", "", "0ms", "", "1ms", "", "lognormal"]
	x_labels[0] = "\n\n      CPU Pinned"
	x_labels[8] = "\n\n     CPU Unpinned"
	ax.set_xticklabels(x_labels)

	xtick_list = ax.get_xticklabels()
	for e in xtick_list:
		e.set_rotation(-45)
		e.set_ha("left")
	#end_for
	xtick_list[0].set_rotation(0)
	xtick_list[8].set_rotation(0)

	plt.tick_params(bottom = False)

	plt.legend(loc = "upper left")

	fig15 = plt.gcf()
	fig15.tight_layout()

	plt.show()

#end_def


main()


