#usage: python convertFullTally.py unfulltally.txt
#by ryan hsu

import os
from os import listdir
from sys import argv

fullKey = "sample	e.coli	BH10507	CA25986	BU6597	PC	BO	BV1447	BT	EL25559	FP17677	CH13275	DP	ER	MF".split('\t')
newTally = "sample	e.coli	BH10507	CA25986	BU6597	PC	BO	BV1447	BT	EL25559	FP17677	CH13275	DP	ER	MF\n"
tallyDictionary = dict()
for i in range(len(fullKey)):
	tallyDictionary[fullKey[i]] = i

oldTally = open(argv[1]).read().split('\n')

oldKey = oldTally[0].split('\t')

remapper = [0]*len(oldKey)

for i in range(len(oldKey)):
	remapper[i] = tallyDictionary[oldKey[i]]

for line in oldTally:
	if len(line) > 2 and line[0] is not 's':
		lineElements = line.split('\t')

		newLine = ['0']*len(fullKey)

		for i in range(len(lineElements)):
			newLine[remapper[i]] = lineElements[i]

		newString = ''
		for index in range(len(newLine)):
			newString += newLine[index]
			if index != len(newLine)-1:
				newString += '\t'
		
		newTally += newString + '\n'

nTal = open(argv[1].split('.')[0]+'c.txt', 'w')
nTal.write(newTally)
nTal.close()
