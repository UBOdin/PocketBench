
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
			sys.exit(2)
		#end_if

	#end_while

	input_file.close()

	if (iteration < 100000):
		print("Error:  Unexpected linecount")
		sys.exit(3)
	#end_if

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

