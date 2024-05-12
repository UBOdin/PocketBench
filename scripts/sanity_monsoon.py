
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

	bucketitertotal = 500
	bucketitercount = 0
	bucketamps = 0
	bucketamps_list = []
	bucketmax = 0
	bucketcount = 0

	input_file = open(file_name, "r")
	# Skip first line:
	logline = input_file.readline()

	iteration = 0

	while (True):

		# Keep reading until finished:
		logline = input_file.readline()

		if (logline == ""):
			break
		#end_if

		#'''
		iteration += 1
		if (iteration % 1000 == 0):
			#break
			#print("Iteration:  ", iteration)
			pass
		#end_if
		#'''

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

			sys.exit(1)
		#end_if

		'''
		amps_total += amps

		bucketitercount += 1
		bucketamps += amps
		if (bucketitercount == bucketitertotal):
			if (bucketamps > bucketmax):
				bucketmax = bucketamps
			#end_if
			bucketamps_list.append(bucketamps)
			bucketitercount = 0
			bucketamps = 0
		#end_if
		'''

	#end_while

	input_file.close()

	'''
	secondspertick = 10
	bucketcount = len(bucketamps_list)
	seconds = int(bucketcount / (5000.0 / bucketitertotal))
	xtick_list = np.arange(0, bucketcount, (5000.0 * secondspertick) / bucketitertotal)
	xlabel_list = []
	for e in range(len(xtick_list)):
		xlabel_list.append(str(int(e * secondspertick)))
	#end_for

	print(xlabel_list)
	print(len(xtick_list))
	print(seconds)
	print(bucketcount)
	print(bucketitercount)
	print(bucketmax)

	mampspertick = 100
	ytick_list = np.arange(0, bucketmax * 1.1, (bucketitertotal * mampspertick))
	ylabel_list = []
	for e in range(len(ytick_list)):
		ylabel_list.append(str(int(e * mampspertick)))
	#end_for

	#return amps_total / (3600.0 * 5.0)
	#return bucketamps_list

	fig, ax = plt.subplots()

	#ax.axis([0, bucketcount, 0, bucketmax * 1.1])
	ax.set_xticks(xtick_list)
	ax.set_xticklabels(xlabel_list)
	ax.set_xlabel("Time, seconds", fontsize = 12, fontweight = "bold")
	ax.set_yticks(ytick_list)
	ax.set_yticklabels(ylabel_list)
	ax.set_ylabel("Current, mA", fontsize = 12, fontweight = "bold")

	# N.b. this is mA, NOT uA or mAh or uAh -- this is current, not power

	print(bucketcount)
	print(bucketmax)
	#ax.axis([0, 700, 0, 350000])

	ax.plot(bucketamps_list)

	plt.show()
	'''

	return

#end_def


def main():

	filename = ""

	#'''
	filename = sys.argv[1]
	print("Sanity checking energyfile %s" %(filename))	
	get_energy(filename)
	print("Passed")
	#'''
	'''
	filelistname = "filelist.txt"
	filelisthandle = open("scripts/" + filelistname, "r")
	filename = ""

	while (True):
		filename = filelisthandle.readline()[:-1]
		if (filename == ""):
			break
		#end_if
		print("Sanity checking energyfile %s" %(filename))	
		get_energy("logs/" + filename)
		print("Passed")
	#end_while

	filelisthandle.close()
	'''

	return

#end_def


main()

