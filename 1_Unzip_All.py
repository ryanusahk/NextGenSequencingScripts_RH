from os import listdir
import os
import gzip

directoryListing = listdir(os.path.dirname(os.path.abspath(__file__)))

zippedFiles = []
for f in directoryListing:
	if f.split('.')[len(f.split('.'))-1] == 'gz':
		zippedFiles.append(f)
		print 'Found ' + f
print "Unzipping " + str(len(zippedFiles)) + " files."

response = raw_input('Continue? y/n: ')
if response is 'y':
	for zipped in zippedFiles:
		unzipped = gzip.open(f)
		writeFile = open(zipped[:-3], 'w')
		writeFile.write(unzipped.read())
		writeFile.close()
		print 'Unzipped ' + zipped[:-3]
else:
	print 'quitting'
	exit()