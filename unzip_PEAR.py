from os import listdir
import os
import gzip
import sys
from subprocess import call
from os.path import expanduser
import time
import subprocess

UNZIPPED_DIRECTORY = "unzipped/"
ASSEMBLED_DIRECTORY = "assembled/"

walk_dir = sys.argv[1]




if not os.path.exists(UNZIPPED_DIRECTORY):
    os.makedirs(UNZIPPED_DIRECTORY)
if not os.path.exists(ASSEMBLED_DIRECTORY):
    os.makedirs(ASSEMBLED_DIRECTORY)


def runPear(pair):
	home = expanduser("~")
	args = [home + '/bin/pear', '-f', UNZIPPED_DIRECTORY + pair[0], '-r', UNZIPPED_DIRECTORY + pair[1], '-o', ASSEMBLED_DIRECTORY + pair[0].split('_')[0], '-j', '8']

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

for root, subdirs, files in os.walk(walk_dir):
	if len(files) > 0:
		for f in files:
			if f.split('.')[-1] == 'gz':
				print 'Copying/Unzipping ' + f
				call(["cp", os.path.join(root, f), UNZIPPED_DIRECTORY])
				call(["gunzip", UNZIPPED_DIRECTORY + f])

# Create Log File
fullLog = open('merge_report.log', 'w')
fullLog.close()

fastqFiles = []
for f in listdir(UNZIPPED_DIRECTORY):
	if f.split('.')[len(f.split('.'))-1] == 'fastq':
		fastqFiles.append(f)

forwardReads = []
for f in fastqFiles:
	if f.split('_')[3] == 'R1':
		forwardReads.append(f)
forwardReads = sorted(forwardReads)

pairedReads = []
for fwd in forwardReads:
	ID = fwd.split('_')[:2]
	for rev in fastqFiles:
		if rev.split('_')[:2] == ID and rev.split('_')[3] == 'R2':
			pairedReads.append([fwd, rev])


print 'Found ' + str(len(pairedReads)) + ' pairs'
for pair in pairedReads:
	runPear(pair)










