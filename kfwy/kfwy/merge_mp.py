# Name: Tiffany Nguyen
# Date: 1.8.19
# File: merge_mp.py

# Note: Using Python 2.7

# 1) Place the analyzed data files (.xlsx) to be merged in a folder with this Python script.
# 2) Open the command line
# 3) Navigate to the folder 
#	  e.g. if folder path is users/data, then type the command "cd users/data" without quotations
# 4) Type command "python merge_mp.py" without quotations to run

import xlrd
import os
import glob
import pandas as pd
import math

def main():
	root = os.getcwd()
	path = root + '\*.xlsx'
	files = glob.glob(path)  

	# Creates output folder called "Merge"
	output_dir = root +'\Merge'
	if (os.path.isdir(output_dir) == False):
		os.makedirs('Merge')

	writer = pd.ExcelWriter('Merge.xlsx')
	dfs = {}
	mergedfs = {}

	print("Analyzing data...")

	# Loops through each excel file
	for name in files:

		# Saves each worksheet in the file as a dataframe
		filename = name.split('\\')[-1]
		filename = filename.split('.')[0]
		filename = filename.decode("ascii", errors="ignore").encode()
		xl = pd.ExcelFile(name)
		dfs[filename] = xl.parse("Averaged Standard Curve")

	# Loops through each dataframe
	for df in dfs:

		# Merges dataframes and normalizes each column's 
		for column_name in dfs[df].columns:
			normalized_col_name = column_name.split(".")[0]
			if normalized_col_name in mergedfs:
				(mergedfs[normalized_col_name])[df] = (dfs[df])[column_name]
			else:
				mergedfs[normalized_col_name] = pd.DataFrame()
				(mergedfs[normalized_col_name])[df] = (dfs[df])[column_name]

	# Produces Mean and SEM across rows in merged dataframes
	for df in mergedfs:
		x = len(mergedfs[df].columns)
		(mergedfs[df])['Mean'] = mergedfs[df].mean(axis=1)
		(mergedfs[df])['SEM'] = (mergedfs[df].drop('Mean', axis=1).std(axis=1)).div(math.sqrt(x))

	os.chdir(output_dir)

	# Exports merged dataframes to excel
	for df in mergedfs:
		mergedfs[df].to_excel(writer, df.replace('/','_'))

	# Saves excel file
	writer.save()
	print('Analysis complete')