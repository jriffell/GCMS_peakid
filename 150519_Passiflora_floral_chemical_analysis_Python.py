###adding in additional chem sheets that were run on the GCMS after 140923
###using combined dictionary  made from Kovats, data run on 140923, and new data

import os

os.chdir("/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/Python")
#paths to the folders of chemical datasheets in .xls format
chem_path_before130831 = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/from_before_alkane_standards_130831/"
chem_path_btwn130831and140707 = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/after_130831_before_140707/"
chem_path_btwn140707and150101 = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/after_140707_before_150101/"
chem_path_after150101 = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/after_150101/"



import dicttocsv_csvtolist_v2 as conv
import scrape_synonyms_from_NIST_webbook_v5 as scrape
import process_MSRep_excel_files_chemname_and_Kovats_v5 as proc
import process_gcms_to_flower_indiv_chem_matrix as cas
import integrate_whole_processed_csv_directory_to_one_csv as integrate


#1st create dictionary of all synonyms in Kovats db with convert_Kovatsdb_synonymns_with_webscraped_dict.py
#then convert the Kovats db so that all names are one NIST synonym using that dictionary

#####################
#2nd aglomerate all xls files by CAS, then add all the chem names to the Kovats db dictionary using
# process_gcms_to_flower_indiv_chem_matrix.py 
csv_output_file =  "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/indiv_chem_flower_matrix_initial.csv"
cas.create_csv_chems_cas(csv_output_file, chem_path_after150101, chem_path_btwn140707and150101, chem_path_btwn130831and140707, chem_path_before130831)

#make list of chems from data
list_of_chems_in_data = conv.read_unicode_csv_col_to_list(csv_output_file , 1)

#read back in dictionary that has chem names from Kovats and data from samples run before 140920
old_dict = conv.read_unicode_csv_to_dict("Kovatsdb_and_data_dict.csv", 0, 1, header=False)

#combine into one dictionary
dict_to_use = scrape.scrape_whole_list_from_NIST(list_of_chems_in_data, old_dict)


#and write it back into a csv because generating the dict can a long time
conv.write_unicode_dict_to_csv("Kovatsdb_and_data_dict.csv", dict_to_use)



#####################
#3rd write the Kovats db that was converted with the NIST_dict back in as a list of tuples
db = proc.Kovats_db_to_list_of_tuples("Kovats_db_NISTsynonymconverted_140909_utf8.csv")	


######################
#4th, process a whole directory of sheets at a time, taking
#care to use the correct alkane sheet to generate Kovats values
 
#paths to the alkane sheets (need to be in this format to work)
#all of these are from standard runs of C7-C30 alkane mix at 10ng/mL EXCEPT:
###alkanes sheet from before 130831 has values that are inferred based on the different elution times of limonene 
###and pinene in the P. trisecta runs from before 130831 and those in runs between 130831 and 140707; the offset was
###applied to the alkane elution times as a best guess for when these would have come off (in an effor to include precious P. trisecta samples)
alkane_path_before130831  = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/Alkanes_for_Kovats/MARIEMETHOD_alkanes_for_Kovats_before130831.csv"
alkane_path_btwn130831and140707  = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/Alkanes_for_Kovats/MARIEMETHOD_alkanes_for_Kovats_130831to140707.csv"
alkane_path_btwn140707and150101  = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/Alkanes_for_Kovats/MARIEMETHOD_alkanes_for_Kovats_140707to150101.csv"
alkane_path_after150101 = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/Alkanes_for_Kovats/MARIEMETHOD_alkanes_for_Kovats_after150101.csv"


#path to folder where will put processed files and Kovatsmatchonly files
#so that similarly processed files will be in same folders even if they need
#to be processed with different alkanne sheets (bc of diff column/trimmed column at run time)
path_processed_lowthresh = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/all_processed_data_30thresh/"
path_Kovatsmatch_lowthresh = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/all_Kovatsmatch_data_30thresh/"

path_processed_highthresh = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/all_processed_data_70thresh/"
path_Kovatsmatch_highthresh = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/all_Kovatsmatch_data_70thresh/"


#process sheets together that were run when the column was in the same state (dates say when column was changed or cut)
#all are DB5 columns



##############################################
#WITH LOW THRESHOLD FOR KEEPING CHEMS (30% match)
##############################################
#process sheets run between 130831 - 140707
proc.process_entire_directory_of_NIST_sheets_to_csv(path_Kovatsmatch_lowthresh, chem_path_btwn130831and140707 ,
 db, 10, alkane_path_btwn130831and140707, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = True, make_csv=True, NIST_qual_threshold= 30)

proc.process_entire_directory_of_NIST_sheets_to_csv(path_processed_lowthresh, chem_path_btwn130831and140707,
 db, 10, alkane_path_btwn130831and140707, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True, NIST_qual_threshold= 30 )

#process sheets run between 140707 - 150101
proc.process_entire_directory_of_NIST_sheets_to_csv(path_Kovatsmatch_lowthresh, chem_path_btwn140707and150101 ,
 db, 10, alkane_path_btwn140707and150101 , dict_to_use, x_min_threshold = 3.5, Kovats_match_only = True, make_csv=True , NIST_qual_threshold= 30)

proc.process_entire_directory_of_NIST_sheets_to_csv(path_processed_lowthresh, chem_path_btwn140707and150101 ,
 db, 10, alkane_path_btwn140707and150101, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True, NIST_qual_threshold= 30)

