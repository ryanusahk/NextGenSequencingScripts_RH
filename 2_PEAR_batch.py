from os import listdir
import os
import sys
import gzip
import subprocess
import time
import sys
from os.path import expanduser

unzippedDirectory = sys.argv[1]

# Create Log File
fullLog = open('merge_report.log', 'w')
fullLog.close()

# http://atacama.qb3.berkeley.edu/auto/sahara/namib/home/ryanhsu/bin/pear

def runPear(pair):

	home = expanduser("~")
	args = [home + '/bin/pear', '-f', unzippedDirectory + '/' + pair[0], '-r', unzippedDirectory + '/' + pair[1], '-o', pair[0].split('_')[0], '-j', '8']

	print time.strftime('%c') + '\n'
	print 'Running PEAR on ' + str(pair) + '\n'

	with open('merge_report.log', 'a') as fullLog:
		fullLog.write(time.strftime('%c') + '\n')
		fullLog.write('Running PEAR on ' + str(pair) + '\n')
		process = subprocess.Popen(args, stdout=subprocess.PIPE)
		for line in iter(process.stdout.readline, ''):
			sys.stdout.write(line)
			fullLog.write(line)
	process.wait()
	fullLog = open('merge_report.log', 'a')
	fullLog.write('\n')
	fullLog.close()


# Create output directory if it doesn't exist
directoryListing = listdir(os.path.dirname(os.path.abspath(__file__)) + '/' + unzippedDirectory)

# Identify fwd and rev read pairs
fastqFiles = []
for f in directoryListing:
	if f.split('.')[len(f.split('.'))-1] == 'fastq':
		fastqFiles.append(f)

forwardReads = []
for f in fastqFiles:
	if f.split('_')[3] == 'R1':
		forwardReads.append(f)

pairedReads = []
for fwd in forwardReads:
	ID = fwd.split('_')[:2]
	for rev in fastqFiles:
		if rev.split('_')[:2] == ID and rev.split('_')[3] == 'R2':
			pairedReads.append([fwd, rev])
			print [fwd, rev]


print 'Found ' + str(len(pairedReads)) + ' pairs'

print 'Please check all pairs are accounted for!'

print 'PEAR EVERYTHING'
response = raw_input('Continue? y/n: ')
if response == 'y':
	for pair in pairedReads:
		runPear(pair)
else:
	exit()
