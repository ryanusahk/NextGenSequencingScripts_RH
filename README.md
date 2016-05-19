#Running the HMB_Taxa Pipeline
#####This set of scripts only works with indexed primers as specified in the sample sheet generator.
#####It is also backwards compatible with the multiple versions of phasing previously used in primers.


###You will need:
* USEARCH 8.0+ installed and in your PATH
* PEAR installed and in your PATH
* Copy these files to a working directory:
  * unzip_PEAR.py
  * HMB_Taxa.py
  * HMB_Database4.fa


###Step 1 - Unzip and Merge:
Copy the raw unzipped NGS data from BaseSpace or the MiSeq into a directory named 'zipped'. The scripts are compatible with both the MiSeq file structure and BaseSpace file structure.
Call unzip_PEAR.py to unzip the files and merge the reads:
```
python unzip_PEAR.py zipped/
```
This will give you a live output of the unzipping/merging status. The outputs of this script are automatically saved into merge_report.log

The merged fasta files are outputted to a 'assembled' directory.


###Step 2 - Assign Taxa and Generate Tally File:
Run:
```
python HMB_Taxa.py assembled/ HMB_Database4.fa
```

This script will first scan through each merged file and discard improper amplicons and also trim the phasing off proper amplicons. The filtered amplicons get put into a folder 'filtered'
The script then runs USEARCH on each of the filtered files and tallies up the counts for each organism.

It outputs three files:

1. tally.txt
  * This is the human-readable tally file.
2. tally.hmb
  * This is a JSON formatted dictionary/array formatted form of the plate-counts mapping
3. report.txt
  * This report contains statistics for each well and is a quick way to check for contamination.
