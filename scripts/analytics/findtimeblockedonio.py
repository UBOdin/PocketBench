# find latency numbers
# Usage: python findtimeblockedonio.py (BDB|SQL) (Workload.log) {--summary}
#															       ^ Optional

# Detailed json = [starttime, endtime, runtime, insert op, complete op, addr]
# Summary json = [IOcount, min runtime, max runtime, average runtime, IOcount of events that were 50% more or less then the average]


import sys
import json
import argparse
import gzip

parser = argparse.ArgumentParser()
parser.add_argument('dbType', type=str, help="Database type.")
parser.add_argument('input', type=str, help="Input data file.")
parser.add_argument('--summary', action="store_true", help="Don't print detailed information.")
args = parser.parse_args()

#print args

dbType = args.dbType
workload = args.input

mypid = 0
sced_on_core = 999
#deltas = []
data = dict()
dict_count = 0

resetline = False
holdline = ''
total = 0.0
start_time = 0.0
end_time = 0.0

with gzip.open(workload,'r') as log:
	between = 0
	for line in log:
		if dbType + '_START' in line:
			start_time = float(line.split()[3].split(':')[0])
			between = 1
			mypid = line.split('[0')[0].split('-')[1].split()[0]
			core = int(line.split(']')[0].split('[')[1])
			sced_on_core = core
			#print core
			assert(mypid != 0)
		if between == 0:
			continue
		#if 'sched_switch' in line or 'START' in line or 'END' in line or 'block':
		if resetline == True:
			if line == holdline:
				resetline = False
				holdline = ''
				continue
			else:
				continue
		if 'prev_pid='+mypid in line:
			sced_on_core = 999
			core = int(line.split(']')[0].split('[')[1])
			#print core
			#break
		if 'next_pid='+mypid in line:
			core = int(line.split(']')[0].split('[')[1])
			sced_on_core = core
			#print core
			#break
		if dbType + '_END' in line:
			end_time = float(line.split()[3].split(':')[0])
			break
		if 'block_rq_insert' in line:
			#timestampstart = float(line.split()[3].split(':')[0])
			insertaddr = line.split()[9] + ' + ' + line.split()[11]
			
			#addr = ad[9] 
			#addr = addr + ' + ' + ad[11]
			#print timestamp
			#if sced_on_core != 999:
			#	continue
			if 'withjson' not in line:
				continue
			#print insertaddr
			#print line
			
			with gzip.open(workload, 'r') as log2:
				linecount = 0
				desced = False
				iocomplete = False

				#count += 1
				sameline = 0
				for line2 in log2:
					
					if line == line2:
						sameline = 1
					if sameline == 0:
						continue
					linecount += 1
					#if sced_on_core != 999:
					#	break
					if 'prev_pid='+mypid in line2:
						timestampstart = float(line2.split()[3].split(':')[0])
						sced_on_core = 999
						core = int(line2.split(']')[0].split('[')[1])
						if linecount <= 10:
							desced = True

						#print core
						#break
					if 'next_pid='+mypid in line2:
						core = int(line2.split(']')[0].split('[')[1])
						sced_on_core = core
						#print core
						#break
						if iocomplete != True:
							break
						else:
							timestampend = float(line2.split()[3].split(':')[0])
							#print 'hello'
							#deltas.append((timestampend - timestampstart)*1000)
							total += (timestampend - timestampstart)*1000
							holdline = line2
							resetline = True
							data[dict_count] = [['IO Event', line],['Waiting time',(timestampend - timestampstart)*1000]]
							dict_count += 1
							break
					
					if 'block_rq_complete' in line2:
						if insertaddr in line2:
							#timestampend = float(line.split()[3].split(':')[0])
							#insert_complete[count] = [line,line2]
							#count += 1
							#deltas.append(timestampend - timestampstart)
							#break 
							if desced == True:
								iocomplete = True

assert(mypid != 0)

#print mypid
#print deltas
#total = 0.0
#for i in deltas:
#	total += i

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
		#print op
		if 'R' in op:
			readnum += 1
			waitreadtime += float(data[key][1][1])
		if 'W' in op:
			writenum += 1
			waitwritetime += float(data[key][1][1])
		if 'F' in op:
			flushnum += 1
			waitflushtime += float(data[key][1][1])
		#break
	wallclocktime = (end_time - start_time)*1000
	summary['Summary'] = [['Time Waiting on IO',['Total',total],['Percentage',(total / wallclocktime)*100]],['Reads',['Number of Ops',readnum],['Time Waiting for Reads',waitreadtime]],['Writes',['Number of Ops',writenum],['Time Waiting for Writes',waitwritetime]],['Flushes',['Number of Ops',flushnum],['Time Waiting for Flushes',waitflushtime]]]
	print json.dumps(summary, indent=2)

else:

	#print total

	print json.dumps(data, indent=2)

#data = dict()






