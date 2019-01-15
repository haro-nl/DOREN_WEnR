#!/usr/bin/python3.5.3

"""Script for scatterplots and distribution maps per EUNIS type.
Hans Roelofsen, November 2018
"""

import os
import sys
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
import numpy as np
from shapely import geometry
import datetime

from helper import do

# get EVA data with EMEP attached, EUNIS completeness attached.
dat = aux.get_eva_emep_score_data()

# get EUNIS types information
eunis_info = aux.get_eunis_types_description()

# get EVA plot data as geopandas geodataframe. We only need this for the European map. CRS = WGS84
eva_gdf = aux.get_eva_data()

# list of all eunis types
eunis_types = [k for k, v in eunis_info.items()]

# Dicts of Dm, Co & Dg species for all EUNIS types
eunis_type_composition_lists = aux.generate_types_species_lists()

# Read Europe country outlines as geopandas geodataframe
eu_cntrs_orig = gp.read_file(os.path.join(r'd:\tempshp\eur_cntrs_wgs84', 'eur_cntrs_wgs84.shp'))
eu_cntrs = eu_cntrs_orig.copy()

# per type from here
for type in eunis_types :
    if type not in ['E11b','E11d','E11e','E11f','E11g','E11h','E11j','E12a','E12b','E12c','E13b','E13c','E15a','E15b','E15c','E15d','E17','E18','E19b','E1B','E21','E22','E23','E24','E31a','E32a','E32b','E33','E34b','E35','E41','E43a','E43b','E44a','E44b','E52a','E52b','E53','E54','E55','E56','E61','E62','E63','E64','E65','F11','F21','F22a','F22c','F23','F24','F31a','F31b','F31e','F31f','F31g','F41','F42','F51','F53','F54','F55','F61a','F61b','F62','F67','F68a','F68b','F68c','F71','F73','F74a','F74b','F74c','F91','F92','F93','F94','G11','G12a','G12b','G13','G14','G16a','G16b','G17a','G17b','G18','G19a','G19b','G1Aa','G1Ab','G1Ba','G1C','G21','G22','G24','G25a','G26','G28','G31a','G31b','G31c','G32','G34a','G34b','G34c','G36','G37','G39a','G39b','G3B','G3C','G3Da','G3Db','G3F2']:
        eunis_type_info = eunis_info[type]
        nDmSp, nCoSp, nDgSp = (len(eunis_type_composition_lists[type][x]) for x in ['DmSp', 'CoSp', 'DgSp'])

        print("{0} - {1} in progress".format(type, eunis_type_info['New name']))

        dat_sel = dat.loc[dat['EUNIScode'] == type, ]  # selection of EVA-EMEP-SCORE data, non-geospatial
        eva_sel = eva_gdf.loc[eva_gdf['PlotObservationID'].isin(dat_sel['PlotObservationID'].tolist())]  # selection from EVA data, geospatial



        if not dat_sel.empty:

            ndep_tot = dat_sel.NdepTot


            # 3rd order polynomial regression
            z = np.polyfit(ndep_tot, dat_sel['dgsp'], 3)
            p = np.poly1d(z)
            xp = np.linspace(0, 6000, 1000)  # x-axis points


            fig = plt.figure(figsize=(12, 8), dpi=80)
            fig.suptitle("{0}, {1}".format(type, eunis_type_info['New name']))
            ax1 = fig.add_subplot(221)
            ax1.scatter(ndep_tot, dat_sel['dmsp'], marker='.')
            ax1.set(title='Dominant Species, n={0}'.format(nDmSp), ylabel='Score', ylim=[-10, 110], xlim=[0, 6000])

            ax2 = fig.add_subplot(222)
            ax2.scatter(ndep_tot, dat_sel['cosp'], marker='.')
            ax2.set(title='Constant Species, n={0}'.format(nCoSp), ylabel='Score', ylim=[-10, 110], xlim=[0, 6000])

            ax3 = fig.add_subplot(223)
            ax3.scatter(ndep_tot, dat_sel['dgsp'], marker='.')
            ax3.set(title='Diagnostic Species, n={0}'.format(nDgSp), ylabel='Score', xlabel='Total N Deposition [mg N / m2]',
                    ylim=[-10, 110], xlim=[0, 6000])
            ax3.plot(xp, p(xp), '-')

            ax4 = fig.add_subplot(224)
            ax4.set(title='Plots, n= {}'.format(len(dat_sel)), xlim=[-20, 65], ylim=[30, 85], )
            # ax4.legend(loc='best', label='{0} EUNIS type EVA plot, n= {1}'.format(eunis_type, len(dat_sel)))
            eu_cntrs.plot(ax=ax4, color='white', edgecolor='grey')
            eva_sel.plot(ax=ax4, color='red', marker='o', markersize=3)

            fig_out_name = "{}_plots".format(type) + datetime.datetime.now().strftime("%Y%m%d_%H%M") + ".png".format(type)
            plt.savefig(os.path.join(r'm:\a_Projects\DOREN\figs\20190103', fig_out_name))
