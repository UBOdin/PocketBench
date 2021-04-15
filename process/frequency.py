
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
	core_frequency = [0, 0, 0, 0]
	benchmark_core = [False, False, False, False]
	timestamp_list = []
	frequency_list = []

	prev_frequency = 0
	prev_iteration = 0

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

			benchmark_core[core] = True

			timestamp_list.append(time)
			frequency_list.append(core_frequency[core])

			prev_frequency = core_frequency[core]
			prev_iteration = iteration

		#end_if

		if ("_END" in logline):

			core = int(logline[24:27]) # 0-3
			time = float(logline[33:46])

			endtime += time
			track = False

			oncore_list[core] = False
			coretime_list[core] += time

			timestamp_list.append(time)
			frequency_list.append(core_frequency[core])

			break

		#end_if

		if (logline[48:62] == "cpu_frequency:"):

			core = int(logline[24:27]) # 0-3
			time = float(logline[33:46])
			fragment = logline[69:]
			frequency = int(fragment.split(" ")[0])

			if (benchmark_core[core] == True):

				if (prev_frequency != core_frequency[core]):
					print("frequency mismatch (core migration) on lines %d and %d" % (iteration, prev_iteration))
				#end_if

				# Record old and new frequencies (delta is 1ms):
				timestamp_list.append(time)
				frequency_list.append(core_frequency[core])
				timestamp_list.append(time)
				frequency_list.append(frequency)

				prev_frequency = frequency
				prev_iteration = iteration

			#end_if
	
			core_frequency[core] = frequency

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

					timestamp_list.append(time)
					frequency_list.append(core_frequency[core])

				#end_if

				if ("next_pid=" + pid in logline):
					#print("swapin")
					if (oncore_list[core] == True):
						print("Swapin on already oncore_list")
						sys.exit(1)
					#end_if
					oncore_list[core] = True
					coretime_list[core] -= time

					# We may have migrated to another core.  Clear status:
					for i in range(0, 4):
						benchmark_core[i] = False
					#end_for
					benchmark_core[core] = True
					timestamp_list.append(time)
					frequency_list.append(core_frequency[core])

				#end_if

			#end_if

		#end_if
		#'''

	#end_while

	input_file.close()

	print("File:  %s" % file_name)

	'''
	print(timestamp_list)
	print(frequency_list)
	'''

	#return (endtime - starttime) * 1000, coretime_total * 1000

	return (timestamp_list, frequency_list)

#end_def


def main():

	print("Hello World")

	filename = ""
	subname = []
	workload = ""
	delay = ""
	timestamp_list = []
	frequency_list = []
	base_time = 0.0
	max_time = 0.0

	filename = sys.argv[1]
	timestamp_list, frequency_list = get_latency(filename)

	subname_list = filename.split("YCSB_")[1].split("_")
	workload = subname_list[1]
	delay = subname_list[2]

	base_time = timestamp_list[0]
	timestamp_list = [ e - base_time for e in timestamp_list ]
	max_time = timestamp_list[-1]

	frequency_list = [ float(e) / 1000000.0 for e in frequency_list ]

	fig, ax = plt.subplots()

	ax.plot(timestamp_list, frequency_list)
	ax.set_title("YCSB Workload " + workload + " (" + delay + " delay)", fontsize = 20, fontweight = "bold")
	ax.set_xlabel("Time since first query ($s$)", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("SQLite CPU Freq ($GHz$)", fontsize = 16, fontweight = "bold")
	ax.set_ylim([0, 2.7])
	ax.set_xlim([0, max_time])

	print(len(timestamp_list))
	print(len(frequency_list))

	output_file_name = filename + ".txt" #"outfile.csv"
	output_file = open(output_file_name, "w")
	output_line = ""

	for i in range(len(timestamp_list)):

		output_line = str(timestamp_list[i]) + "\t" + str(frequency_list[i]) + "\r\n"

		output_file.write(output_line)

	#end_for

	output_file.close()

	plt.show()

	fig.savefig("graphs/frequency_" + workload + "_" + delay + ".pdf", bbox_inches = "tight")

#end_def


main()


