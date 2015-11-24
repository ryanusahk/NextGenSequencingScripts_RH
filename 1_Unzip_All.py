from os import listdir
import os
import gzip

directoryListing = listdir(os.path.dirname(os.path.abspath(__file__)))

directory = 'Unzipped_Indicies'
if not os.path.exists(directory):
	print 'Created ' + directory + ' directory.'
	os.makedirs(directory)

zippedFiles = []
for f in directoryListing:
	if f.split('.')[len(f.split('.'))-1] == 'gz':
		zippedFiles.append(f)
		print 'Found ' + f
print "Unzipping " + str(len(zippedFiles)) + " files."

response = raw_input('Continue? y/n: ')
if response is 'y':
	for zipped in zippedFiles:
		print 'Starting ' + zipped
		unzipped = gzip.open(zipped)
		print 'Opened ' + zipped
		# writeFile = open(directory + '/' + zipped[:-3], 'w')
		# writeFile.write(unzipped.read())
		# writeFile.close()
		
		print 'Unzipped ' + zipped[:-3]
		print '\n'
else:
	print 'quitting'
	exit()