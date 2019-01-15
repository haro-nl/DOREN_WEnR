#!/usr/bin/python3.5.3

"""Script for scatterplots + regression lines and distribution maps per EUNIS type.
Hans Roelofsen, November 2018
"""

import os
import sys
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
import numpy as np
import pickle
from shapely import geometry
import datetime

sys.path.append('m:\B_aux\PC_Doren_py\do')
import aux

# get EVA data with EMEP attached, EUNIS completeness attached.
dat = aux.get_eva_emep_score_data()

# get EVA plot data as geopandas geodataframe. We only need this for the European map. CRS = WGS84
eva_gdf = aux.get_eva_data()

# Read Europe country outlines as geopandas geodataframe
eu_cntrs_orig = gp.read_file(os.path.join(r'd:\tempshp\eur_cntrs_wgs84', 'eur_cntrs_wgs84.shp'))
eu_cntrs = eu_cntrs_orig.copy()

eunis_info = aux.get_eunis_types_description()

eunis_sel = ['G11', 'E12a', 'E17', 'E19b', 'E22', 'E34a', 'E34b', 'E63', 'F41', 'F42', 'F31b', 'F91', 'F92']

eunis_type = eunis_sel[0]

dat_sel = dat.loc[dat['EUNIScode'] == eunis_type, :]
ndep = dat_sel['NdepTot']
dgsp = dat_sel['dgsp']


eva_sel = eva_gdf.loc[eva_gdf['PlotObservationID'].isin(dat_sel['PlotObservationID'].tolist())]

xp = np.linspace(0, 6000, 1000)  # x-axis points

# 3rd order polynominal fit
z = np.polyfit(ndep, dgsp, 3)
p = np.poly1d(z)

# plot die shit
fig = plt.figure(figsize=(12, 8), dpi=80)
fig.suptitle("{0}, {1}".format(eunis_type, eunis_info[eunis_type]['New name']))

ax1 = fig.add_subplot(121)
ax1.set(title='Diagnostic Species', ylabel='Score', xlim=[0, 6000], ylim=[0, 100], xlabel='Total N Deposition [mg N / m2]')
ax1.scatter(ndep, dgsp, marker='.')
ax1.plot(xp, p(xp), '-')

ax2 = fig.add_subplot(122)
ax2.set(title='Plots, n= {}'.format(len(ndep)), xlim=[-20, 65], ylim=[30, 85])
eu_cntrs.plot(ax=ax2, color='white', edgecolor='grey')
eva_sel.plot(ax=ax2, color='red', marker='o', markersize=3)

plt.show()



