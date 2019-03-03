###adding in additional chem sheets that were run on the GCMS after 140923
###using combined dictionary  made from Kovats, data run on 140923, and new data

import os
import pandas as pd

os.chdir("/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/Python")

#paths to integrated chemical files; these were processed with these scripts to yield these integrated
#data sheets, so all the chemicals in them should already be in the dictionary
kovats_30_path = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/150519_integrated_chem_data_Kovatsmatch_30thresh.csv"
kovats_70_path = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/150519_integrated_chem_data_Kovatsmatch_70thresh.csv"
proc_30_path = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/150519_integrated_chem_data_processed_30thresh.csv"
proc_70_path = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/150519_integrated_chem_data_processed_70thresh.csv"



import dicttocsv_csvtolist_v2 as conv
import scrape_stereoisomers_from_NIST_webbook_v2 as ster



# #read back in synonym dictionary that has chem names from Kovats and data from samples run before 140920
# syn_dict = conv.read_unicode_csv_to_dict("Kovatsdb_and_data_dict.csv", 0, 1, header=False)

# #find all stereoisomers of values in the dict (the chem names that will be in our syn_dict converted data)
# #we start with an empty dict because we've never created a stereoisomer dictionary before
# stereo_dict = {}
# stereo_dict = ster.scrape_whole_list_of_stereoisomers_from_NIST_and_create_dict(syn_dict, stereo_dict)

# #write brand new stereoisomer dictionary to a csv
# #TO BE USED AFTER CONVERTING ALL CHEMICAL SYNONYMS TO A SINGLE SYNONYM
# #CONTAINS ALL SYNONYMS IN synonym dict contained in Kovatsdb_and_data_dict.csv as of 150601
# ##### (should be updated with every update of the synonyms dictionary)
# #will then combine these synonyms that are stereoisomers of one another to a single name
# conv.write_unicode_dict_to_csv("main_syns_to_stereoisomer_dict.csv", stereo_dict)

#read back in stereoisomer dictionary
stereo_dict_old = conv.read_unicode_csv_to_dict("main_syns_to_stereoisomer_dict.csv", 0, 1, header=False)

#updating stereoisomer dictionary (should be same in this case)
syn_dict = conv.read_unicode_csv_to_dict("Kovatsdb_and_data_dict.csv", 0, 1, header=False)
stereo_dict = ster.scrape_whole_list_of_stereoisomers_from_NIST_and_create_dict(syn_dict, stereo_dict_old)


########################################################################################################
#now converting Passiflora floral data sheets to single stereoisomers for a set of stereoisomers, 
#and adding these rows together if correspond to the same stereoisomer
os.chdir("/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis")
ster.convert_chemical_matrix_with_stereoisomer_dict(kovats_30_path, stereo_dict, "150604_stereo_chem_kovats30.csv" )

ster.convert_chemical_matrix_with_stereoisomer_dict(kovats_70_path, stereo_dict, "150604_stereo_chem_kovats70.csv" )

ster.convert_chemical_matrix_with_stereoisomer_dict(proc_30_path, stereo_dict, "150604_stereo_chem_proc30.csv" )

ster.convert_chemical_matrix_with_stereoisomer_dict(proc_70_path, stereo_dict, "150604_stereo_chem_proc70.csv" )






