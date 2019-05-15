
import json
import sys
import gzip
import json

import os


def get_latency(file_name):

	#print("Hello world %s, %d" % ("bye", 20))

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


def main():

	#prefix = "repeat_batt/"
	file_list = []
	latency = 0.0
	latency_list = []

	prefix = sys.argv[1]
	file_list = os.listdir(prefix)

	'''
	prefix = "threading/c/bdb_c_"
	file_list = []
	for i in range(1, 7):
		file_list.append(str(i) + ".gz")
	#end_for
	'''

	for filename in file_list:

		if (filename[0:4] != "YCSB"):
			continue
		#end_if

		print(filename)
		print(prefix + filename)
		latency = get_latency(prefix + filename)
		latency_list.append(latency)

	#end_for

	print(latency_list)

#end_def


def quick():

	filename = sys.argv[1]

	get_latency(filename)

#end_def


quick() #main()




