
import json
import sys
import gzip
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

import math
import statistics


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


def process_loglines(file_name, trace_list_list):

	# file_name = ""
	# trace_list_list = []

	logline = ""
	iteration = 0
	cpu = 0
	pid = 0
	time = 0.0
	index = 0
	func = ""
	freq = 0
	freq_list = [0, 0, 0, 0, 0, 0, 0, 0]
	startflag = False
	bench_cpu = 0
	bench_pid = 0
	param = ""
	param_list = []
	fixed_list = []
	trace_list = []
	target_cpu = 0
	sleepstate = 0
	idletime = 0
	idlecount = 0

	perfcycles = 0

	input_file = gzip.open(file_name, "r")

	while (True):

		# Keep reading until finished:
		logline = input_file.readline().decode("ascii")

		if (logline == ""):
			print("Never hit endmark")
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

		if (len(logline) < 50):
			continue
		#end_if
		if (logline[46] != ":"):
			continue
		#end_if

		pid = int(logline[17:23])
		cpu = int(logline[24:27])
		time = float(logline[33:46])

		index = logline.find(":", 48, -1)
		if (index == -1):
			print("Invalid ftrace function")
			sys.exit(1)
		#end_if
		func = logline[48:index]

		#print("%d  %d  %f  %s" % (pid, cpu, time, func))

		if (func == "tracing_mark_write"):
			if (startflag == False):
				if ("SQL_START" in logline):
					startflag = True
					bench_cpu = cpu
					bench_pid = pid
					trace_list = [iteration, time, "start", cpu, freq]
					trace_list_list.append(trace_list)
					#starttime += float(logline[33:46])
				#end_if
			else:
				#if ("SQL_END" in logline):
				if ("Cycle data" in logline):
					trace_list = [iteration, time, "end", cpu, freq]
					trace_list_list.append(trace_list)
					perfcycles = int(logline[79:])
					break
					#endtime += float(logline[33:46])
				#end_if
			#end_if
		#end_if

		if (startflag == False):
			continue
		#end_if

		# N.b. for the cpu_frequency event, the cpu field is the CPU# on which the governor
		# runs.  It is *not* necessarily the *target* CPU# for which the speed is set.
		if (func == "cpu_frequency"):
			index = logline.find(" ", 63, -1)
			if (index == -1):
				print("Invalid speed delimiter")
				sys.exit(1)
			#end_if
			if (logline[63:69] != "state="):
				print("Invalid speed parameter")
				sys.exit(1)
			#end_if
			freq = int(logline[69:index])

			#index = logline.find(" ", index, -1)
			if (logline[index + 1:index + 8] != "cpu_id="):
				print("Invalid run cpu parameter")
				sys.exit(1)
			#end_if
			target_cpu = int(logline[index + 8:-1])  # Fetch the *target* cpu#

			freq_list[target_cpu] = freq
			if (target_cpu == bench_cpu):
				trace_list = [iteration, time, "speed", target_cpu, freq]
				trace_list_list.append(trace_list)
			#end_if
		#end_if

		#'''
		if (func == "cpu_idle"):
			index = logline.find(" ", 58, -1)
			if (index == -1):
				print("Invalid speed delimiter")
				sys.exit(1)
			#end_if
			if (logline[58:64] != "state="):
				print("Invalid speed parameter")
				sys.exit(1)
			#end_if
			sleepstate = int(logline[64:index])
			if (sleepstate == 4294967295):
				sleepstate = -1
				idletime += time
				idlecount += 1
			else:
				idletime -= time
			#end_if

			#index = logline.find(" ", index, -1)
			if (logline[index + 1:index + 8] != "cpu_id="):
				print("Invalid idle cpu parameter")
				sys.exit(1)
			#end_if
			target_cpu = int(logline[index + 8:-1])  # Fetch the *target* cpu#

			# Test hypo:
			if (cpu != target_cpu):
				print("cpu mismatch")
				sys.exit(1)
			#end_if

			#freq_list[target_cpu] = freq
			if (target_cpu == bench_cpu):
				trace_list = [iteration, time, "idle", target_cpu, sleepstate]
				trace_list_list.append(trace_list)
			#end_if
		#end_if
		#'''

		if (func == "sched_migrate_task"):
			param_list = logline[68:].split(" ")

			# Kludge to sanitize for task names containing spaces:
			fixed_list = []
			for param in param_list:
				if ("=" in param):
					fixed_list.append(param)
				#end_if
			#end_for
			param_list = fixed_list

			if (param_list[1][0:4] != "pid="):
				print("Invalid migrate parameter")
				sys.exit(1)
			#end_if

			if (int(param_list[1][4:]) == bench_pid):

				if (param_list[3][0:9] != "orig_cpu="):
					print("Invalid origin parameter")
					sys.exit(1)
				#end_if
				if (int(param_list[3][9:]) != bench_cpu):
					print("Invalid origin cpu")
					sys.exit(1)
				#end_if
				if (param_list[4][0:9] != "dest_cpu="):
					print("Invalid destination parameter")
					sys.exit(1)
				#end_if

				'''
				print(iteration)
				print(time)
				print(bench_cpu)
				print(str(int(param_list[4][9:])))
				'''

				bench_cpu = int(param_list[4][9:])

				trace_list = [iteration, time, "migrate", bench_cpu, cpu]
				trace_list_list.append(trace_list)
	
			#end_if


		#end_if

	#end_while

	#print("iterations:  %d" % (iteration))

	input_file.close()

	print("Idle time:  %f" % (idletime))
	print("Idle count:  %d" % (idlecount))

	return perfcycles

