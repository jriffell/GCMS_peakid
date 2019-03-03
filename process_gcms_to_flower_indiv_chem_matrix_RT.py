import sys #loading a default module, sys
#(sys allows you to pass in file instead of coding the file name into the script)
import csv #loads default module, csv; allows Python to read .csv files
from extract_chemical_data_from_gcms_RT import get_rt_and_name_and_area_from_gcms
import glob
import os.path
from extract_chemical_data_from_gcms_RT import write_to_csv

def get_rt_to_name_and_rt_to_area(gcms_filepath):
    """ makes two dictionaries of unique cas numbers;  one that pairs unique cas
    with this chemical name and one that pairs unique cas with abundance;
    if the flower does not have that particular
    cas number, then it is added to each dictionary; if the cas number occurs already,
    then add old area value with new area value for area dictionary; name stays same as
    first name."""
    rt_and_name_and_area_triples = get_rt_and_name_and_area_from_gcms(
            gcms_filepath)
    rt_to_area = {}
    rt_to_name = {}
    for rt, name, area in rt_and_name_and_area_triples:
        if rt not in rt_to_name:
            rt_to_name[rt] = name
            rt_to_area[rt] = area
        else:
            old_area = rt_to_area[rt]
            area_sum = old_area + area
            rt_to_area[rt] = area_sum
    return rt_to_name, rt_to_area

def make_rt_to_area_dictionary_and_rt_to_name_dictionary_for_all_xls(directory):
    """ generates a macro dictionary that uses filenames as keys, and returns
    the smaller dictionaries for individual files/flower as well as
    separate dictionary mapping rt to names(made by get_unique_
    rt_name_areas; key=rt, returns abundance/area for one dictionary; key= rt,
    returns name for other dictionary)"""

    xls_files = glob.glob(directory + r"\*.xls")
    filepath_to_rt_to_area_dictionaries_dictionary = {}
    master_rt_to_name = {}
    for xls_file in xls_files:
        rt_to_name, rt_to_area = get_rt_to_name_and_rt_to_area(xls_file)
        for rt in rt_to_name:
            master_rt_to_name[rt] = rt_to_name[rt]
        filepath_to_rt_to_area_dictionaries_dictionary[xls_file] = rt_to_area
    return filepath_to_rt_to_area_dictionaries_dictionary, master_rt_to_name


    
def get_table_of_rts_and_list_of_areas(
            filepath_to_rt_dictionaries_dictionary, rt_to_name,
            list_of_filenames):
    """ outputs a dictionary with rt as the key and a list of area values that correspond
    to the order of flower samples in of the list of filenames ({rt ->
    [value of the area for that rt in file 1 in list of filenames,
    in file 2 in list of filenames, etc]}"""
    table = {}
    for rt in rt_to_name:
        areas = []
        for filename in list_of_filenames:
            rt_to_area_dictionary = filepath_to_rt_dictionaries_dictionary[filename]
            area = rt_to_area_dictionary.get(rt, 0)
            areas.append(area)
        table[rt] = areas
    return table

def make_csv_of_rt_name_area(csv_filename, rt_to_areas_dictionary, rt_to_name, list_of_filepaths):
    """ outputs a .csv file with header of filenames, row.names as rts, and areas/
    abundances filling in the cells"""
    header = ["RT_min", "Chemical_Name"]
    filenames = []
    for filepath in list_of_filepaths:
        filename = filepath.rstrip(os.sep)
        filenames.append(filename)
    header.extend(list_of_filenames)
    rows = []
    for rt in rt_to_name:
        row = [rt, rt_to_name[rt]]
        areas = []
        for area in rt_to_areas_dictionary[rt]:
            areas.append(int(area))
        row.extend(areas)
        rows.append(row)
    write_to_csv(csv_filename, rows, header)

print "start"

directory_containing_xls_files = sys.argv[1] #reads in first cmd line argument (gcms excel file)
filepath_to_rt_dictionaries_dictionary, rt_to_name = make_rt_to_area_dictionary_and_rt_to_name_dictionary_for_all_xls(
    directory_containing_xls_files)


list_of_filenames = filepath_to_rt_dictionaries_dictionary.keys()
table = get_table_of_rts_and_list_of_areas(filepath_to_rt_dictionaries_dictionary, rt_to_name,
            list_of_filenames)

csv_output_file = "C:\Users\Marie\Documents\GRAD SCHOOL!\Riffell Lab Research\Theresa chemistry\indiv_chem_flower_matrix.csv"

make_csv_of_rt_name_area(csv_output_file, table, rt_to_name, list_of_filenames)








print "done"
