#!/usr/bin/python

import sys
import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine
import Monsoon.Operations as op
import Monsoon.reflash as reflash

import os
import time

# /home/carlnues/.local/lib/python2.7/site-packages/Monsoon/

def main():

	output_file = "" # file handle
	output_filename = "monsoonout.txt"
	log_file = "" # file handle
	log_filename = "monsoonlog.txt"
	sample_count = 5000 * 60 * 30 # 5000 per second, i.e. set to 5000 for 1 second
	Mon = "" # HVPM object
	engine = "" # sampleEngine object
	samples = [[]]
	sample_metadata = ""

	print("Monsoon:  Start sampling")

	'''
	print(os.getpid())
	time.sleep(1)
	print("Now")
	'''

	Mon = HVPM.Monsoon()
	Mon.setup_usb()

	'''
	Mon.setVout(0)
	print("done")
	sys.exit(0)
	'''

	Mon.setVout(4.0)
	engine = sampleEngine.SampleEngine(Mon)

	'''
	engine.enableCSVOutput("testfoobar.csv")
	engine.ConsoleOutput(True)
	engine.startSampling(sample_count)
	'''

	#'''
	engine.disableCSVOutput()
	#engine.ConsoleOutput(True)
	engine.ConsoleOutput(False)
	engine.startSampling(sample_count)
	samples = engine.getSamples()
	#'''

	#Mon.setVout(0.0)

	'''
	for e in range(len(samples[sampleEngine.channels.timeStamp])):
		timeStamp = samples[sampleEngine.channels.timeStamp][e]
		Current = samples[sampleEngine.channels.MainCurrent][e]
		print("current at t " + repr(timeStamp) + " is " + repr(Current) + "mA")
	#end_for
	'''

	# samples[x]:  0 = time; 1 = current; 4 = voltage

	# Save out results:
	output_file = open(output_filename, "w")
	sample_metadata = "{\"Dropped\":" + str(engine.dropped) + ", \"Events\":" + str(len(samples[0])) + "}"
	output_file.write(sample_metadata + "\n")
	for i in range(len(samples[0])):
		output_file.write(repr(samples[0][i]))
		output_file.write("\t")
		output_file.write(repr(samples[1][i]))
		output_file.write("\t")
		output_file.write(repr(samples[4][i]))
		#output_file.write("\t")
		#output_file.write(repr(samples[6][i]))
		output_file.write("\n")
	#end_for
	output_file.close()

	# Record metadata to progress logfile:
	log_file = open(log_filename, "w")
	log_file.write(sample_metadata + "\n")
	log_file.close()

	print("Monsoon:  Stopped sampling.  Metadata:  " + sample_metadata)

	# Return error if we had dropped events:
	if (engine.dropped != 0):
		sys.exit(1)
	#end_if

	sys.exit(0)

#end_def


main()


