# Several functions related to the DOREN project. By Hans Roelofsen, 27/Nov/2018 16:58

import os
import sys
import pandas as pd
import geopandas as gp
import numpy as np
import pickle
from shapely import geometry
import datetime


def get_eva_data():
    """read eva veg plot header data. Remove non-relevant data. Convert to geodataframe.
    Assumes location of input data"""

    eva_dir_in = r'd:\doren_src_data\EVA_full'
    eva_name_in = 'EVA_2018_09_18_header.csv'

    eva_dat = pd.read_csv(os.path.join(eva_dir_in, eva_name_in), sep="\t")

    # drop redundant columns
    eva_dat = eva_dat.drop([col for col in list(eva_dat) if col not in ['PlotObservationID', 'Date of recording',
                                                                        'Longitude', 'Latitude',
                                                                        'Location uncertainty (m)', 'Dataset']], 1)

    print("EVA plots starting number: {0}".format(len(eva_dat)))

    # remove unusable rows: no year info, no latitude and/or longitude,
    eva_dat = eva_dat.dropna(subset=['PlotObservationID', 'Date of recording', 'Longitude', 'Latitude'])
    print("Remaining after removing nulls: {0}".format(len(eva_dat)))

    # remove plots from non-emep years:
    emep_years = [1980, 1985, 1990, 1995] + [i for i in range(1996, 2016)]
    eva_dat = eva_dat[eva_dat['Date of recording'].isin(emep_years)]
    print("Remaining in just emep years: {0}".format(len(eva_dat)))

    # ensure datatypes for remaining columns
    eva_dat['Date of recording'] = pd.to_numeric(eva_dat['Date of recording'], downcast='integer')

    # add plot geometry and convert to geodataframe
    eva_dat['plot_coordinates'] = list(zip(eva_dat.Longitude, eva_dat.Latitude))
    eva_dat['plot_coordinates'] = eva_dat['plot_coordinates'].apply(geometry.Point)

    return gp.GeoDataFrame(eva_dat, geometry='plot_coordinates', crs={"init": "epsg:4326"})


def get_eva_emep_data():
    """read eva veg plot data with EMEP data attached. Assumes directory and file name"""
    return pd.read_csv(os.path.join(r'd:\tempTV\EVA_EMEP', 'eva_emep_mate_20181122_1547.csv'), sep=',')


def get_eva_emep_score_data():
    """"read eva veg plot data with EMEP data attached, with EUNIS type completeness attahched. 
    Assumes location of input data"""
    with open(r'm:\a_Projects\DOREN\EVA_EMEP\eva_emep_score20190102_1156.pkl', 'rb') as file_handle:
        dat = pickle.load(file_handle) 
    return dat
    

def get_eunis_type_of_all_plots():
    """read the EUNIS type for all the veg plots. Assumes location of input data"""

    eunis_dir_in = r'd:\doren_src_data\EVA_full'
    eunis_name_in = 'EVA_2018_09_18_EUNIS.csv'

    foo = pd.read_csv(os.path.join(eunis_dir_in, eunis_name_in), sep='\t')
    print("EUNIS type found for {0} veg plots.".format(foo.shape[0]))
    return foo


def get_eunis_types_description():
    """gets list of all EUNIS types including old code, new code and new name. Keep in mind that Old code is the correct code!"""
    eunis_species_dir = r'd:\doren_src_data\EVA_full'
    eunis_species_name_in = 'EVA_2018_11_22_EUNIS_SPECIES.csv'
    eunis = pd.read_csv(os.path.join(eunis_species_dir, eunis_species_name_in), sep=';', comment='#')
    eunis = eunis.drop(['Status', 'Species name', 'Frequency'], 1)
    eunis = eunis.drop_duplicates(keep='first')
    all_types = eunis['Old code'].tolist()
    out = {}
    row_iter = eunis.iterrows()
    for i, row in row_iter:
        out_type = {}
        out_type['New code'] = eunis.loc[i, 'New code']
        out_type['New name'] = eunis.loc[i, 'New name']
        out[eunis.loc[i, 'Old code']] = out_type
    return out
    

def generate_types_species_lists():

    # TODO, 29/Nov/2018 10:07, merge this function with get_eunis_types_description()!

    """Create a dictionary to look up Dg, Dm and Co species lists for each EUNIS type, 
    as follows: {EUNIS type1:{'DgSp':[sp1, sp2..sp3], 'DmSp':[sp1, sp2...sp3], 'Co':[sp1, sp2...sp3]}, EUNIS type2:{...}}.
    Assumes location of input data"""
    eunis_species_dir = r'd:\doren_src_data\EVA_full'
    eunis_species_name_in = 'EVA_2018_11_22_EUNIS_SPECIES.csv'
    eunis = pd.read_csv(os.path.join(eunis_species_dir, eunis_species_name_in), sep=';', comment='#')

    eunis_types = eunis['Old code'].unique().tolist()
    species_lists = {}

    statusus = ['DgSp', 'CoSp', 'DmSp']

    for eunis_type in eunis_types:
        out = {}
        for status in statusus:
            out[status] = eunis.loc[(eunis['Status'] == status) & (eunis['Old code'] == eunis_type), 'Species name'].tolist()
        species_lists[eunis_type] = out

    return species_lists


def completeness(plot_species_list, reference_species_list):
    """function to calculate completeness in % between a target list of species and a reference list"""
    n_reference = len(reference_species_list) # number species in the reference list. Assumes no duplicates
    n_plot = len(list(set(plot_species_list) & set(reference_species_list))) # number of matching species equals intersection of the tw0 lists
    return np.product([np.divide(n_plot, n_reference), 100], dtype=np.float16)


def get_eva_plot_species(plot_obs_id_list):
    """function to get species composition of all EVA plots. Assumes EVA plot composition directory and file name.
    Filter rows to PlotObservationIDs as found in *plot_obs_id_list* to avoid loading 33.000.000 records"""
    foo = pd.read_csv(os.path.join(r'd:\doren_src_data\EVA_full', 'EVA_2018_09_18_species.csv'), sep='\t',
                      header=0, usecols=['PlotObservationID','Matched concept', 'Taxon ID', 'Cover %', 'Cover code'])
    return foo[foo['PlotObservationID'].isin(plot_obs_id_list)]


def get_plot_species(plot_species_data, plot_id):
    """function to get all species in *plot_id* as a list sourcing from *plot_species_data* """
    if plot_id in plot_species_data['PlotObservationID'].values:
        return plot_species_data.loc[plot_species_data['PlotObservationID'] == plot_id, 'Matched concept'].tolist()
    else:
        return False


def get_emep_tiles():
    """read emep tiles shapefile as geopandas object. Assumes location of input data"""
    emep_tiles_dir_in = r'd:\doren_src_data\EMEP\cell_shp'
    emep_tiles_in = 'emep_cells.shp'
    return gp.read_file(os.path.join(emep_tiles_dir_in, emep_tiles_in))


def get_emep_dat():
    """read the full emep model output as csv data. Assumes location of input data"""
    # EMEP all data
    emep_dep_dir_in = r'd:\doren_src_data\EMEP'
    emep_dep_name_in = 'QNdepAll_hdr.txt'
    return pd.read_csv(os.path.join(emep_dep_dir_in, emep_dep_name_in), sep=';')


