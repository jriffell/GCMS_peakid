from bs4 import BeautifulSoup
import re, urllib, urllib2, os, requests


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

	
def parse_text_from_NIST_site(BeautifulSoup_sitetext, dict):
	""" Takes the HTML text from the NIST lookup site and adds the title chemical
		as well as all of the chemical synonyms listed on the page as keys in a dictionary.
		All values are the title chemical. This will allow us to convert all chemical
		synonyms in our data sheets and kovats databases into a single name, so that we
		can search and match."""
	soup = BeautifulSoup_sitetext
	htmlless = soup.text #removes html tags, makes a unicode string
	nless = re.sub("\n", " ", htmlless) #removes line breaks
	#main_chem_start_index = nless.find("ChemistryWebBook", 0, len(nless)) +16
	#main_chem_end_index = nless.find("Formula", 0, len(nless))
	#main_chem = nless[main_chem_start_index : main_chem_end_index].strip()
	main_chem = soup.find('h1').text.strip()
	if main_chem in dict: 
		pass
	else:
		val = main_chem
		dict[val] = val
		if nless.find("Other names", 0, len(nless))> 0:	#adds synonyms only if there are "Other names" on NIST site
			other_start_index = nless.find("Other names", 0, len(nless)) +13
			other_end_index = nless.find("Information on this page:  Notes ", 0, len(nless))
			indiv_synonyms = nless[other_start_index : other_end_index]. split(";")
			for indiv_synonym in indiv_synonyms:
				indiv_synonym = indiv_synonym.strip()
				dict[indiv_synonym] = val
	#REMEMBER, ALL VALUES ARE UNICODE STRINGS
	#WHEN WRITING MATCHING CODE, NEED TO MAKE SURE MATCHES
	#ARE IN UNICODE TOO


def scrape_chem_synonyms_from_NIST(cmpd, dict):
	""" Takes a compound string and dictionary and returns the 
	dictionary with all synonyms for a given compound as keys,
	with values as the header from the nist webbook (a single 
	synonym) added to the original dictionary. Accounts for the
	three different results you can get when you do the initial
	search in NIST (Name Not Found, mulitple results, one chem result)"""
	BS_sitetext = lookup_by_name_on_NIST(cmpd)
	header = BS_sitetext.find('h1').text
	if header == u'Name Not Found': #compound not in NIST database
		dict[unicode(cmpd)] = unicode(cmpd)
	elif header == u'Search Results': #multiple matches for search
		BS_chem_site = find_link_if_directed_to_search_page(BS_sitetext)
		if BS_chem_site.find_all('a', href=True, text="Permanent link") != []:
		#going to the 'permanent link' for a compound if it exists
		#because this takes the place of 'Other Information' that usually marks
		#the end of the synonyms ('Other names') list
			BS_chem_site = find_permanent_link(BS_chem_site)
		head_chem = BS_chem_site.find('h1').text
		parse_text_from_NIST_site(BS_chem_site, dict)
		if cmpd not in dict:
				dict[unicode(cmpd)] = head_chem
	else: #compound page reached (header =  compound name or synonym)
		if BS_sitetext.find_all('a', href=True, text="Permanent link") != []:
		#going to the 'permanent link' for a compound if it exists
		#because this takes the place of 'Other Information' that usually marks
		#the end of the synonyms ('Other names') list
			BS_sitetext = find_permanent_link(BS_sitetext)
		parse_text_from_NIST_site(BS_sitetext, dict)
		if cmpd not in dict:
			dict[unicode(cmpd)] = header
	return dict 

def scrape_whole_list_from_NIST(cmpd_list, dict):
	for compound in cmpd_list:
		if compound not in dict.keys():
			dict = scrape_chem_synonyms_from_NIST(compound, dict)
	return dict