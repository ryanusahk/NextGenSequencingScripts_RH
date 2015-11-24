from os import listdir
import os
import sys
import gzip
import subprocess
import time
import sys
from os.path import expanduser
import json

ASSEMBLED_DIRECTORY = sys.argv[1]
HMB_DATABASE = sys.argv[2]
BLAST6OUTPUT = 'blast6/temp.blast6'
TALLY_TXT = 'tally.txt'
TALLY_HMB = 'tally.hmb'
PATH_TO_USEARCH8 = '/bin/usearch8'

if not os.path.exists('blast6'):
    os.makedirs('blast6')

# Create Log File
sample_dictionary = dict()
organism_database = []


# http://atacama.qb3.berkeley.edu/auto/sahara/namib/home/ryanhsu/bin/pear

def getAllOrganisms(database):
	arrayoforgs = []
	database = open(HMB_DATABASE, 'r').read().split('\n')
	for line in database:
		if len(line) > 0 and line[0] == '>':
			arrayoforgs.append(line[1:])
	return arrayoforgs

def tally(sample_name):
	counts_dictionary = dict()
	for org in organism_database:
		counts_dictionary[org] = 0

	blast6file = open(BLAST6OUTPUT, 'r').read().split('\n')
	for line in blast6file:
		if len(line) > 0:
			identitity = line.split('\t')[1]
			counts_dictionary[identitity] += 1

	sample_dictionary[sample_name] = counts_dictionary

def usearch(assembledFile):
	sample_name = assembledFile[:8]
	home = expanduser("~")
	args = [home + PATH_TO_USEARCH8,
			'-usearch_global', assembledFile,
			'-db', HMB_DATABASE, 
			'-blast6out', BLAST6OUTPUT,
			'-strand', 'both',
			'-id', '.95']

	process = subprocess.Popen(args, stdout=subprocess.PIPE)

	for line in iter(process.stdout.readline, ''):
		sys.stdout.write(line)

	process.wait()

def findAssembledFASTQ(directoryList):
	assembledFiles = []
	for f in directoryList:
		if f.split('.')[-2] == 'assembled' and f.split('.')[-1] == 'fastq':
			assembledFiles.append(f)
	return sorted(assembledFiles)

def saveTallyHMB():
	jsonOutput = json.dumps(sample_dictionary)
	print 'Saving ' + TALLY_HMB
	open(TALLY_HMB, 'w').write(jsonOutput)

def saveTallyText():
	tallyText = 'sample'
	for org in organism_database:
		tallyText += '\t' + org

	plateSet = 'HMB'
	for platenum in range(1,13):
		for letter in 'ABCDEFGH':
			for column in range(1,13):
				sampleID = argsToSampleID(plateSet, platenum, letter, column)
				if sampleID in sample_dictionary:
					tallyText += '\n'
					tallyText += sampleID
					for org in organism_database:
						tallyText += '\t'
						tallyText += str(sample_dictionary[sampleID][org])
	print 'Saving ' + TALLY_TXT
	open(TALLY_TXT, 'w').write(tallyText)

def argsToSampleID(plateSet, plate, letter, column):
	return plateSet+"%02d"%(plate,)+letter+"%02d"%(column)

def main():
	global organism_database
	organism_database = getAllOrganisms(HMB_DATABASE)
	getAllOrganisms(HMB_DATABASE)
	directoryListing = listdir(os.path.dirname(os.path.abspath(__file__)) + '/' + ASSEMBLED_DIRECTORY)
	fastQs = findAssembledFASTQ(directoryListing)

	for i in range(len(fastQs)):
		f = fastQs[i]
		sample_name = f[:8]
		print '\n' + time.strftime('%c') + '\n'
		print 'PROGRESS: ' + str(i+1) + '/' + str(len(fastQs)) + '   ' + str((100.0*i)/len(fastQs)) + '%'
		print 'Running USEARCH on ' + f
		usearch(ASSEMBLED_DIRECTORY + '/' + f)
		print 'Tallying ' + f
		tally(sample_name)
	# print sample_dictionary['HMB01A01']
	saveTallyText()
	saveTallyHMB()

main()
