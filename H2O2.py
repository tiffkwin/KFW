# Initialize# Initialize
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn-darkgrid')
import seaborn as sns
import scipy.stats as stats
#import pickle
#import sys
import glob
#import errno
import os
import datetime

# Constants
SLOPE = 0.0
Y_INT = 0.0
TIME_PERIOD = 180
NUM_PERIODS = 8
sub_list = ['Pyr/M','G/M','Pc/M','S/R','AKG','P/G/M/S/Pc','Pc/M','Ac/M','KIC/M']
substrates = []
ID = ''
s_num = [0,0,0,0,0,0,0,0,0]
MITOCHONDRIA = 0.0

# Retrieves input from the user
def get_input():
	global ID
	global SLOPE
	global Y_INT
	global substrates
	global MITOCHONDRIA
	print('\nDATA ANALYSIS')
	print('-----------------------------------------------')
	ID = input('Enter the ID: ')

	while True:	
		try:
			NUM_SUBSTRATES = int(input('How many substrates will you be testing? '))
			break
		except ValueError:
			print('\n[Error]: Please enter a valid number.\n')

	print('\nSubstrate List:\n\t1) Pyr/M\n\t2) G/M\n\t3) Pc/M\n\t4) S/R\n\t5) AKG\n\t6) P/G/M/S/Pc\n\t7) Pc/M\n\t8) Ac/M\n\t9) KIC/M\n')
	print('To select a substrate, enter the number it corresponds with in the list.\n\n[Example] When selecting Pyr/M\n> Select substrate: 1')
	print('-----------------------------------------------')

	while True:
		try:
			for i in range(0,NUM_SUBSTRATES):
				sub_num = int(input('Select substrate ' + str(i + 1) + ': ')) - 1
				if s_num[sub_num] > 0:
					substrates.append(sub_list[sub_num] + '.' + str(s_num[sub_num]))
				else:
					substrates.append(sub_list[sub_num])
				s_num[sub_num] += 1

			break
		except Exception:
			print('\n[Error]: Please start over and enter a valid number for each selection.\n')
			substrates = []

	stdcurve = input('\nWill you be using the standard curve? [y/n]: ').lower() == 'y'

	while True:
		try:
			if(stdcurve):
				SLOPE = float(input('\tEnter the slope: '))
				Y_INT = float(input('\tEnter the y-intercept: '))
			break
		except ValueError:
			print('\n[Error]: Please start over and enter a valid number for each value.\n')

	while True:	
		try:
			MITOCHONDRIA = int(input('How many milligrams of mitochondria will you be using? '))
			break
		except ValueError:
			print('\n[Error]: Please enter a valid number.\n')
		
	return stdcurve

# Adjusts the y-values using the standard curve calculation
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

# Produces an average for all the data points within a time period
def calc_slopes(fluor):

	cnum_slope = 0 # Column num in 'averages' dataframe

	# Creates empty dataframe to store averages in
	slope_df = pd.DataFrame(columns=substrates)

	# Iterrates through every other column in the dataframe
	for column in fluor[fluor.columns[::2]]:

		period = 0 # Counter that tracks the period
		x = [] # Array containing x-values of data points to be used in slope calculation
		y = [] # Array containing y-values of data points to be used in slope calculation

		# Creates numpy array to store averages in
		slopes = np.array([])

		rnum = 0 # Tracks the row index
		last_row = fluor.apply(pd.Series.last_valid_index)[column] # Finds index of last row in the column that does not have a null value

		# Iterrates through each item in the column
		for j in fluor[column]:

			start = TIME_PERIOD * period # Starting cutoff time for substrate addition
			end = TIME_PERIOD * (period+1) # Ending cutoff time for substrate addition

			if(period != NUM_PERIODS-1):

				# If the time given by the x-value, j, is within the period for substrate addition
				if j > (start+60) and j < (end-30):

					# Add the y-value to the running sum
					#fluorsum += fluor[column+1][rnum]
					x.append(fluor[column][rnum])
					y.append(fluor[column+1][rnum])

				# If the time given by the x-value surpasses the ending cutoff time for substrate addition
				elif (j > (end-30)):

					# Calculate slope and add to slopes array
					if x:
						slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
						slopes = np.append(slopes, slope)

					# Increment the substrate number by 1
					period += 1

					# Clear x and y arrays
					x = []
					y = []

			else:
				if j > (start+60):

					# Add data points to x and y arrays
					x.append(fluor[column][rnum])
					y.append(fluor[column+1][rnum])

				# If the time given by the x-value surpasses the ending cutoff time for substrate addition
				if (rnum == last_row):

					# Calculate slope and add to slopes array
					if x:
						slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
						slopes = np.append(slopes, slope)

					# Increment the substrate number by 1
					period += 1

					# Clear x and y arrays
					x = []
					y = []


			# Increment the row number by 1
			rnum += 1

		# Create a pandas series using the numpy array, averages, and append it to the dataframe
		# that stores the slopes, slope_df
		slope_df[substrates[cnum_slope]] = pd.Series(slopes)

		# Increment the column number by 1
		cnum_slope += 1

	return slope_df

