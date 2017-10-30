## Ryan Hsu 11/3/2015
## Version 1.0
from string import maketrans
import time

INDEX_BARCODES_FILE = 'hmb_rb_index_barcodes.txt'

def generateHeaderSection():
	investigator = raw_input('Investigator Name: ')
	project = raw_input('Project Name: ')
	experiment = raw_input('Experiment: ')
	date = raw_input('Date (MM/DD/YY): ')

	header = '[Header]\nIEMFileVersion,4\n' + \
	'Investigator Name,' + investigator + "\n" + \
	'Project Name,' + project + '\n' + \
	'Experiment Name,' + experiment + '\n' + \
	"""Application,FASTQ Only
Assay,TruSeqLT
Description
Chemistry,Amplicon

[Reads]
300
300

[Settings]\n\n"""
	return header

def revComp(index_sequence):
	trans_table = maketrans("ATCG", "TAGC")
	revc = ''
	for base in index_sequence:
		revc = base.translate(trans_table) + revc
	return revc

def hmbPlateToFwdIndices(plateNum, f_index_array):
	fwdGroupNum = 8 * ((plateNum - 1) / 2)
	return f_index_array[fwdGroupNum : fwdGroupNum + 8]

def hmbPlateToRevIndicies(plateNum, r_index_array):
	revGroupNum = 12*((plateNum - 1) % 2)
	revGroupNum += 24
	return r_index_array[revGroupNum : revGroupNum + 12]
	
def readIndiciesFile():
	index_file = open(INDEX_BARCODES_FILE, 'r').read().split('\n')

	f_index_array = []
	r_index_array = []

	for line in index_file:
		s = line.split('\t')
		name = s[0]
		sequence = s[1]

		if name[:3] == 'Fwd':
			f_index_array.append((name, sequence))
		elif name[:3] == 'Rev':
			r_index_array.append((name, sequence))
		else:
			'Error: Incorrect Index Barcode Reference File Format'
	return f_index_array, r_index_array

def crossPlateIndicies(plateNum):
	f_index_array, r_index_array = readIndiciesFile()
	f_seqs = hmbPlateToFwdIndices(plateNum, f_index_array)
	r_seqs = hmbPlateToRevIndicies(plateNum, r_index_array)

	sample_sheet_entries = []
	letters = "ABCDEFGH"
	for fwd_ind in range(len(f_seqs)):
		for rev_ind in range(len(r_seqs)):
			wellCol = "%02d" % (rev_ind + 1,)
			wellRow = letters[fwd_ind]
			plateID = "%02d" % (plateNum,)
			
			sampleID = 'HMB' + plateID + wellRow + wellCol

			entry = sampleID + ',,,,' + \
			r_seqs[rev_ind][0] + ',' + revComp(r_seqs[rev_ind][1]) + ',' + \
			f_seqs[fwd_ind][0] + ',' + f_seqs[fwd_ind][1] + ',,'

			sample_sheet_entries.append(entry)

	return sample_sheet_entries

def getPlateNumbers():
	print 'Which HMB plates did you use?'
	print 'Enter a plate number, then hit enter.'
	print 'When you are done entering plate numbers, enter a X'

	platesUsed = []

	response = 'lol'
	while True:
		response = raw_input("Used HMB Plate: ")
		if response == 'X' or response == 'x':
			break
		if not response.isdigit():
			print "ENTER A REAL NUMBER"
			continue
		platesUsed.append(int(response))

	print '\nGenerating Sample sheet with these plates: '
	for p in platesUsed:
		print 'HMB' + "%02d" % (p,)
	print '\n'

	return platesUsed

def generateDataSection():
	platesUsed = getPlateNumbers()

	dataSection = "[Data]\nSample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description\n"


	for plate in platesUsed:
		entries = crossPlateIndicies(plate)
		for entry in entries:
			dataSection += entry + '\n'

	return dataSection

def main():
	print "-. .-.   .-. .-.   .-. .-.   .-. .-.   .-. .-.   .-. .-.   .\n  \   \ /   \   \ /   \   \ /  \   \ /   \   \ /   \   \ /\n / \   \   / \   \   / \   \  / \   \   / \   \   / \   \\\n~   `-~ `-`   `-~ `-`   `-~ `-~   `-~ `-`   `-~ `-`   `-~ `-\nHuman Microbiome DARPA Project MiSeq Sample Sheet Generator\n"

	head = generateHeaderSection()
	data = generateDataSection()
	outputfile = head + data
	fileName = 'SampleSheet_' + str(time.time())[:-3] + '.csv'
	open(fileName, 'w').write(outputfile) 
	print 'Saved ' + fileName + '\n'
	print 'Fingers crossed for the MiSeq run!!'

main()

