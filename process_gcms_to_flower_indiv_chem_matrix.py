import sys #loading a default module, sys
#(sys allows you to pass in file instead of coding the file name into the script)
import csv #loads default module, csv; allows Python to read .csv files
from extract_chemical_data_from_gcms import get_cas_and_name_and_area_from_gcms
import glob
import os.path
from extract_chemical_data_from_gcms import write_to_csv

def get_cas_to_name_and_cas_to_area(gcms_filepath):
    """ makes two dictionaries of unique cas numbers;  one that pairs unique cas
    with this chemical name and one that pairs unique cas with abundance;
    if the flower does not have that particular
    cas number, then it is added to each dictionary; if the cas number occurs already,
    then add old area value with new area value for area dictionary; name stays same as
    first name."""
    cas_and_name_and_area_triples = get_cas_and_name_and_area_from_gcms(
            gcms_filepath)
    cas_to_area = {}
    cas_to_name = {}
    for cas, name, area in cas_and_name_and_area_triples:
        if cas not in cas_to_name:
            cas_to_name[cas] = name
            cas_to_area[cas] = area
        else:
            old_area = cas_to_area[cas]
            area_sum = old_area + area
            cas_to_area[cas] = area_sum
    return cas_to_name, cas_to_area

def make_cas_to_area_dictionary_and_cas_to_area_dictionary_for_all_xls(*directories):
    """ generates a macro dictionary that uses filenames as keys, and returns
    the smaller dictionaries for individual files/flower as well as
    separate dictionary mapping cas to names(made by get_unique_
    cas_name_areas; key=cas, returns abundance/area for one dictionary; key= cas,
    returns name for other dictionary)"""
    xls_files = []
    for count, directory in enumerate(directories):
        xls_files_from_dir = glob.glob(directory + "*.xls")
        for xls_file in xls_files_from_dir:
            xls_files.append(xls_file)
    filepath_to_cas_to_area_dictionaries_dictionary = {}
    master_cas_to_name = {}
    for xls_file in xls_files:
        cas_to_name, cas_to_area = get_cas_to_name_and_cas_to_area(xls_file)
        for cas in cas_to_name:
            master_cas_to_name[cas] = cas_to_name[cas]
        filepath_to_cas_to_area_dictionaries_dictionary[xls_file] = cas_to_area
    return filepath_to_cas_to_area_dictionaries_dictionary, master_cas_to_name


    
def get_table_of_cas_numbers_and_list_of_areas(
            filepath_to_cas_dictionaries_dictionary, cas_to_name,
            list_of_filenames):
    """ outputs a dictionary with cas as the key and a list of area values that correspond
    to the order of flower samples in of the list of filenames ({cas ->
    [value of the are for that cas in file 1 in list of filenames,
    in file 2 in list of filenames, etc]}"""
    table = {}
    for cas in cas_to_name:
        areas = []
        for filename in list_of_filenames:
            cas_to_area_dictionary = filepath_to_cas_dictionaries_dictionary[filename]
            area = cas_to_area_dictionary.get(cas, 0)
            areas.append(area)
        table[cas] = areas
    return table

def make_csv_of_cas_name_area(csv_filename, cas_to_areas_dictionary, cas_to_name, list_of_filepaths):
    """ outputs a .csv file with header of filenames, row.names as cas numbers, and areas/
    abundances filling in the cells"""
    header = ["CAS_Number", "Chemical_Name"]
    filenames = []
    for filepath in list_of_filepaths:
        filename = filepath.rstrip(os.sep)
        #retain just file name, not full path
        all_slash_indices = [i for i, char in enumerate(filename) if char == "/"]
        last_slash_index = all_slash_indices[-1]
        filename = filename[(last_slash_index + 1):]
        extension_index = filename.index(".xls")
        filename = filename[:extension_index]
        filenames.append(filename)
    header.extend(filenames)
    rows = []
    for cas in cas_to_name:
        row = [cas, cas_to_name[cas]]
        areas = []
        for area in cas_to_areas_dictionary[cas]:
            areas.append(int(area))
        row.extend(areas)
        rows.append(row)
    write_to_csv(csv_filename, rows, header)




# def create_csv_chems_cas(directory_containing_xls_files, csv_output_file = "indiv_chem_flower_matrix_initial.csv"):
#     """create csv of all files and all chemicals aggregated by CAS for use in adding to the synonym dictionary"""

#     #directory_containing_xls_files = sys.argv[1] #reads in first cmd line argument (gcms excel file)
#     filepath_to_cas_dictionaries_dictionary, cas_to_name = make_cas_to_area_dictionary_and_cas_to_area_dictionary_for_all_xls(
#         directory_containing_xls_files)

#     list_of_filepaths = filepath_to_cas_dictionaries_dictionary.keys()
#     table = get_table_of_cas_numbers_and_list_of_areas(filepath_to_cas_dictionaries_dictionary, cas_to_name,
#             list_of_filepaths)


#     make_csv_of_cas_name_area(csv_output_file, table, cas_to_name, list_of_filepaths)


def create_csv_chems_cas(csv_output_file = "indiv_chem_flower_matrix_initial.csv", *directories_containing_xls_files):
    """create csv of all files and all chemicals aggregated by CAS for use in adding 
    to the synonym dictionary; can take multiple directories as *args so that can combine
    data that need to be separated for later analyses because were run with different columns"""

    #directory_containing_xls_files = sys.argv[1] #reads in first cmd line argument (gcms excel file)
    filepath_to_cas_dictionaries_dictionary, cas_to_name = make_cas_to_area_dictionary_and_cas_to_area_dictionary_for_all_xls(
        *directories_containing_xls_files)

    list_of_filepaths = filepath_to_cas_dictionaries_dictionary.keys()
    table = get_table_of_cas_numbers_and_list_of_areas(filepath_to_cas_dictionaries_dictionary, cas_to_name,
            list_of_filepaths)


    make_csv_of_cas_name_area(csv_output_file, table, cas_to_name, list_of_filepaths)



