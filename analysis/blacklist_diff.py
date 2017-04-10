import pandas as pd
import numpy as np

def ComputeDelta(file1, file2):
	#all_files = {file1, file2}

	#df_from_each_file = (pd.read_csv(f) for f in all_files)
	#concatenated_df   = pd.concat(df_from_each_file, ignore_index=True)
	#print(concatenated_df)

	#Read the two files and create two pandas objects
	m1 = pd.read_csv(file1)
	m2 = pd.read_csv(file2)


	#print(m1)
	#print(m2)

	# create a data frame by concating the two data frames
	df = pd.concat([m1, m2])
	df = df.reset_index(drop=True)
	#print(df)
	df_gpby = df.groupby(list(df.columns))
	#Find the indexes for which the lines are repeated
	idx = [x[0] for x in df_gpby.groups.values() if len(x) == 1]
	#print(idx)
	df.reindex(idx)
	#print(df)
	#Find the indewes that we should keep in our Output
	indexes_list = []
	for i in range(0,idx[len(idx)-1]):
		if(i in idx):
		 print('')
		else:
			#print('i DROP NUMBER ',i)
			indexes_list.append(i)
	#print('index_list' , indexes_list)
	m=df.drop(indexes_list)
	print(m)

	#print(idx)
	#difference_locations = np.where(m1 != m2)
	#print(difference_locations)

	#changed_from = df1.values[difference_locations]
	#print (changed_from)

	return m
#Test with the name of the files
toPanda("urls1.txt", "urls2.txt")
