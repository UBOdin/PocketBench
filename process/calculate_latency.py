
import json
import sys
import gzip
import json


def main():

	#print("Hello world %s, %d" % ("bye", 20))

        input_file_name = ""
	logline = ""
	iteration = 0
	starttime = 0.0
	endtime = 0.0

	if (len(sys.argv) != 2):
		print("Missing input file name")
		sys.exit()
	#end_if
	input_file_name = sys.argv[1]
	#input_file = open(input_file_name, 'r')

	input_file = gzip.open(sys.argv[1])

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

#end_def




main()




