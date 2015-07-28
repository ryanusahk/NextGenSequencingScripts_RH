#GG genomic TITRATIONS

###
outputFileName = 'GG_genomic_titrations.csv'

from os import listdir
import os
import csv
import sys
import time
from multiprocessing.pool import ThreadPool


def findMergedFastQs():
	directoryListing = listdir(os.path.dirname(os.path.abspath(__file__)))

	mergedFiles = []
	for f in directoryListing:
		fileNameSplit = f.split('.')
		if fileNameSplit[-1] == 'fastq' and fileNameSplit[1] == 'assembled':
			mergedFiles.append(f)
			# print 'Found ' + f
	# print "Found " + str(len(mergedFiles)) + " merged files."
	return mergedFiles

def getSequences(FASTQfile):
	if FASTQfile.split('.')[-1] != 'fastq':
		print "NOT A FASTQ FILE"
		return
	else:
		tempFile = open(FASTQfile).read().split('\n')

		sequences = []
		prevAt = False
		for line in tempFile:
			if prevAt:
				sequences.append(line)
				prevAt = False
			if len(line) > 3 and line[0] == '@':
				prevAt = True
		return sequences

def filterBySize(listOfSeqs, size=480):
	correctSeqs = []

	GCGGcount = 0

	for seq in listOfSeqs:
		if len(seq) > (size - 3) and len(seq) < (size + 3):
			correctSeqs.append(seq)

			if seq[-3:] == 'GCG':
				GCGGcount += 1

	print GCGGcount
	return correctSeqs

def barcodeByEndRegions(listOfSeqs):
	allBarcodes = []
	for seq in listOfSeqs:
		if seq.find('CTGGTAGTCC') and seq[seq.rfind('CTGGTAGTCC'):]:
			endOfAnneal = seq.rfind('CTGGTAGTCC') + len('CTGGTAGTCC')
			scarIndex = seq.rfind('GCG')
			rb = seq[endOfAnneal:scarIndex]


			if len(rb) == 15 and endOfAnneal > 300 \
			 and scarIndex - endOfAnneal == 15 and rb.find('N') == -1:
				allBarcodes.append(rb)
	return allBarcodes

def countUniqueBarcodes(listOfBarcodes):
	counter = dict()
	for bc in listOfBarcodes:
		if bc in counter:
			counter[bc] += 1
		else:
			counter[bc] = 1
	return counter

def nucleotideContent(listOfSeqs):
	CGs = 0
	ATs = 0
	for seq in listOfSeqs:
		for char in seq:
			if char == 'C' or char == 'G':
				CGs += 1
			if char == 'A' or char == 'T':
				ATs += 1
	return (CGs, ATs)

def makeDatapoint(name, numAssembled, numFilteredSize, numBarcodes, GC, AT, numUniqueRB):
	return [name, numAssembled, numFilteredSize, numBarcodes, GC, AT, numUniqueRB]

def analyze(files):
	arrayOfDatapoints = []
	for fastq in files:
		print 'analyzed ' + fastq
		name = fastq.split('.')[0]
		currFile = fastq
		sequences = getSequences(currFile)
		sized480 = filterBySize(sequences, sizeFilter)
		barcodes = barcodeByEndRegions(sized480)
		UniqueRBs = countUniqueBarcodes(barcodes)

		(GC, AT) = nucleotideContent(barcodes)

		arrayOfDatapoints.append(makeDatapoint(name, len(sequences), 
			len(sized480), len(barcodes), GC, AT, len(UniqueRBs)))
	return arrayOfDatapoints

def analyzeSingle(sFile):
	# print 'started ' + sFile
	name = sFile.split('.')[0]
	currFile = sFile
	sequences = getSequences(currFile)
	sized480 = filterBySize(sequences, sizeFilter)
	barcodes = barcodeByEndRegions(sized480)

	UniqueRBs = countUniqueBarcodes(barcodes)


	# for bc in UniqueRBs:
	# 	if UniqueRBs[bc] > 1:
	# 		print bc

	(GC, AT) = nucleotideContent(barcodes)
	# print 'finished ' + sFile
	return makeDatapoint(name, len(sequences), 
		len(sized480), len(barcodes), GC, AT, len(UniqueRBs))

# results = analyze(files)

# for line in results:
# 	print line

# arrayOfDatapoints = []
# pool = ThreadPool(4)
# pool.map(analyzeSingle, files)

# arrayOfDatapoints.sort()

def timeAnalyze(threads):
	tic = time.clock()
	pool = ThreadPool(threads)
	datapoints = pool.map(analyzeSingle, files)
	toc = time.clock()
	return 'Threads: ' + str(threads) + ' | Time: ' + str(toc-tic) + 'sec.'  

times = []
# print 'times.append(timeAnalyze(2))'
# times.append(timeAnalyze(2))

files = findMergedFastQs()
files.sort()
sizeFilter = int(sys.argv[1])

tic = time.clock()
datapoints = [['name', 'numSequences', 'numSizeFiltered', 'numBarcodes', 'GC', 'AT', 'UniqueRBs']]

totalFiles = len(files)
count = 0
for merged in files:


	datapoints.append(analyzeSingle(merged))
	count += 1

	print str((100 * count) / totalFiles) + '%'


for line in datapoints:
	print line
toc = time.clock()
print str(toc - tic)

with open(outputFileName, "wb") as f:
    writer = csv.writer(f)
    writer.writerows(datapoints)

