import os
os.chdir("C:\\Users\Marie\Documents\GRAD SCHOOL!\Riffell Lab Research\Theresa chemistry\Python")

import scrape_synonyms_from_NIST_webbook_v4 as scrape
import dicttocsv_csvtolist as conv
import codecs

#importing list of chemicals in Kovats db to create
#webscraped NIST synonym dictionary for all compounds contained
#therein
#with open('VOC_Kovats_onlycmpds_utf8.txt', 'r') as f:
#	VOC_list = f.readlines()
	
with codecs.open('VOC_Kovats_onlycmpds_utf8.txt', encoding='utf-8') as f:
	VOC_list=f.readlines()

#removing newline (\r\n) character from end of all items in list	
#takes in list of unicode strings and puts out list of unicode strings
nless_VOC_list = []
for item in VOC_list:
	chem = item.split("\r\n")[0].strip()
	nless_VOC_list.append(chem)	
#	chem = str(item).split("\n")[0].strip()
#	nless_VOC_list.append(chem.decode('unicode-escape'))
	
#nless_test = []
#for item in my_list[0:10]:
#	chem = str(item).split("\n")[0].strip()
#	nless_test.append(chem.decode('unicode-escape'))
	
#using this to make a webscraped dictionary from NIST

Kovats_dict={}
scrape.scrape_whole_list_from_NIST(nless_VOC_list, Kovats_dict)

conv.write_unicode_dict_to_csv("Kovats_db_NIST_dict.csv", Kovats_dict)


#dict={}
#scrape.scrape_chem_synonyms_from_NIST('ocimene', dict)