#process sheets run after 150101
proc.process_entire_directory_of_NIST_sheets_to_csv(path_Kovatsmatch_lowthresh, chem_path_after150101 ,
 db, 10, alkane_path_after150101 , dict_to_use, x_min_threshold = 3.5, Kovats_match_only = True, make_csv=True, NIST_qual_threshold= 30)

proc.process_entire_directory_of_NIST_sheets_to_csv(path_processed_lowthresh, chem_path_after150101 ,
 db, 10, alkane_path_after150101, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True, NIST_qual_threshold= 30)


#process sheets run before 130831 (many from 2012) with alkane elution times guessed based on sample differences in RT for limonene
#and pinene from 2012 vs between 130831 and 140707 to find the offset;
###just done to include precious P. trisecta samples that were run before we did alkane standards and that were used up in ephys experiments
proc.process_entire_directory_of_NIST_sheets_to_csv(path_Kovatsmatch_lowthresh, chem_path_before130831,
 db, 10, alkane_path_before130831 , dict_to_use, x_min_threshold = 3.5, Kovats_match_only = True, make_csv=True, NIST_qual_threshold= 30)

proc.process_entire_directory_of_NIST_sheets_to_csv(path_processed_lowthresh, chem_path_before130831,
 db, 10, alkane_path_before130831, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True, NIST_qual_threshold= 30)


##############################################
#WITH HIGH THRESHOLD FOR KEEPING CHEMS (70% match)
##############################################
#process sheets run between 130831 - 140707
proc.process_entire_directory_of_NIST_sheets_to_csv(path_Kovatsmatch_highthresh, chem_path_btwn130831and140707 ,
 db, 10, alkane_path_btwn130831and140707, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = True, make_csv=True, NIST_qual_threshold= 70)

proc.process_entire_directory_of_NIST_sheets_to_csv(path_processed_highthresh, chem_path_btwn130831and140707,
 db, 10, alkane_path_btwn130831and140707, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True, NIST_qual_threshold= 70 )

#process sheets run between 140707 - 150101
proc.process_entire_directory_of_NIST_sheets_to_csv(path_Kovatsmatch_highthresh, chem_path_btwn140707and150101 ,
 db, 10, alkane_path_btwn140707and150101 , dict_to_use, x_min_threshold = 3.5, Kovats_match_only = True, make_csv=True,  NIST_qual_threshold= 70)

proc.process_entire_directory_of_NIST_sheets_to_csv(path_processed_highthresh, chem_path_btwn140707and150101 ,
 db, 10, alkane_path_btwn140707and150101, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True, NIST_qual_threshold= 70)

#process sheets run after 150101
proc.process_entire_directory_of_NIST_sheets_to_csv(path_Kovatsmatch_highthresh, chem_path_after150101 ,
 db, 10, alkane_path_after150101 , dict_to_use, x_min_threshold = 3.5, Kovats_match_only = True, make_csv=True, NIST_qual_threshold= 70)

proc.process_entire_directory_of_NIST_sheets_to_csv(path_processed_highthresh, chem_path_after150101 ,
 db, 10, alkane_path_after150101, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True, NIST_qual_threshold= 70)


#process sheets run before 130831 (many from 2012) with alkane elution times guessed based on sample differences in RT for limonene
#and pinene from 2012 vs between 130831 and 140707 to find the offset;
###just done to include precious P. trisecta samples that were run before we did alkane standards and that were used up in ephys experiments
proc.process_entire_directory_of_NIST_sheets_to_csv(path_Kovatsmatch_highthresh, chem_path_before130831,
 db, 10, alkane_path_before130831 , dict_to_use, x_min_threshold = 3.5, Kovats_match_only = True, make_csv=True, NIST_qual_threshold= 70)

proc.process_entire_directory_of_NIST_sheets_to_csv(path_processed_highthresh, chem_path_before130831,
 db, 10, alkane_path_before130831, dict_to_use, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True, NIST_qual_threshold= 70)



#finally, use integrate_whole_processed_csv_directory_to_one_csv.py in the command line to process all the items
# in the _Kovatsmatchonly folder and separately for those in the _processed folder
#for each, change the filepath for the new csv in the python file

#kovats match only (within 10 kovats units and NIST match); low NIST threshold of 30% match
directory_Kovatsmatch = path_Kovatsmatch_lowthresh
csv_output_file_Kovatsmatch = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/150519_integrated_chem_data_Kovatsmatch_30thresh.csv"
integrate.integrate_csvs_to_one_by_name(csv_output_file_Kovatsmatch, directory_Kovatsmatch)

#kovats match only (within 10 kovats units and NIST match); high NIST threshold of 70% match
directory_Kovatsmatch = path_Kovatsmatch_highthresh
csv_output_file_Kovatsmatch = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/150519_integrated_chem_data_Kovatsmatch_70thresh.csv"
integrate.integrate_csvs_to_one_by_name(csv_output_file_Kovatsmatch, directory_Kovatsmatch)


# all NIST over 30% 
#with choosing best kovats match IF there is that matches the NIST match within 10 kovats units of the hit
directory_processed = path_processed_lowthresh
csv_output_file_processed = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/150519_integrated_chem_data_processed_30thresh.csv"
integrate.integrate_csvs_to_one_by_name(csv_output_file_processed, directory_processed)

# all NIST over 70% 
#with choosing best kovats match IF there is that matches the NIST match within 10 kovats units of the hit
directory_processed = path_processed_highthresh
csv_output_file_processed = "/media/sf_Riffell_Lab_Research/Passiflora_final_chemical_analysis/data/150519_integrated_chem_data_processed_70thresh.csv"
integrate.integrate_csvs_to_one_by_name(csv_output_file_processed, directory_processed)
