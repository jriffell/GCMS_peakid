from bs4 import BeautifulSoup
import re, urllib, urllib2, os, requests
import pandas as pd


def lookup_by_name_on_NIST(cmpd):
	""" Takes the name of a chemical compound as a string and looks it up on the NIST chemical 
		webbook; returns the text of the site reached by searching for the input chemical"""
	url_safe_cmpd = urllib.quote(cmpd.encode('utf-8'))
	address = "http://webbook.nist.gov/cgi/cbook.cgi?Name=" + url_safe_cmpd + "&Units=SI"
	site_text = requests.get(address).text 
	#this is site_text input for parse_text_from_NIST_site or 
	#for find_link_if_directed_to_search_page
	return BeautifulSoup(site_text)
	
def find_link_if_directed_to_search_page(BeautifulSoup_sitetext):
	""" If initial chemical search through NIST ends up
		on a search results page with multiple links to 
		different chemical pages, choose the link to 
		the first chemical page"""
	soup = BeautifulSoup_sitetext
	links = soup.find_all('a')
	l = links[0].get('href', None)
	link_to_chem = "http://webbook.nist.gov" + l
	chem_sitetext = requests.get(link_to_chem).text 
	return BeautifulSoup(chem_sitetext)

def find_permanent_link(BeautifulSoup_sitetext):
	"""If there is a Permanent link to a page for a compound
	right after the list of 'Other names' instead of 'Information on this page',
	then follow the link to the permanent page and use this page to scrape instead"""
	perma_link = BeautifulSoup_sitetext.find_all('a', href=True, text="Permanent link")
	l = perma_link[0].get('href', None)
	link_to_chem = "http://webbook.nist.gov" + l
	chem_sitetext = requests.get(link_to_chem).text
	return BeautifulSoup(chem_sitetext)




	
def parse_stereoisomer_list_from_NIST_site(BeautifulSoup_sitetext):
	""" Takes the HTML text from the NIST lookup site and finds all stereoisomers for the
	chemical in question; puts these in a list. Includes chemicals in "species with the same
	structure" as these are usually more general names for the compounds in question, and NIST
	is inconsistent in whether they count these as "other species with the same structure" or 
	"stereoisomers".
	"""
	soup = BeautifulSoup_sitetext

	#find all stereoisomers of our compound on the page and put them in a list
	htmlless = soup.text #removes html tags, makes a unicode string
	#nless = re.sub("\n", " ", htmlless) #removes line breaks
	stereoisomer_list = []
	if htmlless.find("Stereoisomers:") > 0 and htmlless.find("Other names") > 0:
		#if page contains a section for Stereoisomers and is followed by a section entitled "Other names", return a list of these
		stereoisomer_text = htmlless[htmlless.find("Stereoisomers:") + 14 : htmlless.find("Other names")]
		stereoisomer_split = stereoisomer_text.split("\n")
		for item in stereoisomer_split:
			if item:
				stereoisomer_list.append(item)
	elif htmlless.find("Stereoisomers:") > 0 and htmlless.find("Other names") <= 0:
		#if page contains section for stereoisomers, but no section for other names to bookend it
		for stereoisomer in soup.find("strong", text = "Stereoisomers:").parent.find("ul").stripped_strings:
			stereoisomer_list.append(stereoisomer)

	if htmlless.find("Species with the same structure:") > 0:
		#if page contains section for species with the same structure
		for chemical in soup.find("strong", text = "Species with the same structure:").parent.find("ul").stripped_strings:
			stereoisomer_list.append(chemical)
	main_chem = soup.find('h1').text.strip()
	stereoisomer_list.append(main_chem)

	return stereoisomer_list



