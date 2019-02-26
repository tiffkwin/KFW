# Name: Tiffany Nguyen
# Date: 8.20.18
# File: membrane_potential.py (kfwx)

# Note: Using Python 2.7

# 1) Place the raw data files (.txt) to be analyzed in a folder with this Python script.
# 2) Open the command line
# 3) Navigate to the folder 
#	  e.g. if folder path is users/data_analysis, then type the command "cd users/data_analysis" without quotations
# 4) Type command "python membrane_potential.py" without quotations to run

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
SLOPE = 0.0
Y_INT = 0.0
substrates = [] # list that contains the substrates used in experiment
ID = '' # the experiment id
s_num = [] # list that keeps track of substrate repetitions
additions = [] # list that contains the additions used in experiment
groups = [] # list containing group descriptions

# FUNCTION: Retrieves input from the user
# RETURNS: A boolean where True indicates use of the standard curve
def get_input():
	global ID
	global SLOPE
	global Y_INT
	global substrates
	global additions
	global NUM_PERIODS
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
	print('Enter x to start over.')
	print('-----------------------------------------------')
	while True:
		try:
			for i in range(0,NUM_SUBSTRATES):
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

	# Prompts user for standard curve
	stdcurve = raw_input('\nWill you be using the standard curve? [y/n]: ').lower() == 'y'

	# Retrieves slope and y-intercept from user if standard curve is being used
	while True:
		try:
			if(stdcurve):
				SLOPE = float(raw_input('\tEnter the slope: '))
				Y_INT = float(raw_input('\tEnter the y-intercept: '))
			break
		except ValueError:
			print('\n[Error]: Please start over and enter a valid number for each value.\n')

	# Returns a boolean indicating whether or not the standard curve is being used
	return stdcurve

# FUNCTION: Adjusts the y-values using the standard curve calculation
# RETURNS: The adjusted dataframe
def std_curve(fluor):

	# Iterrates through every row in the dataframe
	for index, row in fluor.iterrows():
		
		column = 1 # Counter that tracks the indices of columns containing y-values

		# Iterrates through every column containing y-values in the row
		while column < len(fluor.columns):

			# Retrieves the y value from df[column][row]
			y = row[column]

			# Converts the fluorescence value to membrane potential 
			fluor.at[index, column] = (y - Y_INT)/SLOPE

			# Increments the column counter
			column += 2

	return fluor

# FUNCTION: Produces an average for all the data points within a time period
# RETURNS: The dataframe containing the averages
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

# FUNCTION: Divides all the averages by the average for Ala to produce a corrected dataset
# RETURNS: The Ala corrected dataframe
def corrected(avg_raw):

	for column in avg_raw:

		rnum = 0
		ala_avg = avg_raw[column][avg_raw.apply(pd.Series.last_valid_index)[column]]

		for j in avg_raw[column]:
			avg_raw.at[rnum, column] = j-ala_avg
			rnum += 1

	return avg_raw

# FUNCTION: Produces a dataframe containing the metadata for the experiments
# RETURNS: The dataframe containing the metadata
def prod_metadata(bool_stdcurve):
	metadata = pd.DataFrame(columns=['ID','Standard Curve','Slope','Y-Intercept','Groups', 'Substrates', 'Additions', 'Date'])
	metadata.at[0, 'ID'] = ID
	metadata.at[0, 'Standard Curve'] = bool_stdcurve
	metadata.at[0, 'Slope'] = SLOPE
	metadata.at[0, 'Y-Intercept'] = Y_INT
	for i in range(0, len(groups)):
		metadata.at[i, 'Groups'] = groups[i]
	for i in range(0,len(substrates)):
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

	bool_stdcurve = get_input()
	#print(bool_stdcurve)
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

		#print(filename) #uncomment this line for debugging

		# Reads in the data from the csv and stores it as a dataframe
		fluor_raw = pd.read_csv(filename, sep='\t', skiprows=6, skipfooter=1, header=None, engine='python')

		os.chdir(output_dir)

		# Plot raw data
		plot1(fluor_raw, 'Raw Data', 'Raw.png')

		# Produces metadata
		metadata = prod_metadata(bool_stdcurve)

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

		# ----AVERAGES - RAW DATA----

		avg_raw = averages(fluor)

		# Plots averaged raw data
		plot2(avg_raw, 'Averaged Raw Data', 'Avg_Raw.png')

		# ----EXPORT TO EXCEL - AVG RAW DATA----

		avg_raw.to_excel(writer, ('Averaged Raw Data'))

		# Performs correction calculation
		corrected_raw = corrected(avg_raw)

		# Plots corrected data
		plot2(corrected_raw, 'Corrected Data', 'Corrected.png')

		# ----MEMBRANE POTENTIAL STANDARD CURVE----
		if(bool_stdcurve):
			fluor = std_curve(fluor)

			# Plots standard curve data
			plot1(fluor, 'Standard Curve Data', 'Standard_Curve.png')

		# ----AVERAGES - STANDARD CURVE----

			avg_stdcurve = averages(fluor)

			# Plots averaged standard curve data
			plot2(avg_stdcurve, 'Averaged Standard Curve Data', 'Avg_Standard_Curve.png')

		# ----EXPORT TO EXCEL - CORRECTED RAW DATA---

		# Set column labels
		fluor.columns = column_labels

		corrected_raw.to_excel(writer,('Corrected Raw Data'))

		# ----EXPORT TO EXCEL - STANDARD CURVE / AVERAGED STANDARD CURVE DATA---

		if(bool_stdcurve):
			fluor.to_excel(writer,('Standard Curve'))
			avg_stdcurve.to_excel(writer,('Averaged Standard Curve'))

		# Saves excel file and moves on to next file to be analyzed if there is one
		writer.save()
		file_num += 1
		os.chdir(root)

	print('Analysis complete')
	print('-----------------------------------------------')

# Executes main()
#main()
