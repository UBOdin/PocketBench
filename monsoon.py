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

	print("Hello World")

	'''
	print(os.getpid())
	time.sleep(1)
	print("Now")
	'''
	sample_count = 5000 * 60 * 30 # 5000 per second, i.e. set to 5000 for 1 second

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

	'''
	for e in range(len(samples[sampleEngine.channels.timeStamp])):
		timeStamp = samples[sampleEngine.channels.timeStamp][e]
		Current = samples[sampleEngine.channels.MainCurrent][e]
		print("current at t " + repr(timeStamp) + " is " + repr(Current) + "mA")
	#end_for
	'''

	if (len(samples[0]) != sample_count):
		print("Incorrect sample count")
		#sys.exit(1)
	#end_if

	#'''
	# samples[x]:  0 = time; 1 = current; 4 = voltage
	output_filename = "monsoonout.txt"
	'''
	print("Argcount:  " + str(len(sys.argv)))
	for i in range(len(sys.argv)):
		print(sys.argv[i])
	#end_for
	output_filename = "energy/monsoon_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[3] + "_" + sys.argv[4] + "_" + sys.argv[5]
	print("Output file:  " + output_filename)
	'''

	output_file = "" # file handle
	output_file = open(output_filename, "w")
	output_file.write("Dropped:  " + str(engine.dropped) + "\n")
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
	#'''

	#Mon.setVout(0.0)

	print("Length:  " + str(len(samples[0])))

	print("Dropped:  " + str(engine.dropped))

	print("Goodbye world")

#end_def


main()


