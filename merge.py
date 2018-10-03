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

for name in files:
	print(name)
	filename = name.split('/')[-1]
	xl = pd.ExcelFile(name)
	os.chdir(output_dir)
	dfs = {sheet: xl.parse(sheet) for sheet in xl.sheet_names}
	for sheet in dfs:
		dfs[sheet].to_excel(writer, (sheet + ' ' + filename)[:30])
	os.chdir(root)
os.chdir(output_dir)
writer.save()