#end_def


def graph_freq_time(trace_list_list):

	# trace_list_list = []
	trace_iter = ""  # iterator
	time_list = []
	speed_list = []
	time = 0.0
	func = ""
	speed = 0
	savespeed = 0  # speed from previous non-idle iteration
	basetime = 0.0
	maxtime = 0.0
	maxspeed = 0
	idlestate = 0
	cycles = 0

	fig, ax = plt.subplots()

	trace_iter = iter(trace_list_list)
	trace_list = next(trace_iter)
	basetime = trace_list[1]
	assert (trace_list[2] == "start"), "Expected start"
	i = -1
	#speed = 1
	speed = 1747200 #1401600
	maxspeed = 1747200 #1401600
	savespeed = 1747200 #1401600
	idlestate = -1  # Prime to non-idle

	while (True):

		i += 1

		try:
			trace_list = next(trace_iter)
		except StopIteration:
			break
		#end_try

		#print(i)

		time = trace_list[1]
		func = trace_list[2]
		if (func == "migrate"):
			#print("Migrate on line %d" % (i))
			continue
		#end_if
		if (func == "speed"):

			if (idlestate < 0):
				time_list.append(time - basetime)
				speed_list.append(speed)

				speed = trace_list[4]
				if (speed > maxspeed):
					maxspeed = speed
				#end_if
				savespeed = speed

				time_list.append(time - basetime)
				speed_list.append(speed)
				#cycles += oldspeed * (time - oldtime)
			#end_if

			if (idlestate == 0):
				savespeed = trace_list[4]
			#end_if

		#end_if

		if (func == "idle"):
			idlestate = trace_list[4]

			if (idlestate >= 0):
				# N.b. can't assert this -- can go from, e.g., idle state 0 to 2
				#assert (speed > 0), ("Expected > 0 speed on %d" % (i))
				time_list.append(time - basetime)
				speed_list.append(speed)
				speed = 0
				time_list.append(time - basetime)
				speed_list.append(speed)
			#end_if

			if (idlestate < 0):
				# Small bug:  not tracking previous CPU speed when migrating to a new core (ignore and use speed of old core)
				#assert (speed == 0), ("Expected 0 speed on %d %f" % (i, time))
				time_list.append(time - basetime)
				speed_list.append(speed)
				speed = savespeed
				time_list.append(time - basetime)
				speed_list.append(speed)
			#end_if

		#end_if

	#end_while
	assert (trace_list[2] == "end"), "Expected end"
	maxtime = trace_list_list[-1][1] - basetime


	#'''
	#ax.scatter(time_list, speed_list, s = 5, color = "black")
	ax.plot(time_list, speed_list, color = "black")
	ax.scatter(time_list, speed_list, color = "black", s = 1)
	ax.axis([0, maxtime * 1.1, 0, maxspeed * 1.1])
	ax.set_title("Fixed 90 Governor, Workload A, log Delay", fontsize = 16, fontweight = "bold")
	ax.set_xlabel("Benchmark runtime (s)", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Benchmark CPU speed (kHz)", fontsize = 16, fontweight = "bold")

	plt.show()
	#'''
	print("Max time:  %f" % (maxtime))
	print("Max speed:  %d" % (maxspeed))

	return cycles, maxtime

#end_def


def bargraphs():

	cycle_list_list = []
	time_list_list = []
	cycle_list = []
	time_list = []
	cycles = 0
	time = 0
	filename = ""
	trace_list_list = []

	index_list = []
	cycle_mean_list = []
	cycle_err_list = []
	time_mean_list = []
	time_err_list = []
	mean = 0.0
	err = 0.0

	perfcycles = 0

	#prefix = "YCSB_SQL_A_0ms_"
	#prefix = "save_unpinned/YCSB_SQL_A_0ms_"
	#governor_list = ["schedutil_none", "userspace_50", "userspace_55", "userspace_60", "userspace_65", "userspace_70"]

	'''
	prefix = ""
	governor_list = ["save_unpinned/YCSB_SQL_A_0ms_schedutil_none", "save_unpinned/YCSB_SQL_F_0ms_schedutil_none", "save_pinned/YCSB_SQL_A_0ms_schedutil_none", "save_pinned/YCSB_SQL_F_0ms_schedutil_none"]
	label_list = ["", "Unpinned A", "Unpinned F", "Pinned A", "Pinned F"]
	'''
	#'''
	#prefix = "../logs/runs_20200521/"
	prefix = "../logs/save_runs_20210608/"
	#governor_list = ["save_unpinned/YCSB_SQL_A_0ms_schedutil_none", "save_pinned/YCSB_SQL_A_0ms_schedutil_none", "save_unpinned/YCSB_SQL_A_0ms_userspace_50", "save_pinned/YCSB_SQL_A_0ms_userspace_50", "save_unpinned/YCSB_SQL_A_0ms_userspace_55", "save_pinned/YCSB_SQL_A_0ms_userspace_55", "save_unpinned/YCSB_SQL_A_0ms_userspace_60", "save_pinned/YCSB_SQL_A_0ms_userspace_60", "save_unpinned/YCSB_SQL_A_0ms_userspace_65", "save_pinned/YCSB_SQL_A_0ms_userspace_65"]
	governor_list = ["save_unpinned/YCSB_SQL_F_0ms_schedutil_none", "save_pinned/YCSB_SQL_F_0ms_schedutil_none", "save_unpinned/YCSB_SQL_F_0ms_userspace_50", "save_pinned/YCSB_SQL_F_0ms_userspace_50", "save_unpinned/YCSB_SQL_F_0ms_userspace_55", "save_pinned/YCSB_SQL_F_0ms_userspace_55", "save_unpinned/YCSB_SQL_F_0ms_userspace_60", "save_pinned/YCSB_SQL_F_0ms_userspace_60", "save_unpinned/YCSB_SQL_F_0ms_userspace_65", "save_pinned/YCSB_SQL_F_0ms_userspace_65"]


	label_list = ["", "Unpinned Def", "Pinned Def", "Unpinned 50", "Pinned 50", "Unpinned 55", "Pinned 55", "Unpinned 60", "Pinned 60", "Unpinned 65", "Pinned 65"]
	#'''

	runno = 5
	barcount = len(governor_list) + 1

	for i, governor in zip(range(len(governor_list)), governor_list):

		print(governor)

		cycle_list = []
		time_list = []

		for run in range(runno):

			print(run)

			trace_list_list = []
			filename = prefix + governor + "_1_" + str(run) + ".gz"
			#print(filename)
			perfcycles = process_loglines(filename, trace_list_list)
			cycles, time = graph_freq_time(trace_list_list);

			'''
			if ("userspace" in governor):
				cycles = get_cycles(governor, time)
			#end_if
			'''
			cycles = perfcycles

			cycle_list.append(cycles)
			time_list.append(time)

		#end_for

		print(cycle_list)
		print(time_list)

		cycle_list_list.append(cycle_list)
		time_list_list.append(time_list)

		mean, err = mean_margin(cycle_list)
		cycle_mean_list.append(mean)
		cycle_err_list.append(err)

		mean, err = mean_margin(time_list)
		time_mean_list.append(mean)
		time_err_list.append(err)

		index_list.append(i + 1)

		print(governor)
		print(cycle_list)
		print(mean)
		print(err)
		print(runno)
		print("")

	#end_for

	print(cycle_mean_list)
	print(time_mean_list)
	print(index_list)

	#'''
	fig, ax = plt.subplots()

	ax.bar(index_list, cycle_mean_list, color = "red", width = .4)
	ax.errorbar(index_list, cycle_mean_list, color = "black", yerr = cycle_err_list, fmt = "o", elinewidth = 2, ecolor = "black", capsize = 10, capthick = 2)

	ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10])
	fb = ax.get_xticklabels()
	print("LEN")
	print(len(fb))
	print(fb)
	print(index_list)
	ax.set_xticklabels(label_list)

	#ax.axis([0, barcount, 5000000, 7000000])
	ax.axis([0, barcount, 7000000, 11000000])
	#ax.set_title("Workload A", fontsize = 16, fontweight = "bold")
	ax.set_title("Workload F", fontsize = 16, fontweight = "bold")
	ax.set_xlabel("CPU affinity and governor", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Perf HW CPU cycles (M) (90% confidence)", fontsize = 16, fontweight = "bold")

	plt.show()

	plt.close("all")
	#'''

	fig, ax = plt.subplots()

	ax.bar(index_list, time_mean_list, color = "red", width = .4)
	ax.errorbar(index_list, time_mean_list, color = "black", yerr = time_err_list, fmt = "o", elinewidth = 2, ecolor = "black", capsize = 10, capthick = 2)

	ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10])
	ax.set_xticklabels(label_list)

	ax.axis([0, barcount, 4, 6])
	#ax.set_title("Workload A", fontsize = 16, fontweight = "bold")
	ax.set_title("Workload F", fontsize = 16, fontweight = "bold")
	ax.set_xlabel("CPU affinity and governor", fontsize = 16, fontweight = "bold")
	ax.set_ylabel("Time (us) (90% confidence)", fontsize = 16, fontweight = "bold")

	plt.show()

	plt.close("all")


	return


#end_def


def get_cycles(governor, time):

	# governor = ""
	# time = 0.0
	cycles = 0
	suffix = ""

	speed = 0
	speed_dict = {"50":950500, "55":1045440, "60":1140480, "65":1235520, "70":1330560}

	suffix = governor[-12:]

	precount = suffix[-2:]

	speed = speed_dict[precount]

	print("CALC:  %d" % (speed * time))

	return speed * time

#end_def


def main():

	filename = ""
	trace_list_list = []
	cycles = 0
	time = 0

	perfcycles = 0

	print(sys.version_info)

	filename = sys.argv[1]

	print(filename)

	perfcycles = process_loglines(filename, trace_list_list)

	#print("early exit")
	#sys.exit(0)

	graph_freq_time(trace_list_list);
	print("bi")

	'''
	print(len(trace_list_list))

	for e in trace_list_list:
		print(e)
	#end_for
	'''

#end_def


main()
#bargraphs()

