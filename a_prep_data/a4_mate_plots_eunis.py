# -*- coding: utf-8 -*
#!/usr/bin/python3.5.3

'''Script to
1. read EUNIS type indicator species
2. generate look up dictionaries to get Dg, CoSp & DmSp species for each EUNIS types
3. read species list for all EVA vegetation plots and add sp list to each plot in a new column
4. define completeness score for a veg plot based on similarity between actual sp list and DgSp, CoSp & DmSp lists
5. calculate scores for all plots

Hans Roelofsen, 22 November 2018, Wageningen Environmental Research
    '''

import os
import datetime
import pickle

from helper import do

if __name__ == "__main__":

    print("starting at {0}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M")))

    eva_head = do.get_eva_emep_data()         # EVA header data with EMEP already joined
    eva_plot_comp = do.get_eva_plot_species(eva_head['PlotObservationID'].tolist()) # Species composition of all EVA plots
    eunis_type_composition_lists = do.generate_types_species_lists() # Dictionary of CoSp, DgSp & DmSp species for all EUNIS types

    # Add species list as column to the EVA plot table
    eva_head['sp_list'] = eva_head.apply(lambda row: do.get_plot_species(eva_plot_comp, row['PlotObservationID']), axis=1)
    print("Done 01 at {0}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M")))

    # Calculate DmSp score based on actual species list and DmSp species list for the applicable EUNIS type
    eva_head['dmsp'] = eva_head.apply(lambda row: do.completeness(plot_species_list=row['sp_list'],
                                                                  reference_species_list=eunis_type_composition_lists[row['EUNIScode']]['DmSp']), axis=1)
    print("Done 02 at {0}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M")))

    # idem for DgSp
    eva_head['dgsp'] = eva_head.apply(lambda row: do.completeness(plot_species_list=row['sp_list'],
                                                                  reference_species_list=eunis_type_composition_lists[row['EUNIScode']]['DgSp']), axis=1)
    print("Done 03 at {0}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M")))

    # idem for CoSp
    eva_head['cosp'] = eva_head.apply(lambda row: do.completeness(plot_species_list=row['sp_list'],
                                                                  reference_species_list=eunis_type_composition_lists[row['EUNIScode']]['CoSp']), axis=1)
    print("Done 04 at {0}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M")))

    # write to pickle file for safe keeping
    pickle_name = "eva_emep_score" + datetime.datetime.now().strftime("%Y%m%d_%H%M") + '.pkl'
    with open(os.path.join(r'd:\temppickle', pickle_name), 'wb') as handle:
        pickle.dump(eva_head, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("Done all at {0}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M")))




