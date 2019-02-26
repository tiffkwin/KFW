# Name: Tiffany Nguyen
# Date: 8.27.18
# File: NADHRedox.py (kfwx)

# Note: Using Python 2.7

# 1) Place the raw data files (.txt) to be analyzed in a folder with this Python script.
# 2) Open the command line
# 3) Navigate to the folder 
#	  e.g. if folder path is users/data_analysis, then type the command "cd users/data_analysis" without quotations
# 4) Type command "python NADHRedox.py" without quotations to run

import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn-darkgrid')
import seaborn as sns
import scipy.stats as stats
import glob
import os
import datetime
from sys import platform

# Global constants (CHANGE IF NEEDED)
TIME_PERIOD = 180 # length of trial in seconds
NUM_PERIODS = 8 # number of additions in one trial
sub_list = ['Pyr/M','G/M','Pc/M','S/R','AKG','P/G/M/S/O','Oct/M','Ac/M','KIC/M','KIC', 'KIV', 'KMV','KIV/M','KIV/Oct','KMV/M','KMV/Oct','Pyr/C','Oct/C','Pc/C','Ac/C','Glut', 'None'] # list of available substrates
add_list = ['Buffer', 'Mito', 'Substrate', 'PCR', 'Drug', 'Vehicle', 'FCCP', 'Oligo', 'Rot', 'Ant A', 'AF', 'BCNU', 'CN', 'Ala', 'Other'] # list of available additions

# Global variables (DO NOT CHANGE)
substrates = [] # list that contains the substrates used in experiment
ID = '' # the experiment id
s_num = [] # list that keeps track of substrate repetitions
additions = [] # list that contains the additions used in experiment
groups = [] # list containing groups descriptions

# FUNCTION: Retrieves input from the user
# RETURNS: Nothing
def get_input():
	global ID
	global substrates
	global NUM_PERIODS
	global additions
	global groups

	for x in sub_list:
		s_num.append(0)

	print('\nDATA ANALYSIS')
	print('-----------------------------------------------')

	# Retrieves experiment id from user
	ID = raw_input('Enter the ID: ')

	# Retrieves groups from user
	while True:
		try:
			NUM_GROUPS = int(raw_input('How many groups are there? (1-4) '))
			for i in range(0,NUM_GROUPS):
				group_description = raw_input('Description for Group ' + str(i + 1) + ': ')
				groups.append('G' + str(i+1) + ': ' + group_description)
			break
		except ValueError:
			print('\n[Error]: Please enter a valid number.\n')

	# Retrieves num substrates from user
	while True:	
		try:
			NUM_SUBSTRATES = int(raw_input('How many substrates will you be testing? '))
			break
		except ValueError:
			print('\n[Error]: Please enter a valid number.\n')

	# Retrieves list of substrates used in experiment from user
	print('\nSubstrate List:')
	for i in range(len(sub_list)):
		print('\t{}) {}'.format(i+1, sub_list[i]))
	print('To select a substrate, enter the number it corresponds with in the list.\n\n[Example] When selecting Pyr/M\n> Select substrate: 1')
	print('-----------------------------------------------')
	while True:
		try:
			for i in range(NUM_SUBSTRATES):
				sub_num = int(raw_input('Select substrate ' + str(i + 1) + ': ')) - 1
				group_num = int(raw_input('Select group number (1-4): '))
				substrates.append(sub_list[sub_num] + '_G' + str(group_num))
				#if s_num[sub_num] > 0:
				#	substrates.append(sub_list[sub_num] + '.' + str(s_num[sub_num]))
				#else:
				#	substrates.append(sub_list[sub_num])
				#s_num[sub_num] += 1
			break
		except Exception:
			print('\n[Error]: Please start over and enter a valid number for each selection.\n')
			substrates = []
	
	# Retrieves num additions from user
	while True:	
		try:
			NUM_ADDITIONS = int(raw_input('\nHow many additions will you be making? '))
			NUM_PERIODS = NUM_ADDITIONS
			break
		except ValueError:
			print('\n[Error]: Please enter a valid number.\n')

	# Retrieves list of additions used in experiment from user
	print('\nAddition List:')
	for i in range(len(add_list)):
		print('\t{}) {}'.format(i+1, add_list[i]))
	print('To select an addition, enter the number it corresponds with in the list.\n\n[Example] When selecting Buffer\n> Select addition: 1')
	print('-----------------------------------------------')
	while True:
		try:
			for i in range(NUM_ADDITIONS):
				add_num = int(raw_input('Select addition ' + str(i + 1) + ': ')) - 1
				additions.append(add_list[add_num])
			break
		except Exception:
			print('\n[Error]: Please start over and enter a valid number for each selection.\n')
			additions = []

