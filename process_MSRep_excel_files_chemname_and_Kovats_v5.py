import os
import math
import glob

#os.chdir("C:\\Users\Marie\Documents\GRAD SCHOOL!\Riffell Lab Research\Passiflora bulk chemical analysis\Python")

import dicttocsv_csvtolist_v2 as conv
from xlrd import open_workbook

#read in excel files
#make lists
#All in one:
	#for each list in the list
	#remove peak (list) if RT before 3.5 mins (or user specify?)
	#remove peak (list) if NIST match quality percentage is below a user specified value (default, 70%)
	#change RTs into Kovats (take in list of lists and a sheet of alkane C's and RTs)- its own helper fxn
	#convert chem names with NIST synonym dictionary in each list
	#retain the name and match percentage of the NIST match (with highest match percentage that matches a Kovats entry); 
	##if not matches, keep NIST match -its own helper fxn
	
#os.chdir("C:\\Users\Marie\Documents\GRAD SCHOOL!\Riffell Lab Research\Theresa chemistry\NIST Library")


def get_rt_area_chemname_and_matchqual_from_gcms(xls_filename):
	"""reads in gcms excel data from file name passed in; returns a list of lists of retention times, areas,
	and all the chemical names and match quality percentages that are potential matches for that peak 
	(each peak is a list, with one rt, one area, and 1 or more values for chem name and 1 or more values
	for match percentage in lists within this list, which represents all peaks in a VOC sample)."""
	workbook = open_workbook(xls_filename)
	sheet = workbook.sheet_by_name(u'LibRes')
	number_of_rows = sheet.nrows 
	rt_area_name_qual_quadruples = []
	for row_index in range(9, number_of_rows):
        #extracting data from row 9 till last row in sheet
        #GC program puts no usable data until row 9
		#creates big list to put all of our information in
        # col 3 is area
        # col 8 is the chemical name
        # col 1 is RT
		# col 9 is hit quality percentage
		name_cell = sheet.cell(row_index, 8)
		qual_cell = sheet.cell(row_index, 9)
		if sheet.cell(row_index, 3).value:  #if there is a value in the area column for this row
			area_cell = sheet.cell(row_index, 3)
			area_value = area_cell.value
			rt_cell = sheet.cell(row_index, 1)
			rt_value = rt_cell.value
			name_value = [name_cell.value]
			qual_value = [qual_cell.value]
			rt_area_name_qual_quadruple = [rt_value, area_value, name_value, qual_value]
		#below deals with rows that have additional chemical hits but don't represent new peaks
		else:
			name_value = rt_area_name_qual_quadruple[2].append(name_cell.value)
			qual_value = rt_area_name_qual_quadruple[3].append(qual_cell.value)
		if row_index == (number_of_rows - 1): #if the sheet is ending, then add the completed quadruple to the list of quadruples
			rt_area_name_qual_quadruples.append(rt_area_name_qual_quadruple)
		elif sheet.cell(row_index + 1, 3).value: #if the next row index has a new area value (list of chems and quals that are matches
		#for a single given peak are complete), add the completed quadruple to list of quadruples
			rt_area_name_qual_quadruples.append(rt_area_name_qual_quadruple)
	return rt_area_name_qual_quadruples
	

def convert_RT_to_Kovats(RT, csvstr_of_alkane_n_RT):
	"""takes an RT (float) from a GCMS run and a string filepath to a csv of RTs and # of carbons for C7-C30 alkanes run with the
	same method as the sample GCMS run, and returns a Kovats index for that peak"""
	alkane_RT_dict = conv.read_unicode_csv_to_dict(csvstr_of_alkane_n_RT, 1,2) #alkane n is column 1(2) and alkane RT is column 2(3)
	alkane_dict = dict([int(key), float(value)] for key, value in alkane_RT_dict.iteritems())
	if RT > min(alkane_dict.values()) and RT < max(alkane_dict.values()):
		smaller_alkane_n = max([key for key in alkane_dict.keys() if alkane_dict[key] < RT])
		smaller_alkane_RT = alkane_dict[smaller_alkane_n]
		larger_alkane_n = min([key for key in alkane_dict.keys() if alkane_dict[key] > RT])
		larger_alkane_RT = alkane_dict[larger_alkane_n]
		Kovats = 100*(smaller_alkane_n + (larger_alkane_n - smaller_alkane_n)*((RT - smaller_alkane_RT)/(larger_alkane_RT - smaller_alkane_RT)))
		return Kovats
	else:
		return float('NaN')
		

