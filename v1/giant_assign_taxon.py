#usage: python giant_assign_taxon.py file.fastq database.fa
#by ryan hsu

import os
from os import listdir
from sys import argv

splitFQdirectory = 'splitFQs/'
splitATdirectory = 'splitAssignTaxon/'

if not os.path.exists(splitFQdirectory):
	os.makedirs(splitFQdirectory)

originalFASTQ = argv[1]

os.system('split -l 400000 '+ originalFASTQ + ' ' + splitFQdirectory + 'miniFQ_')

if not os.path.exists(splitATdirectory):
	os.makedirs(splitATdirectory)

directoryListing = listdir('splitFQs')
directoryListing.sort()
database = argv[2]

for splitFQ in directoryListing:
	print splitFQ
	os.system('python2.7 assign_taxon.py -p 10 ' + '-o ' + splitATdirectory + splitFQ+'taxon/ ' + '-m ' + splitFQdirectory + '/' + splitFQ + ' ' + database)

print('\n\n Merging Assign_taxon outputs')

giantATtxt = ''
giantAT = open('giant_assigned_taxa.txt', 'w')

for folder in listdir(splitATdirectory):
	print('Combining ' + folder)
	giantATtxt += open(splitATdirectory + '/' + folder + '/assigned_taxa.txt').read()
giantAT.write(giantATtxt)

print('DONE!')