def find_stereoisomer_links_from_NIST_site(BeautifulSoup_sitetext, stereoisomer_list):
	"""Finds all links to stereoisomer pages from the main compound page and puts them into a list; returns list of links
	"""
	soup = BeautifulSoup_sitetext
	link_prefix = "http://webbook.nist.gov"
	list_of_links = []
	list_of_stereoisomer_lists = [stereoisomer_list]
	for isomer in stereoisomer_list:
		link_suffix = soup.findAll('a', href = True, text = isomer)
		#the main chemical whose page you're on, which should be the last item in the isomer list should
		#not have a link corresponding to it; this allows the function to be ok with skipping it.
		if link_suffix:
			link_suffix = link_suffix[0]['href']
			list_of_links.append(link_prefix + link_suffix)
	return list_of_links




def arrive_at_correct_page(BS_sitetext):
	""" Makes sure that the best page for the chemical in question is arrived at when doing
		when moving to a link associated with a stereoisomer from a previous page or after doing a
		chemical search using lookup_by_name_on_NIST;
		return BS_chem_site for that correct page for further processing
	"""

	header = BS_sitetext.find('h1').text
	if header == u'Name Not Found': #compound not in NIST database
		return []
	elif header == u'Search Results': #multiple matches for search
		BS_chem_site = find_link_if_directed_to_search_page(BS_sitetext)
		if BS_chem_site.find_all('a', href=True, text="Permanent link") != []:
		#going to the 'permanent link' for a compound if it exists
		#because this takes the place of 'Other Information' that usually marks
		#the end of the synonyms ('Other names') list
			BS_chem_site = find_permanent_link(BS_chem_site)
		return BS_chem_site
	else: #compound page reached (header =  compound name or synonym)
		if BS_sitetext.find_all('a', href=True, text="Permanent link") != []:
		#going to the 'permanent link' for a compound if it exists
		#because this takes the place of 'Other Information' that usually marks
		#the end of the synonyms ('Other names') list
			BS_chem_site = find_permanent_link(BS_sitetext)
			return BS_chem_site
		else:
			#otherwise, should have correct page!:
			return BS_sitetext





def find_comprehensive_stereoisomer_list(cmpd):
	"""Takes the HTML text from the NIST lookup site and finds all stereoisomers for the
	chemical in question; puts these in a list. Then looks up the links to those other stereoisomers to make sure the
	list of stereoisomers is comprehensive. After this, chooses the shortest name in the find_all
	list of stereoisomers to be the dictionary value for all items in the list, which will be keys.
	This will allow us to convert all stereoisomers into the same name after the full processing of
	the chemical datasheets occurs, to help us sift through fewer chemicals in the multivariate analysis."""
	BS_sitetext = lookup_by_name_on_NIST(cmpd)
	BS_sitetext = arrive_at_correct_page(BS_sitetext)

	#if any webbook search results for a particular compound, find all stereoisomers and links to those
	#pages and find all stereoisomers in those links and add them to the list as well; if there are not
	#search results for a particular compound, then return a list containing just the cmpd
	if BS_sitetext:
		list_of_stereoisomers = parse_stereoisomer_list_from_NIST_site(BS_sitetext)
		list_of_stereoisomer_links = find_stereoisomer_links_from_NIST_site(BS_sitetext, list_of_stereoisomers)

		list_of_stereoisomer_lists = [list_of_stereoisomers]
		for link in list_of_stereoisomer_links:
			link_text = requests.get(link).text 
			#this is site_text input for parse_text_from_NIST_site or 
			#for find_link_if_directed_to_search_page
			BS_linktext =  BeautifulSoup(link_text)
			BS_linktext = arrive_at_correct_page(BS_linktext)
			stereoisomer_list_in_link = parse_stereoisomer_list_from_NIST_site(BS_linktext)
			list_of_stereoisomer_lists.append(stereoisomer_list_in_link)
		flat_list_of_stereoisomers = [item for sublist in list_of_stereoisomer_lists for item in sublist]
		
		#make sure cmpd itself is in list as well (since this is the item that was returned by our synonyms dictionary)
		flat_list_of_stereoisomers.append(unicode(cmpd))
		#keep unique stereoisomer names
		list_of_all_unique_stereoisomers = list(set(flat_list_of_stereoisomers))
		#remove any empty strings if they happen to be in there...
		list_of_all_unique_stereoisomers = [item for item in list_of_all_unique_stereoisomers if item]
	else:
		list_of_all_unique_stereoisomers = [cmpd]


	return list_of_all_unique_stereoisomers



