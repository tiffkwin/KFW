import xlrd
import os
import glob
import pandas as pd

root = os.getcwd()
path = root + '/*.xlsx'
files = glob.glob(path)  

output_dir = root +'/Merge'
if (os.path.isdir(output_dir) == False):
	os.makedirs('Merge')

writer = pd.ExcelWriter('Merge.xlsx')
dfs = {}
mergedfs = {}

print("Analyzing data...")
for name in files:
	print(name)
	filename = name.split('/')[-1]
	filename = filename.split('.')[0]
	xl = pd.ExcelFile(name)
	dfs[filename] = xl.parse("Averaged Reduced Data")

for df in dfs:
	for column_name in dfs[df].columns:
		normalized_col_name = column_name.split(".")[0]
		if normalized_col_name in mergedfs:
			(mergedfs[normalized_col_name])[df] = (dfs[df])[column_name]
		else:
			mergedfs[normalized_col_name] = pd.DataFrame()
			(mergedfs[normalized_col_name])[df] = (dfs[df])[column_name]

for df in mergedfs:
	(mergedfs[df])['Mean'] = mergedfs[df].mean(axis=1)
	(mergedfs[df])['SEM'] = (mergedfs[df].drop('Mean', axis=1).std(axis=1)).div(math.sqrt(x))

os.chdir(output_dir)

for df in mergedfs:
	print(mergedfs[df])
	mergedfs[df].to_excel(writer,df.replace('/','_'))
writer.save()
print('Analysis complete')