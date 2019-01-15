#!/usr/bin/python3.5.3

'''
script for reading EMEP and saving as file per year
Hans Roelofsen, 20 november 2018
'''

import pandas as pd
import os

# read input data
in_dir = r'd:\temptxt\EMEP'
emep_in = 'QNdepAll.txt' # This is data as provided by Gert Jan Reinds!
emep_all = pd.read_csv(os.path.join(in_dir, emep_in), sep= ";")

# restrict data to indices i = 1:132 and j = 1:159
emep_all = emep_all.loc[(emep_all['i'] > 0) & (emep_all['i'] < 133) & (emep_all['j'] > 0) & (emep_all['j'] < 160), :]

# create emep tile id
emep_all['emep_tile_id'] = emep_all['i'].map(str) + '_' + emep_all['j'].map(str)

# write back
emep_all.to_csv(os.path.join(in_dir, 'QNdepAll_hdr.txt'), sep=';', index= False)
'''
# the years with emep data. Write each year to file
years = [1980, 1985, 1990, 1995] + [i for i in range(1996, 2016)]
out_dir = r'd:\temptxt\EMEP\yearly'
out_root = 'emep_qndepall_'

for year in years:
    emep_sel= emep_all.loc[emep_all['Yr'] == year]
    emep_sel.to_csv(os.path.join(out_dir, out_root + str(year) + ".txt"), sep= ";", index= False)
'''