def scrape_chem_stereoisomers_from_NIST_and_create_dict(cmpd, st_dict):
	""" Takes a compound string and dictionary and returns the 
	dictionary with all stereoisomers for a given compound as keys,
	with values as the shortest stereoisomer found from the nist webbook (a single 
	stereoisomer) added to the original dictionary. Uses only chemical names that
	are headers in the NIST webbook, since our chemical synonym dictionary
	already converts other chemical names to these single header synonyms.
	Only performs search for compounds not already in dictionary for speed."""

	if cmpd not in st_dict.keys():
		list_of_all_unique_stereoisomers = find_comprehensive_stereoisomer_list(cmpd)

		for i in range(0,len(list_of_all_unique_stereoisomers)):
			if i == 0:
				shortest_len = len(list_of_all_unique_stereoisomers[0])
				shortest_index = 0
			else:
				if len(list_of_all_unique_stereoisomers[i]) < shortest_len:
					shortest_len = len(list_of_all_unique_stereoisomers[i])
					shortest_index = i


		shortest_stereoisomer = list_of_all_unique_stereoisomers[shortest_index]

		for item in list_of_all_unique_stereoisomers:
			if item not in st_dict.keys():
				st_dict[item] = shortest_stereoisomer

	return st_dict


def scrape_whole_list_of_stereoisomers_from_NIST_and_create_dict(syn_dict, st_dict):
	"""Takes a whole list of compounds from the synonym dictionary
	and a dictionary and returns the dictionary
	with all stereoisomers for a given compound as keys,
	with values as the shortest stereoisomer found from the nist webbook (a single 
	stereoisomer) added to the original dictionary. Uses only chemical names that
	are headers in the NIST webbook, since our chemical synonym dictionary
	already converts other chemical names to these single header synonyms.
	"""
	cmpd_list = list(set(syn_dict.values()))
	for cmpd in cmpd_list:
		st_dict = scrape_chem_stereoisomers_from_NIST_and_create_dict(cmpd, st_dict)
		print cmpd
	return st_dict


def convert_chemical_matrix_with_stereoisomer_dict(chem_mat_csv_path, stereo_dict, output_csv_path):
	"""Convert all chemical synonymns in the chemical data matrix into a single one of its stereoisomers
	and then change chemical data matrix so that rows that correspond to chemicals that are now a single
	stereoisomer are added together. Outputs a csv of this new chemical data matrix.
	Arguments:
	chem_mat_csv_path : filepath to original chemical data csv
	stereo_dict : dictionary of stereoisomers generated from scrape_stereoisomers_from_NIST_webbook scripts
	output_csv_path : desired filepath to processed csv (stereoisomer converted)
	"""
	#read in original chemical data matrix, maintaining unicode encoding
	chem_df = pd.read_csv(chem_mat_csv_path, encoding = "utf-8")
	# chem_names_ordered_list = chem_df.iloc[:,0].tolist()

	# #converting chemicals with stereoisomer dictionary
	# converted_chems_ordered_list = []
	# for i in range(0, len(chem_names_ordered_list)):
	# 	converted = stereo_dict.get(chem_names_ordered_list[i], chem_names_ordered_list[i])
	# 	converted_chems_ordered_list.append(converted)
	for i in range(0, chem_df.shape[0]):
		chem_df.iloc[i, 0] = stereo_dict.get(chem_df.iloc[i,0], chem_df.iloc[i,0])

	#summing rows with the corresponding to the same stereoisomer
	grouped = chem_df.groupby(chem_df.columns.values[0])
	summed_chem_df = grouped.sum()

	#outputting to csv
	summed_chem_df.to_csv(output_csv_path, encoding = "utf-8")
	print "done!"