def convert_chem_synonyms(chem_list, NIST_dict):
	"""takes list of chemicals and replaces each item in that list with the chosen synonym from the NIST_dict; 
	if item not in NIST_dict, then it returns the item"""
	for i in range(len(chem_list)):
		chem_list[i] = NIST_dict.get(chem_list[i], chem_list[i])
	return chem_list #all items converted to a single chemical synonym from NIST


def Kovats_db_to_list_of_tuples(Kovats_db_csv):
	""" reads csv of synonym converted Kovats db so that kovats and chem names are in matched tuples in a large list"""
	kovats = [float(item) for item in conv.read_unicode_csv_col_to_list(Kovats_db_csv, 0)]
	names = conv.read_unicode_csv_col_to_list(Kovats_db_csv, 1)
	Kovats_db_tups = []
	for i in range(0, len(kovats)):
		Kovats_db_tups.append((kovats[i], names[i]))
	return Kovats_db_tups
	
def find_Kovats_matches(peak_list, Kovats_db, int_KI_plusorminus, csvstr_of_alkane_n_RT, NIST_dict, Kovats_match_only = False):
	"""takes in a peak_list (one item from xls_list of lists), a csv of alkane info for generating Kovats with 
	the method you used for your GCMS run, the NIST-converted Kovats database (as list of tuples from Kovats_db_to_list_of_tuples) 
	and an integer value (Kovats_plusorminus) for the range around a peak's
	RT value that we should use to find potential matches in the Kovats database. Outputs a single chemical name that is the
	best match based on highest match percentage and having a match in the Kovats database that is within the Kovats_plusorminus
	of the peak's Kovats index value. Kovats match only means to keep only peaks that have both NIST and Kovats data; this is set
	to false by default, so by default if it is not possible to calculate Kovats or to find a match between NIST and Kovats results,
	then the top NIST hit will be retained."""
	RT = peak_list[0]
	area = peak_list[1]
	all_chems = convert_chem_synonyms(peak_list[2], NIST_dict)
	all_quals = peak_list[3]
	Kovats = convert_RT_to_Kovats(RT, csvstr_of_alkane_n_RT)
	if math.isnan(Kovats) == True: #if a Kovats value cannot be calculated
		if Kovats_match_only:
			return [] #delete this peak if Kovats can't be calculated and Kovats_match_only set to True
		else:
			return [RT, Kovats, area, all_chems[0], all_quals[0]] #if Kovats can't be calculated and Kovats_match_only is False, then return the top NIST match
	else: #if a Kovats value can be calculated	
		Kovats_chems = set([chem for KI, chem in Kovats_db if KI > (Kovats - int_KI_plusorminus) and KI < (Kovats + int_KI_plusorminus)])
		#get all unique chems from db within int_KI_plus or minus of experimental KI of our compound
		matches = Kovats_chems.intersection(set(all_chems))
		if not matches: #if there are no matches (empty set)
			if Kovats_match_only:
				return [] # if no matches btwn Kovats db and NIST for that peak, then delete peak
			else:
				return [RT, Kovats, area, all_chems[0], all_quals[0]] # if no matches btwn Kovats db and NIST for that peak, then return top NIST result
		else: #if we do have some matches, choose the NIST-Kovats chemical match with the highest NIST MS quality percentage
			top_qual = 0
			for item in matches:
				index = all_chems.index(item) #we can use the first index result because the quals list is sorted largest to smallest
				qual = all_quals[index]
				if qual > top_qual:
					top_qual = qual
					top_index = index
			top_match = all_chems[top_index]
			return [RT, Kovats, area, all_chems[top_index], all_quals[top_index]]
		
		

