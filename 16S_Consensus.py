from Bio import pairwise2
import time
from multiprocessing import Pool
from sys import argv
from os import listdir
import os
from time import gmtime, strftime
import datetime
import numpy as np 
from scipy import stats

# 5'->3'
F_PRIMER = "ACTCCTACGGGAGGCAGCAGTG"

# 5'->3' Reverse-Compliment
R_PRIMER = "AACAGGATTAGATACCCTGGTAGTCC"

def findMergedFastQs():
	directoryListing = listdir(os.path.dirname(os.path.abspath(__file__)))
	mergedFiles = []
	for f in directoryListing:
		fileNameSplit = f.split('.')
		if fileNameSplit[-1] == 'fastq':
			mergedFiles.append(f)
	return mergedFiles

def getSequences(FASTQfile):
	tempFile = open(FASTQfile).read().split('\n')
	sequences = []
	lineNum = 0
	for line in tempFile:
		if lineNum == 1:
			sequences.append(line)
		lineNum += 1
		if lineNum == 4:
			lineNum = 0
	return sequences

def filterByLength(sequences):

	def defineLengths(sequences):
		lengths = []
		for seq in sequences:
			lengths.append(len(seq))
		lengths = np.array(lengths)
		return stats.mode(lengths)

	mode = defineLengths(sequences)[0][0]
	filtered = []
	for seq in sequences:
		if len(seq) == mode:
			filtered.append(seq)
	return filtered

def filterByPrimers(sequences):
	filtered = []
	for seq in sequences:
		if seq.find(F_PRIMER) > -1 and seq.find(R_PRIMER) > -1:
			filtered.append(seq[seq.find(F_PRIMER):seq.find(R_PRIMER) + len(R_PRIMER)])
	return filtered

def findBestBase(sequences, index):
	#ATCG
	total = len(sequences)
	counts = {'A':0, 'T':0, 'C':0, 'G':0}
	for seq in sequences:
		if seq[index] in 'ACTG':
			counts[seq[index]] += 1

	countArray = np.array([counts['A'], counts['T'], counts['C'], counts['G']])
	maxCount = np.max(countArray)

	for base in counts:
		if counts[base] == maxCount:
			message = ''
			if 100.0*maxCount / total < 90.0:
				message += str(100.0*maxCount / total)[:5] + "% confidence at position " + str(index)
			# print base + extraMessage
			return base, message

def main():
	allConsensii = []
	fastQs = sorted(findMergedFastQs())

	for fq in fastQs:
		sequences = getSequences(fq)
		primerFiltered = filterByPrimers(sequences)
		sizeFiltered = filterByLength(primerFiltered)

		consensus = ''
		name = fq.split('.')[0] + '_c'
		for i in range(len(sizeFiltered[0])):
			base, message = findBestBase(sizeFiltered, i)

			if len(message) > 0:
				print fq.split('.')[0] + ' ' + message
			consensus += base


		allConsensii.append((name, consensus, len(sizeFiltered)))

	outFile = ''
	for pair in allConsensii:
		outFile += '>' + pair[0] + '\n' + pair[1] + '\n'
		print pair[0] + '\tfrom ' + str(pair[2]) + ' filtered sequences'
		print pair[1] + '\n'
	open('consensus.fasta', 'w').write(outFile)


main()










