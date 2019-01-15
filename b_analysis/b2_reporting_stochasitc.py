#!/usr/bin/python3.5.3

"""Script for presence/absence plots for typical species in a EUNIS type.
Hans Roelofsen, November 2018
"""

import os
import sys
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np
from shapely import geometry
import datetime
from scipy import stats

from helper import do

# get EVA data with EMEP attached, EUNIS completeness attached.
dat = do.get_eva_emep_score_data()

# get EUNIS types information
eunis_info = do.get_eunis_types_description()

eunis_type = 'F42'
sp_sel = ['Gentiana pneumonanthe', 'Molinia caerulea', 'Drosera rotundifolia', 'Cladonia portentosa',
          'Sphagnum compactum', 'Eriophorum angustifolium']
eva = dat.dropna(subset=['sp_list', 'NdepTot'])#.loc[dat['EUNIScode'] == eunis_type, :]

fig = plt.figure(figsize=(12, 8), dpi=80)
fig.suptitle("{0}, {1}".format(eunis_type, eunis_info[eunis_type]['New name']))

i = 1

def noise(x):
    return np.random.normal(loc=x, scale=0.01)
    return x

for sp in sp_sel:

    eva = eva.loc[eva['EUNIScode'] == eunis_type, :]
    eva['presence'] = eva.apply(lambda row: 1 if (sp in row['sp_list']) else 0, axis=1)

    ax = fig.add_subplot(3,2,i)


    # Present
    ndep = np.array(eva['NdepTot'].tolist())
    presence = np.array(eva['presence'].tolist())
    # xpresent = np.vstack([ndep, present])
    # zpresent = gaussian_kde(xpresent)(xpresent  )
    #
    # idx = zpresent.argsort()
    # x, y, z = ndep[idx], present[idx], zpresent[idx]
    ax.scatter(ndep, presence, edgecolor='')

    # TODO: stochastic model is gewoon als EXP(ax+b)/(1+EXP(ax+b))
    idx = np.linspace(0, 6000)
    slope, intercept, r_value, p_value, std_err = stats.linregress(ndep, presence)
    prop = np.add(np.multiply(idx, slope), intercept)
    log_prop = np.divide(np.exp(prop), np.add(1, np.exp(prop)))

    ax.plot(idx, log_prop)
    ax.set(title="{0}, R2: {1}".format(sp, round(r_value**2, 2)), ylabel='Presence/Absence', xlim=[0, 6000], ylim=[-0.5, 1.5])

    # absent
    # ndep = np.array(eva.loc[eva[sp] < 0.5, 'NdepTot'].tolist())
    # absent= np.array(eva.loc[eva[sp] < 0.5, sp].tolist())
    # xabsent = np.vstack([ndep, absent])
    # zabsent = gaussian_kde(xabsent)(xabsent)
    #
    # idx = zabsent.argsort()
    # x, y, z = ndep[idx], absent[idx], zabsent[idx]
    # ax.scatter(x, y, c=z, edgecolor='')

    i += 1

plt.show()

