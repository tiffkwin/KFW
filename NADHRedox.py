# Name: Tiffany Nguyen
# Date: 8.27.18
# File: NADHRedox.py

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
TIME_PERIOD = 180
NUM_PERIODS = 8
sub_list = ['Pyr/M','G/M','Pc/M','S/R','AKG','P/G/M/S/Pc','Pc/M','Ac/M','KIC/M']
substrates = []
ID = ''
s_num = [0,0,0,0,0,0,0,0,0]

# Retrieves input from the user
def get_input():
	global ID
	global substrates
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

# Strips the non-NADH runs from the dataframe
def strip(fluor):

	stripped = pd.DataFrame()
	for column in fluor[fluor.columns[::6]]:
		stripped = pd.concat([stripped, fluor[column]], axis=1)
		stripped =  pd.concat([stripped, fluor[column+1]], axis=1)

	return stripped

# Reduces the y values using the eqn: y = (y-min)/(max-min)*100
def reduce(fluor, avg_stripped):
	newdf = fluor.copy()
	col = 0
	for column in newdf[newdf.columns[::2]]:
		max_y = avg_stripped[substrates[col]].iloc[-2]
		min_y = avg_stripped[substrates[col]].iloc[-1]
		for j in range(0,newdf.apply(pd.Series.last_valid_index)[column] + 1):
			y = newdf[column+1][j]
			val = (y - min_y)/(max_y - min_y)*100
			newdf.at[j,column+1] = val
		col += 1	

	return newdf

# Produces an average for all the data points within a time period
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

# Produces a dataframe containing the metadata for the experiments
def prod_metadata():
	# Prints metadata to dataframe
	metadata = pd.DataFrame(columns=['ID','Substrates','Date'])
	metadata.at[0, 'ID'] = ID
	for i in range(0,len(substrates)):
		metadata.at[i, 'Substrates'] = substrates[i]
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

# ----MAIN----

get_input()
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

	# ----STRIP - RAW DATA----

	fluor = strip(fluor)

	# ----EXPORT - STRIPPED DATA----
	fluor.columns = list(range(0,len(fluor.columns)))

	fluor.to_excel(writer, ('Stripped Data'))

	# Plot stripped data
	plot1(fluor, 'Stripped Data', 'Stripped.png')

	avg_stripped = fluor.copy()
	avg_stripped = averages(avg_stripped)

	# ----REDUCTION - STRIPPED DATA----
	
	fluor = reduce(fluor, avg_stripped)

	# ----EXPORT - REDUCED DATA----

	fluor.to_excel(writer, ('Reduced Data'))

	# Plot reduced data
	plot1(fluor, 'Reduced Data', 'Reduced.png')

	# ----AVERAGES - REDUCED DATA----

	avg = averages(fluor)

	# Plot averaged reduced data
	plot2(avg, 'Averaged Reduced Data', 'Avg_Reduced.png')

	# ----EXPORT - AVG REDUCED DATA----

	avg.to_excel(writer, ('Averaged Reduced Data'))

	writer.save()
	file_num += 1
	os.chdir(root)

print('Analysis complete')
print('-----------------------------------------------')