# FUNCTION: Strips the non-NADH runs from the dataframe
# RETURNS: The stripped dataframe
def strip(fluor):

	stripped = pd.DataFrame()
	for column in fluor[fluor.columns[::6]]:
		stripped = pd.concat([stripped, fluor[column]], axis=1)
		stripped =  pd.concat([stripped, fluor[column+1]], axis=1)

	return stripped

# FUNCTION: Reduces the y values using the eqn: y = (y-min)/(max-min)*100
# RETURNS: The reduced dataframe
def reduce(fluor, avg_stripped):
	newdf = fluor.copy()
	col = 0
	for column in newdf[newdf.columns[::2]]:
		#max_y = avg_stripped[substrates[col]].iloc[-2]
		min_y = avg_stripped[substrates[col]].iloc[-1]
		for j in range(0,newdf.apply(pd.Series.last_valid_index)[column] + 1):
			y = newdf[column+1][j]
			val = y-min_y
			newdf.at[j,column+1] = val
		col += 1	

	return newdf

# FUNCTION: Produces an average for all the data points within a time period
# RETURNS: The dataframe containing the averagesperiod
def averages(fluor):

	cnum_avg = 0 # Column num in 'averages' dataframe

	# Creates empty dataframe to store averages in
	avg_stdcurve = pd.DataFrame(columns=substrates)

	
	# Iterrates through every other column in the dataframe
	for column in fluor[fluor.columns[::2]]:

		period = 0 # Counter that tracks the period
		fluorsum = 0 # The running sum of fluorescence values to be averaged
		k = 0 # Number of data points being averaged

		# Creates numpy array to store averages in
		averages = np.array([])

		rnum = 0 # Tracks the row index
		last_row = fluor.apply(pd.Series.last_valid_index)[column] # Finds index of last row in the column that does not have a null value

		# Iterrates through each item in the column
		for j in fluor[column]:

			start = TIME_PERIOD * period # Starting cutoff time for substrate addition
			end = TIME_PERIOD * (period+1) # Ending cutoff time for substrate addition

			if(period != NUM_PERIODS-1):

				# If the time given by the x-value, j, is within the period for substrate addition
				if j > (start+10) and j < (end-10):

					# Add the y-value to the running sum
					fluorsum += fluor[column+1][rnum]

					# Increment the amount of data points being averaged
					k += 1

				# If the time given by the x-value surpasses the ending cutoff time for substrate addition
				elif (j > (end-10)):

					# Calculate the average and store it in the numpy array
					avg = fluorsum/k
					averages = np.append(averages, avg)

					# Reset the number of data points being averaged to 0
					k = 0

					# Increment the substrate number by 1
					period += 1

					# Reset the running sum to 0
					fluorsum=0

			else:
				if j > (start+10):

					# Add the y-value to the running sum
					fluorsum += fluor[column+1][rnum]

					# Increment the amount of data points being averaged
					k += 1

				# If the time given by the x-value surpasses the ending cutoff time for substrate addition
				if (rnum == last_row):

					# Calculate the average and store it in the numpy array
					avg = fluorsum/k
					averages = np.append(averages, avg)

					# Reset the number of data points being averaged to 0
					k = 0

					# Increment the substrate number by 1
					period += 1

					# Reset the running sum to 0
					fluorsum=0


			# Increment the row number by 1
			rnum += 1

		# Create a pandas series using the numpy array, averages, and append it to the dataframe
		# that stores the averages, avg_stdcurve
		avg_stdcurve[substrates[cnum_avg]] = pd.Series(averages)

		# Increment the column number by 1
		cnum_avg += 1
	
	#print(avg_stdcurve) #debug
	#print(fluor) #debug

	return avg_stdcurve

# FUNCTION: Produces a dataframe containing the metadata for the experiments
# RETURNS: The dataframe containing the metadata
def prod_metadata():
	# Prints metadata to dataframe
	metadata = pd.DataFrame(columns=['ID','Groups', 'Substrates', 'Additions', 'Date'])
	metadata.at[0, 'ID'] = ID
	for i in range(0, len(groups)):
		metadata.at[i, 'Groups'] = groups[i]
	for i in range(len(substrates)):
		metadata.at[i, 'Substrates'] = substrates[i]
	for i in range(len(additions)):
		metadata.at[i, 'Additions'] = additions[i]
	now = datetime.datetime.now()
	metadata.at[0,'Date'] = now.strftime("%Y-%m-%d")

	return metadata

