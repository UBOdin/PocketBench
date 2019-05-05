
import json
import sys
import gzip
import json

import matplotlib.pyplot as plt
import numpy as np

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


def get_energy(input_filename, end_line):

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
	start_line = 0

	input_file = gzip.open(input_filename, "r")
	input_file.readline() # Skip drop count

	start_line = 5000 * 10

	while (True):

		iteration += 1

		#input_line = str(input_file.readline())[2:-1]
		input_line = input_file.readline().decode("ascii")

		if (input_line == ""):
			# Overran logfile.  Return 0:
			amps_total = 0
			watts_total = 0
			break
		#end_if

		if (iteration < start_line):
			continue
		#end_if

		#'''
		if (iteration == end_line):
			break
		#end_if
		#'''

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

	'''
	print("Current:  " + str(amps_total))
	print("Energy:  " + str(watts_total))
	'''

	return amps_total

#end_def


def get_mean_error(end_line):

	pathname = ""
	energy_prefix = "monsoon_NULL_N_null_"
	energy = 0.0
	energy_list = []
	energy_mean = 0.0
	energy_error = 0.0
	energy_mean_list = []

	governor_list = ["userspace_300000", "userspace_1267200", "userspace_2649600", "interactive_none", "ondemand_none"]
	directory_list = ["../null_01", "../null_02", "../null_03"]

	for governor in governor_list:

		energy_list = []
		for directory in directory_list:
			pathname = directory + "/" + energy_prefix + governor + ".gz"
			energy = get_energy(pathname, end_line)
			print(pathname + " " + str(energy))
			energy_list.append(energy)
		#end_for
		print(energy_list)
		energy_mean, energy_error = mean_margin(energy_list)
		print(energy_mean, energy_error)
		energy_mean_list.append(energy_mean)

	#end_for

	return energy_mean_list

#end_def


def main():

	print("Hello World")

	nulltimes_dict = {}

	for i in range(500000, 1001000, 50000):

		print("STARTING:  " + str(i))
		end_line = i
		nulltimes_dict[end_line] = get_mean_error(end_line)

	#end_for

	print(nulltimes_dict)

#end_def


main()


