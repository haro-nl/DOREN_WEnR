# -*- coding: utf-8 -*
#!/usr/bin/python3.5.3

'''
Script to:
1. read emep i,j coordinates
2. create shapefile with emep tiles
3. export to shapefile

Hans Roelofsen, 20 november 2018
'''

import os
import pandas as pd
import geopandas as gp
from shapely import geometry
import datetime

# output data
shp_out_dir = r'd:\temptxt\EMEP\cell_shp'
shp_out_name = 'emep_cells.shp'

# read emep coordinate data
in_dir = r'd:\temptxt\EMEP'
emep_in = 'EMEPgrid.csv' # Download from: http://www.emep.int/grid/index.html
emep_coord = pd.read_csv(os.path.join(in_dir, emep_in), sep= ",")

# drop redundant columns
emep_coord = emep_coord.drop(['longcenter', 'latcenter', 'area'], 1)

# create coordinate tuples. Note that the csv gives incorrect names for the points
# .    .
#
# .    .
# from top left & clock wise the points according to the csv are: p3, p4, p2, p1

emep_coord['p1'] = list(zip(emep_coord.longcorner3, emep_coord.latcorner3))
emep_coord['p2'] = list(zip(emep_coord.longcorner4, emep_coord.latcorner4))
emep_coord['p3'] = list(zip(emep_coord.longcorner2, emep_coord.latcorner2))
emep_coord['p4'] = list(zip(emep_coord.longcorner1, emep_coord.latcorner1))

# create empty geodata frame
gdf= gp.GeoDataFrame(crs= {"init": "epsg:4326"})
gdf['geometry'] = None
gdf['emep_tile_id'] = ''
gdf['created'] = ''

# iterate through the coordinates and populate the empty geodataframe
row_iterator =emep_coord.iterrows()
for i, row in row_iterator:

    ply_coord = geometry.Polygon(emep_coord.loc[i, ['p1', 'p2', 'p3', 'p4']])
    gdf.loc[i, 'geometry'] = ply_coord
    gdf.loc[i, 'emep_tile_id'] = str(int(emep_coord.loc[i, 'i'])) + '_' + str(int(emep_coord.loc[i, 'j']))
    gdf.loc[i, 'created'] = datetime.datetime.now().strftime("%Y%m%d_%H%M")

# write to shapefile
gdf.to_file(os.path.join(shp_out_dir, shp_out_name))
# Note, somehow the CRS is not written to the shapefile!
# arcpy.DefineProjection_management(os.path.join(shp_out_dir, shp_out_name), arcpy.SpatialReference(4326))