# FUNCTION: Plots a dataframe with an X Y X Y X Y... structure of columns and saves the figure
# RETURNS: Nothing
def plot1(df, plot_name, file_name):
	x_col = df[0]
	run = 1
	for i in range(0, len(df.columns)):
		if i % 2 == 0:
			x_col = df[i]
		else:
			plt.plot(x_col, df[i], label='Run ' + str(run))
			run += 1
	plt.legend(loc='best')
	plt.title(plot_name)
	plt.savefig(file_name)
	plt.clf()

# FUNCTION: Plots a dataframe with an S1 S2 S3... structure of columns and saves the figure
# RETURNS: Nothing
def plot2(df, plot_name, file_name):
	df.plot()
	plt.title(plot_name)
	plt.savefig(file_name)
	plt.clf()

# FUNCTION: Executes the data analysis process
# RETURNS: Nothing
def main():
	mac = True
	if platform == "win32":
		mac = False

	get_input()
	print('-----------------------------------------------')
	print("Loading...")

	# Retrieves all .txt files in the current working directory
	root = os.getcwd()
	if mac:
		path = root + '/*.txt'
	else:
		path = root + '\*.txt'

	files = glob.glob(path)   

	file_num = 1

	if mac:
		if (os.path.isdir(root + '/output') == False):
			os.makedirs('output')
	else:
		if (os.path.isdir(root + '\output') == False):
			os.makedirs('output')

	# Loops through every .txt file found
	for name in files:
		print('Analyzing file ' + str(file_num) + '...')

		if mac:
			# Stores file name
			filename = name.split('/')[-1]
		else:
			filename = name.split('\\')[-1]

		# Removes file type from filename
		shortened_filename = filename.split('.')[0]

		if mac:
			output_dir = root +'/output/' + shortened_filename
		else:
			output_dir = root +'\output\\' + shortened_filename

		if (os.path.isdir(output_dir) == False):
			if mac:
				os.chdir(root + '/output')
			else:
				os.chdir(root + '\output')
			os.makedirs(shortened_filename)
			os.chdir(root)

		# Creates .xlsx file to output analyzed data to
		writer = pd.ExcelWriter(shortened_filename + '.xlsx')

		# ----DATA READ-IN----

		#print(filename) #debug

		# Reads in the data from the csv and stores it as a dataframe
		fluor_raw = pd.read_csv(filename, sep='\t', skiprows=6, skipfooter=1, header=None, engine='python')

		os.chdir(output_dir)

		# Plot raw data
		plot1(fluor_raw, 'Raw Data', 'Raw.png')

		# Produces metadata
		metadata = prod_metadata()

		# Exports metadata to .xlsx file
		metadata.to_excel(writer, ('Metadata'))

		# Gets column labels
		column_labels = []
		for i in range(0,len(fluor_raw.columns)):
			if(i % 2 == 0):
				column_labels.append('X')
			else:
				column_labels.append('Y')

		# ----EXPORT TO EXCEL - RAW DATA----

		fluor = fluor_raw.copy()
		fluor_raw.columns = column_labels
		fluor_raw.to_excel(writer, ('Raw Data'))

		# ----STRIP - RAW DATA----

		fluor = strip(fluor)

		# ----EXPORT TO EXCEL - STRIPPED DATA----
		fluor.columns = list(range(0,len(fluor.columns)))

		fluor.to_excel(writer, ('Stripped Data'))

		# Plot stripped data
		plot1(fluor, 'Stripped Data', 'Stripped.png')

		avg_stripped = fluor.copy()
		avg_stripped = averages(avg_stripped)

		# ----REDUCTION - STRIPPED DATA----
		
		fluor = reduce(fluor, avg_stripped)

		# ----EXPORT TO EXCEL - REDUCED DATA----

		fluor.to_excel(writer, ('Reduced Data'))

		# Plot reduced data
		plot1(fluor, 'Reduced Data', 'Reduced.png')

		# ----AVERAGES - REDUCED DATA----

		avg = averages(fluor)

		# Plot averaged reduced data
		plot2(avg, 'Averaged Reduced Data', 'Avg_Reduced.png')

		# ----EXPORT TO EXCEL - AVG REDUCED DATA----

		avg.to_excel(writer, ('Averaged Reduced Data'))

		# Saves excel file and moves on to next file to be analyzed if there is one
		writer.save()
		file_num += 1
		os.chdir(root)

	print('Analysis complete')
	print('-----------------------------------------------')

# Executes main()
#main()