def process_whole_NIST_sheet(directory_for_files, xls_filename, Kovats_db, int_KI_plusorminus, csvstr_of_alkane_n_RT, NIST_dict, x_min_threshold = 3.5, NIST_qual_threshold= 70, Kovats_match_only = False, make_csv = True):
	"""takes in an xls filepath and returns a list of lists that is processed so that NIST MS IDs are confirmed with 
	Kovats index matches (if Kovats_match_only = True). Creates a csv that is put in the same folder as the original xls file if make_csv=True.
	Can specify the range around the compound Kovats to search for matches (int_KI_plusorminus), as well as a threshold to remove peaks before(eg, 
	if not all runs had a solvent delay). Can also specify a minimum MS match quality, where peaks are dicarded if they are not above that threshold"""
	if not os.path.exists(directory_for_files):
		os.makedirs(directory_for_files)
	all_peaks = get_rt_area_chemname_and_matchqual_from_gcms(xls_filename)
	all_peaks = [peak for peak in all_peaks if peak[0] > x_min_threshold] #keep only peaks whose RTs are after a threshold 
	all_peaks = [peak for peak in all_peaks if peak[3][0] > NIST_qual_threshold] #keep only peaks whose NIST match quality is above a certain threshold
	processed_peaks = []
	for i in range(0, len(all_peaks)): 
		peak = find_Kovats_matches(all_peaks[i], Kovats_db, int_KI_plusorminus, csvstr_of_alkane_n_RT, NIST_dict, Kovats_match_only)
		processed_peaks.append(peak)
	new_sheet = [peaks for peaks in processed_peaks if peaks != []]
	if make_csv:
		filename = xls_filename.rstrip(os.sep)
		#retain just file name, not full path, and put in chosen directory
		all_slash_indices = [i for i, char in enumerate(filename) if char == "/"]
		last_slash_index = all_slash_indices[-1]
		filename = filename[(last_slash_index + 1):]
		extension_index = filename.index(".xls")
		filename = filename[:extension_index]
		if Kovats_match_only:
			#csv_name = xls_filename.split(".xls")[0].strip() + "_Kovatsmatchonly.csv"
			csv_name = directory_for_files + filename + "_Kovatsmatchonly.csv"
		else:
			#csv_name = xls_filename.split(".xls")[0].strip() + "_processed.csv"
			csv_name = directory_for_files + filename + "_processed.csv"
		header_list = [u'RT', u'Kovats', u'Area', u'Chemical', u'MS_Match_Quality']
		u_new_sheet = []
		for index in range(0,len(new_sheet)):
			u_new_sheet.append([unicode(item) for item in new_sheet[index]]) 
		conv.write_unicode_lists_into_csv_listsasrows(csv_name, u_new_sheet, header_list)
	else:
		return new_sheet


def process_entire_directory_of_NIST_sheets_to_csv(directory_for_files, directory, Kovats_db, int_KI_plusorminus, csvstr_of_alkane_n_RT, NIST_dict, NIST_qual_threshold= 70, x_min_threshold = 3.5, Kovats_match_only = False, make_csv=True):
	"""takes in the filepath for a directory of raw MSRep excel files (and all of the arguments for to process an individual MSRep
	Excel file (process_whole_NIST_sheet)) and creates csvs of the processed data for each sample in the same directory"""
	print "start"
	xls_files = glob.glob(directory + "*.xls")
	for xls_filename in xls_files:
		process_whole_NIST_sheet(directory_for_files = directory_for_files, xls_filename=xls_filename, Kovats_db = Kovats_db, int_KI_plusorminus= int_KI_plusorminus, csvstr_of_alkane_n_RT =csvstr_of_alkane_n_RT , NIST_dict=NIST_dict, NIST_qual_threshold= NIST_qual_threshold, x_min_threshold=x_min_threshold, Kovats_match_only=Kovats_match_only, make_csv=make_csv)
	print "done"

#ALL ABOVE FXNS TESTED AND WORK!
		
#db = Kovats_db_to_list_of_tuples("Kovats_db_NISTsynonymconverted_140909_utf8.csv")	
#NIST_dict = conv.read_unicode_csv_to_dict("Kovats_db_NIST_dict.csv", 0, 1, header = False)
#lim_test=find_Kovats_matches(test[4], db, 10, "JEFFMETHOD_alkanes_for_Kovats.csv", NIST_dict, Kovats_match_only=False)
#th_test = process_whole_NIST_sheet("C:\\Users\\Marie\\Documents\\GRAD SCHOOL!\\Riffell Lab Research\\Theresa chemistry\\NIST Library\\050212_ththa707b_fl.xls", db, 10, "JEFFMETHOD_alkanes_for_Kovats.csv", NIST_dict, Kovats_match_only=False, make_csv=False)
#th_test2 = process_whole_NIST_sheet("C:\\Users\\Marie\\Documents\\GRAD SCHOOL!\\Riffell Lab Research\\Theresa chemistry\\NIST Library\\050212_ththa707b_fl.xls", db, 10, "JEFFMETHOD_alkanes_for_Kovats.csv", NIST_dict, Kovats_match_only=True, make_csv=False)
#process_whole_NIST_sheet("C:\\Users\\Marie\\Documents\\GRAD SCHOOL!\\Riffell Lab Research\\Theresa chemistry\\NIST Library\\050212_ththa707b_fl.xls", db, 10, "JEFFMETHOD_alkanes_for_Kovats.csv", NIST_dict, Kovats_match_only=False, make_csv=True)

#process_entire_directory_of_NIST_sheets_to_csv("C:\\Users\\Marie\\Documents\\GRAD SCHOOL!\\Riffell Lab Research\\Theresa chemistry\\NIST_Library_TEST", db, 10, "JEFFMETHOD_alkanes_for_Kovats.csv", NIST_dict, x_min_threshold = 3.5, Kovats_match_only = False, make_csv = True)