# Produces a dataframe containing the metadata for the experiments
def prod_metadata():
	metadata = pd.DataFrame(columns=['ID','Standard Curve','Slope','Y-Intercept','Substrates', 'Mitochondria', 'Date'])
	metadata.at[0, 'ID'] = ID
	metadata.at[0, 'Standard Curve'] = bool_stdcurve
	metadata.at[0, 'Slope'] = SLOPE
	metadata.at[0, 'Y-Intercept'] = Y_INT
	for i in range(0,len(substrates)):
		metadata.at[i, 'Substrates'] = substrates[i]
	metadata.at[0, 'Mitochondria'] = MITOCHONDRIA
	now = datetime.datetime.now()
	metadata.at[0,'Date'] = now.strftime("%Y-%m-%d")

	return metadata

# Plots a dataframe with an X Y X Y X Y... structure of columns
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

# Plots a dataframe with an S1 S2 S3... structure of columns
def plot2(df, plot_name, file_name):
	df.plot()
	plt.title(plot_name)
	plt.savefig(file_name)
	plt.clf()

# Performs a correction calculation on the data
def corrected(df):

	for column in df:

		rnum = 0

		for j in df[column]:
			df.at[rnum, column] = j/MITOCHONDRIA
			rnum += 1

	return df

# ------------------------MAIN------------------------

bool_stdcurve = get_input()
print('-----------------------------------------------')
print("Loading...")

# Retrieves all .txt files in the current working directory
root = os.getcwd()
path = root + '/*.txt'
files = glob.glob(path)   

file_num = 1

# Loops through every .txt file found
for name in files:
	print('Analyzing file ' + str(file_num) + '...')

	# Stores file name
	filename = name.split('/')[-1]

	# Removes file type from filename
	shortened_filename = filename.split('.')[0]

	output_dir = root +'/' + shortened_filename
	if (os.path.isdir(output_dir) == False):
		os.makedirs(shortened_filename)

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

	# ----EXPORT - RAW DATA----

	fluor = fluor_raw.copy()
	fluor_raw.columns = column_labels
	fluor_raw.to_excel(writer, ('Raw Data'))

	# ----SLOPES CALCULATION - RAW DATA----

	slope_df = calc_slopes(fluor)

	# ----EXPORT - SLOPES DATA----

	# Plots slopes data
	plot2(slope_df, 'Slopes Data', 'Slopes.png')

	slope_df.to_excel(writer, ('Slopes Data'))

	# ----CORRECTION - SLOPES DATA----

	slope_df = corrected(slope_df)

	# ----EXPORT - CORRECTED SLOPES DATA----

	# Plots corrected slopes data
	plot2(slope_df, 'Corrected Slopes Data', 'Corrected Slopes.png')

	slope_df.to_excel(writer, ('Corrected Slopes'))

	# ----MEMBRANE POTENTIAL STANDARD CURVE----
	if(bool_stdcurve):
		fluor = std_curve(fluor)

		# Plots standard curve data
		plot1(fluor, 'Standard Curve Data', 'Standard_Curve.png')

	# ----AVERAGES - STANDARD CURVE----

		slopes_stdcurve = calc_slopes(fluor)

		# Plots averaged standard curve data
		plot2(slopes_stdcurve, 'Standard Curve Slopes Data', 'Standard_Curve_Slopes.png')

		correct_slopes_stdcurve = slopes_stdcurve.copy()

		correct_slopes_stdcurve = corrected(correct_slopes_stdcurve)

		# Plots averaged standard curve data
		plot2(correct_slopes_stdcurve, 'Corrected Standard Curve Slopes Data', 'Correct_Standard_Curve_Slopes.png')

	# ----EXPORT---

	# Set column labels
	fluor.columns = column_labels

	if(bool_stdcurve):
		fluor.to_excel(writer,('Standard Curve'))
		slopes_stdcurve.to_excel(writer,('Standard Curve Slopes'))
		correct_slopes_stdcurve.to_excel(writer,('Corrected Standard Curve Slopes'))

	writer.save()
	file_num += 1
	os.chdir(root)

print('Analysis complete')
print('-----------------------------------------------')