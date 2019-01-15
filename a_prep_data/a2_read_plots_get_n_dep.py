# -*- coding: utf-8 -*
#!/usr/bin/python3.5.3

"""
Script to:
1. read EVA plot header data
2. mate EVA plot header data to its EUNIS vegetation type
3. match each plot to the nearest EMEP tile based on emep_cell_id "i_j" using a spatial join
4. mate each plot to an emep model output based on its emep_cell_id and drawing emep data from the same year
5. export EVA plot header data as csv with total n deposition data and other emep model output attached

Hans Roelofsen, 20 november 2018
"""

import os
import pandas as pd
import geopandas as gp
from shapely import geometry
import datetime
import sys

from helper import do

if __name__ == "__main__":

    # script output name and location
    eva_dir_out = r'm:\a_Projects\DOREN\b_half'
    eva_name_out = 'eva_emep_mate_' + datetime.datetime.now().strftime("%Y%m%d_%H%M") + '.csv'

    print("starting at {0}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M")))

    # get eva plot data
    eva = aux.get_eva_data()

    # get eunis types
    eunis = aux.get_eunis_type_of_all_plots()

    # get emep tiles (shapefile) and all data (pandas df)
    emep_tiles = aux.get_emep_tiles()
    emep_all = aux.get_emep_dat()

    # eva to eunis merge based on PlotObservationID
    eva = pd.merge(eva, eunis, on='PlotObservationID', how='inner')
    print('EVA plots after merge with EUNIS: {0}'.format(eva.shape[0]))

    # eva spatial join to emep tiles
    eva = gp.sjoin(eva, emep_tiles, how='inner', op='within')
    print('EVA plots after spatial join emep tiles: {0}'.format(eva.shape[0]))

    # other important stuff
    emep_years = [1980, 1985, 1990, 1995] + [i for i in range(1996, 2016)]
    eva_holder = []

    # iterate for each year, to allow a eva-emep merge based on the emep_tile_id (remember each tile id occurs in
    # each year!)
    for year in emep_years:
        eva_yr = eva.loc[eva['Date of recording'] == year,:]
        emep_yr = emep_all.loc[emep_all['Yr'] == year,:]

        dat = pd.merge(eva_yr, emep_yr, left_on='emep_tile_', right_on='emep_tile_id', how='left')
        eva_holder.append(dat)

    # concatenate the stored dfs to a new pd.df and write to file
    eva_out = pd.concat([gdf for gdf in eva_holder])
    gdf.to_csv(os.path.join(eva_dir_out, eva_name_out),
               columns=[col for col in list(gdf) if col not in ['plot_coordinates', 'index_right', 'created',
                                                                'Longitude', 'Latitude']], index=False)
    print("Done at {0}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M")))