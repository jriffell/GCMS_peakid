import sys #loading a default module, sys
#(sys allows you to pass in file instead of coding the file name into the script)
import csv #loads default module, csv; allows Python to read .csv files
import glob
import os.path
import os
import dicttocsv_csvtolist_v2 as conv


def get_name_and_area_from_gcms(csv_filename):
	"""
	reads in processed gcms data from utf8-encoded csv file name passed in; returns a list of
	chemicals and their areas for that sample
	"""
	name_and_area_doubles = []
	areas = [float(item) for item in conv.read_unicode_csv_col_to_list(csv_filename, 2)] 
	names = conv.read_unicode_csv_col_to_list(csv_filename, 3 )
	for i in range(0, len(areas)):
		name_and_area_doubles.append([names[i], areas[i]])
	return name_and_area_doubles	


def get_names_and_name_to_area(gcms_filepath):
	""" make a list of unique chemical names in each processed sample file, and 
	a dictionary one that pairs names with abundance/area;
	if the flower does not have that particular
	chemical, then it is added to each the list and the dictionary; 
	if we ID two peaks as the same chemical (they may be closely related compounds),
	then we add together the values for all of those peaks for the final area in the dictionary."""
	name_and_area_doubles = get_name_and_area_from_gcms(gcms_filepath)
	list_of_names = []
	name_to_area = {}
	for name, area in name_and_area_doubles:
		if name not in list_of_names:
			list_of_names.append(name)
			name_to_area[name] = area
		else:
			old_area = name_to_area[name]
			area_sum = old_area + area
			name_to_area[name] = area_sum
	return list_of_names, name_to_area

	
def make_list_of_names_and_name_to_area_dictionary_for_all_csvs(directory):
	""" for all csv files in a directory,generates a macro dictionary
	that uses filenames as keys, and returns
	the smaller dictionaries for individual files; also generates as
	separate list with all unique chemical names across all files"""
	csv_files = glob.glob(directory + "*.csv")
	filepath_to_name_to_area_dictionaries_dictionary = {}
	master_list_of_names = []
	for csv_file in csv_files:
		list_of_names, name_to_area = get_names_and_name_to_area(csv_file)
		for name in list_of_names:
			if name not in master_list_of_names:
				master_list_of_names.append(name)
		filepath_to_name_to_area_dictionaries_dictionary[csv_file] = name_to_area
	return filepath_to_name_to_area_dictionaries_dictionary, master_list_of_names


    
def get_dictionary_of_names_and_list_of_areas_in_order(filepath_to_name_to_area_dictionaries_dictionary, master_list_of_names, list_of_filenames):
	""" outputs a dictionary with rt as the key and a list of area values that correspond
	to the order of flower samples in of the list of filenames ({rt ->
	[value of the area for that rt in file 1 in list of filenames,
	in file 2 in list of filenames, etc]}"""
	table = {}
	for name in master_list_of_names:
		all_areas = []
		for filename in list_of_filenames:
			name_to_area_dictionary = filepath_to_name_to_area_dictionaries_dictionary[filename]
			area = name_to_area_dictionary.get(name, 0)
			all_areas.append(area)
		table[name] = all_areas
	return table
	
def make_csv_of_name_area(csv_filename, name_to_areas_dictionary, master_list_of_names, list_of_filepaths):
	""" outputs a .csv file with header of filenames, row.names as rts, and areas/
	abundances filling in the cells"""
	header = ["Chemical_Name"]
	filenames = []
	for filepath in list_of_filepaths:
		filename = filepath.rstrip(os.sep)
		#retain just file name, not full path
		all_slash_indices = [i for i, char in enumerate(filename) if char == "/"]
		last_slash_index = all_slash_indices[-1]
		filename = filename[(last_slash_index + 1):]
		extension_index = filename.index(".csv")
		filename = filename[:extension_index]
		filenames.append(filename)
	header.extend(filenames)
	rows = []
	for name in master_list_of_names:
		row = [name]
		areas = []
		for area in name_to_areas_dictionary[name]:
			areas.append(unicode(int(area)))
		row.extend(areas)
		rows.append(row)
	conv.write_unicode_lists_into_csv_listsasrows(csv_filename, rows, header)

def integrate_csvs_to_one_by_name(csv_output_file, directory_containing_csv_files):

	print "start"
	filepath_to_name_to_area_dictionaries_dictionary, master_list_of_names = make_list_of_names_and_name_to_area_dictionary_for_all_csvs(directory_containing_csv_files)
	
	list_of_filenames = filepath_to_name_to_area_dictionaries_dictionary.keys()
	table = get_dictionary_of_names_and_list_of_areas_in_order(filepath_to_name_to_area_dictionaries_dictionary, master_list_of_names, list_of_filenames)

	make_csv_of_name_area(csv_output_file, table, master_list_of_names, list_of_filenames)


	print "done"

