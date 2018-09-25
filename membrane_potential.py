# Initialize
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

def get_input():
	global ID
	global SLOPE
	global Y_INT
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
				substrates.append(sub_list[int(input('Select substrate ' + str(i + 1) + ': ')) - 1])
			break
		except Exception:
			print(substrates)
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
		
	return stdcurve


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

# Divides all the averages by the average for Ala to produce a corrected dataset
def corrected(avg_raw):

	for column in avg_raw:

		rnum = 0
		ala_avg = avg_raw[column][avg_raw.apply(pd.Series.last_valid_index)[column]]

		for j in avg_raw[column]:
			avg_raw.at[rnum, column] = j/ala_avg
			rnum += 1

	return avg_raw


# ----MAIN----

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

	x_col = fluor_raw[0]
	run = 1
	for i in range(0, len(fluor_raw.columns)):
		if i % 2 == 0:
			x_col = fluor_raw[i]
		else:
			plt.plot(x_col, fluor_raw[i], label='Run ' + str(run))
			run += 1
	plt.legend(loc='best')
	#plt.show()
	plt.title('Raw Data')
	plt.savefig('Raw.png')
	plt.clf()

	# Prints metadata to dataframe
	metadata = pd.DataFrame(columns=['ID','Standard Curve','Slope','Y-Intercept','Substrates','Date'])
	metadata.at[0, 'ID'] = ID
	metadata.at[0, 'Standard Curve'] = bool_stdcurve
	metadata.at[0, 'Slope'] = SLOPE
	metadata.at[0, 'Y-Intercept'] = Y_INT
	for i in range(0,len(substrates)):
		metadata.at[i, 'Substrates'] = substrates[i]
	now = datetime.datetime.now()
	metadata.at[0,'Date'] = now.strftime("%Y-%m-%d")

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

	# ----AVERAGES - RAW DATA----

	avg_raw = averages(fluor)

	avg_raw.plot()
	plt.title('Averaged Raw Data')
	plt.savefig('Avg_Raw.png')
	plt.clf()

	# ----EXPORT - AVG RAW DATA----

	avg_raw.to_excel(writer, ('Averaged Raw Data'))

	corrected_raw = corrected(avg_raw)

	corrected_raw.plot()
	plt.title('Corrected Data')
	plt.savefig('Corrected.png')
	plt.clf()

	# ----MEMBRANE POTENTIAL STANDARD CURVE----
	if(bool_stdcurve):
		fluor = std_curve(fluor)

		x_col = fluor[0]
		run = 1
		for i in range(0, len(fluor.columns)):
			if i % 2 == 0:
				x_col = fluor[i]
			else:
				plt.plot(x_col, fluor[i], label='Run ' + str(run))
				run += 1
		plt.legend(loc='best')
		#plt.show()
		plt.title('Standard Curve Data')
		plt.savefig('Standard_Curve.png')
		plt.clf()

	# ----AVERAGES - STANDARD CURVE----

		avg_stdcurve = averages(fluor)

		avg_stdcurve.plot()
		plt.title('Averaged Standard Curve Data')
		plt.savefig('Avg_Standard_Curve.png')
		plt.clf()

	# ----EXPORT---

	# Set column labels
	fluor.columns = column_labels

	corrected_raw.to_excel(writer,('Corrected Raw Data'))

	if(bool_stdcurve):
		fluor.to_excel(writer,('Standard Curve'))
		avg_stdcurve.to_excel(writer,('Averaged Standard Curve'))

	writer.save()
	file_num += 1
	os.chdir(root)

print('Analysis complete')
print('-----------------------------------------------')