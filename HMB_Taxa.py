from os import listdir
import os
import sys
import gzip
import subprocess
import time
import sys
from os.path import expanduser
import json


### FILE PATHS ###
ASSEMBLED_DIRECTORY = sys.argv[1]
HMB_DATABASE = sys.argv[2]
BLAST6OUTPUT = 'blast6/temp.blast6'
FILTERED_DIRECTORY = 'filtered/'
TALLY_TXT = 'tally.txt'
TALLY_HMB = 'tally.hmb'
REPORT_TXT = 'report.txt'
PATH_TO_USEARCH8 = '/bin/usearch8'

### FILTER OPTIONS ###
MIN_LENGTH = 300
F_ANNEALING_REGION = "ACTCCTACGGGAGGCAGCAGTG"
R_ANNEALING_REGION = "GGATTAGATACCCTGGTAGTCC"
MAX_PLATE_ID = 20


if not os.path.exists('blast6'):
    os.makedirs('blast6')
if not os.path.exists('filtered'):
	os.makedirs('filtered')

# Create Log File
sample_dictionary = dict()
organism_database = []


# http://atacama.qb3.berkeley.edu/auto/sahara/namib/home/ryanhsu/bin/pear

def filterFastQ(assembledFile):
	def getSequences(FASTQfile):
		tempFile = open(ASSEMBLED_DIRECTORY + FASTQfile).read().split('\n')
		sequences = []
		lineNum = 0
		for line in tempFile:
			if lineNum == 1:
				sequences.append(line)
			lineNum += 1
			if lineNum == 4:
				lineNum = 0
		return sequences

	conditionName = assembledFile.split(".")[0]
	newFileName = conditionName + "." + "filtered.fasta"

	seqs = getSequences(assembledFile)
	filteredFastQ = ""
	for seqNum in range(len(seqs)):
		seq = seqs[seqNum]
		if len(seq) > MIN_LENGTH:
			fphasingIndex = seq.find(F_ANNEALING_REGION, 0, 36)
			rphasingIndex = seq.find(R_ANNEALING_REGION, len(seq)-36, len(seq))
			print rphasingIndex
			if fphasingIndex >= 0 and rphasingIndex > 0:
				filteredSeq = seq[fphasingIndex:rphasingIndex+len(R_ANNEALING_REGION)]
				filteredFastQ += ">Sequence" + str(seqNum) + '\n' + filteredSeq + '\n'
	open(FILTERED_DIRECTORY + newFileName, 'w').write(filteredFastQ)
	

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
			"-maxhits", "32",
	        "-maxaccepts", "1",
	        "-maxrejects", "32",
			'-id', '.975']

	process = subprocess.Popen(args, stdout=subprocess.PIPE)

	# for line in iter(process.stdout.readline, ''):
	# 	sys.stdout.write(line)

	process.wait()

def findAssembledFASTQ(directoryList):
	assembledFiles = []
	for f in directoryList:
		if f.split('.')[-2] == 'assembled' and f.split('.')[-1] == 'fastq':
			assembledFiles.append(f)
	return sorted(assembledFiles)

def findFilteredFASTA(directoryList):
	filteredFiles = []
	for f in directoryList:
		if f.split('.')[-2] == 'filtered' and f.split('.')[-1] == 'fasta':
			filteredFiles.append(f)
	return sorted(filteredFiles)

def saveTallyHMB():
	jsonOutput = json.dumps(sample_dictionary)
	print 'Saving ' + TALLY_HMB
	open(TALLY_HMB, 'w').write(jsonOutput)

def saveTallyText():
	tallyText = 'sampleWell'
	for org in organism_database:
		tallyText += '\t' + org

	plateSet = 'HMB'
	for platenum in range(1,MAX_PLATE_ID):
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

def saveReport():
	reportText = 'sample\tReads\tOrganisms Over 5%'

	plateSet = 'HMB'
	for platenum in range(1,MAX_PLATE_ID):
		for letter in 'ABCDEFGH':
			for column in range(1,13):
				sampleID = argsToSampleID(plateSet, platenum, letter, column)
				if sampleID in sample_dictionary:
					reportText += '\n'
					reportText += sampleID

					totalReads = 0
					for org in organism_database:
						totalReads += sample_dictionary[sampleID][org]
					reportText += '\t' + str(totalReads)

					threshold = 0.05*totalReads

					for org in organism_database:
						if sample_dictionary[sampleID][org] > threshold:
							reportText += '\t' + org


	print 'Saving ' + REPORT_TXT
	open(REPORT_TXT, 'w').write(reportText)

def argsToSampleID(plateSet, plate, letter, column):
	return plateSet+"%02d"%(plate,)+letter+"%02d"%(column)

def main():
	global organism_database
	organism_database = getAllOrganisms(HMB_DATABASE)
	getAllOrganisms(HMB_DATABASE)
	directoryListing = listdir(os.path.dirname(os.path.abspath(__file__)) + '/' + ASSEMBLED_DIRECTORY)
	fastQs = findAssembledFASTQ(directoryListing)

	for fqIndex in range(len(fastQs)):
		print "Filtering " + str(fastQs[fqIndex]) + '\t' + str(100.0*fqIndex/len(fastQs)) + '%' 
		filterFastQ(fastQs[fqIndex])

	directoryListing = listdir(os.path.dirname(os.path.abspath(__file__)) + '/' + FILTERED_DIRECTORY)
	filteredFASTAs = findFilteredFASTA(directoryListing)

	for i in range(len(filteredFASTAs)):
		f = filteredFASTAs[i]
		sample_name = f[:8]
		print '\n' + time.strftime('%c') + '\n'
		print 'PROGRESS: ' + str(i+1) + '/' + str(len(filteredFASTAs)) + '   ' + str((100.0*i)/len(filteredFASTAs)) + '%'
		print 'Running USEARCH on ' + f
		usearch(FILTERED_DIRECTORY + '/' + f)
		print 'Tallying ' + f
		tally(sample_name)
	# print sample_dictionary['HMB01A01']
	saveTallyText()
	saveTallyHMB()
	saveReport()

main()
