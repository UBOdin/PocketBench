import sys
import json
import argparse
import gzip

parser = argparse.ArgumentParser()
parser.add_argument('dbType', type=str, help="Database type.")
parser.add_argument('input', type=str, help="Input data file.")
parser.add_argument('--summary', action="store_true", help="Don't print detailed information.")
args = parser.parse_args()

dbType = args.dbType
workload = args.input

mypid = 0
sced_on_core = 999
data = dict()
dict_count = 0

resetline = False
holdline = ''
total = 0.0
start_time = 0.0
end_time = 0.0

with gzip.open(workload,'r') as log:
	between = 0
	iomode = False
	for line in log:
		if dbType + '_START' in line:
			start_time = float(line.split()[3].split(':')[0])
			between = 1
			mypid = line.split('[0')[0].split('-')[1].split()[0]
			core = int(line.split(']')[0].split('[')[1])
			sced_on_core = core
			assert(mypid != 0)
		if between == 0:
			continue
		'''
		if resetline == True:
			if line == holdline:
				resetline = False
				holdline = ''
				continue
			else:
				continue
		'''
		if 'prev_pid='+mypid in line:
			sced_on_core = 999
			core = int(line.split(']')[0].split('[')[1])
		if 'next_pid='+mypid in line:
			core = int(line.split(']')[0].split('[')[1])
			sced_on_core = core
		if dbType + '_END' in line:
			end_time = float(line.split()[3].split(':')[0])
			break

		# Thread queues I/O
		if (('block_rq_insert' in line) and ('withjson' in line)):
			iomode = True
			continue
		#end_if
		# TODO:  trap for double inserting?  (can happen?)

		# Thread blocks:
		if ((iomode == True) and ('prev_pid='+mypid in line)):
			timestampstart = float(line.split()[3].split(':')[0])
			sced_on_core = 999
			core = int(line.split(']')[0].split('[')[1])

			continue
		#end_if
		# TODO:  trap for double blocking
		# TODO:  need to track core #??


		# Thread runs:
		if ((iomode == True) and ('next_pid='+mypid in line)):
			core = int(line.split(']')[0].split('[')[1])
			sced_on_core = core

			timestampend = float(line.split()[3].split(':')[0])
			total += (timestampend - timestampstart)*1000
			data[dict_count] = [['IO Event', line],['Waiting time',(timestampend - timestampstart)*1000]]
			dict_count += 1

			continue
		#end_if
		# TODO:  trap for orphan unblocking
		# TODO:  need to track core #?

		# Thread dequeues I/O
		if (('block_rq_complete' in line) and ('withjson' in line)):
			iomode = False

			continue
		#end_if
		# TODO:  Need to filter for correct PID

	#end_for

#end_with


'''
			with gzip.open(workload, 'r') as log2:
				linecount = 0
				desced = False
				iocomplete = False

				sameline = 0
				for line2 in log2:
					
					if line == line2:
						sameline = 1
					if sameline == 0:
						continue
					linecount += 1
					if 'prev_pid='+mypid in line2:
						timestampstart = float(line2.split()[3].split(':')[0])
						sced_on_core = 999
						core = int(line2.split(']')[0].split('[')[1])
						if linecount <= 10:
							desced = True

					if 'next_pid='+mypid in line2:
						core = int(line2.split(']')[0].split('[')[1])
						sced_on_core = core
						if iocomplete != True:
							break
						else:
							timestampend = float(line2.split()[3].split(':')[0])
							total += (timestampend - timestampstart)*1000
							holdline = line2
							resetline = True
							data[dict_count] = [['IO Event', line],['Waiting time',(timestampend - timestampstart)*1000]]
							dict_count += 1
							break
					
					if 'block_rq_complete' in line2:
						if insertaddr in line2:
							if desced == True:
								iocomplete = True


'''


assert(mypid != 0)

if args.summary:
	summary = dict()

	readnum = 0
	waitreadtime = 0.0
	writenum = 0
	waitwritetime = 0.0
	flushnum = 0
	waitflushtime = 0.0

	for key in data:
		op = data[key][0][1].split('179,0 ')[1].split()[0]
		if 'R' in op:
			readnum += 1
			waitreadtime += float(data[key][1][1])
		if 'W' in op:
			writenum += 1
			waitwritetime += float(data[key][1][1])
		if 'F' in op:
			flushnum += 1
			waitflushtime += float(data[key][1][1])
	wallclocktime = (end_time - start_time)*1000
	summary['Summary'] = [['Time Waiting on IO',['Total',total],['Percentage',(total / wallclocktime)*100]],['Reads',['Number of Ops',readnum],['Time Waiting for Reads',waitreadtime]],['Writes',['Number of Ops',writenum],['Time Waiting for Writes',waitwritetime]],['Flushes',['Number of Ops',flushnum],['Time Waiting for Flushes',waitflushtime]]]
	print json.dumps(summary, indent=2)

else:

	print json.dumps(data, indent=2)

