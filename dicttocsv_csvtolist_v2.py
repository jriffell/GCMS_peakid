import csv, codecs,cStringIO
from xlrd import open_workbook
from collections import defaultdict

class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
			


#write a dictionary to a csv
def write_unicode_dict_to_csv(namestr_dotcsv, dict):
	"""Writes a Python dictionary into a csv with keys as first
	column and values as second; allows us to store and quickly 
	read back in dictionaries for synonym conversion"""
	with open(namestr_dotcsv, 'wb') as f:
		writer = UnicodeWriter(f, quoting=csv.QUOTE_ALL)
		for key, value in dict.items():
			writer.writerow([key, value])

#read a csv into a dictionary

def read_unicode_csv_to_dict(dictstr_dotcsv, key_col_index, value_col_index, header=True):	
	"""Reads a csv into a Python dictionary;
	where you specify column indices for the keys and values (ints)"""	
	with open(dictstr_dotcsv, 'rb') as f:
		if header:
			f.readline()
		my_dict={}
		reader = UnicodeReader(f)
		for rows in reader:
			k = rows[key_col_index]
			v = rows[value_col_index]
			my_dict[k] = v
	return my_dict
	
		
##from csv into list
def read_unicode_csv_col_to_list(namestr_dotcsv, col_index, header=True):
	"""Reads the chosen column (given column index as col_index)
	from a unicode-containing
	csv (for which you provide filepath as argument) into
	a Python list; if there is a header, skip 1st line """
	with open(namestr_dotcsv, 'rb') as f:
		my_list = []
		if header:
			f.readline()
		reader = UnicodeReader(f)
		for rows in reader:
			my_list.append(rows[col_index])
	return my_list
	

##csv to list of tuples for Kovats db
def Kovats_db_to_list_of_tuples(Kovats_db_csv):
	""" reads csv of synonym converted Kovats db so that kovats and chem names are in matched tuples in a large list"""
	kovats = [float(item) for item in conv.read_unicode_csv_col_to_list(Kovats_db_csv, 0)]
	names = conv.read_unicode_csv_col_to_list(Kovats_db_csv, 1)
	Kovats_db_tups = []
	for i in range(0, len(kovats)):
		Kovats_db_tups.append((kovats[i], names[i]))
	return Kovats_db_tups	


def read_unicode_csv_to_list_of_lists(namestr_dotcsv, header=True):
	""" Reads an entire utf-8 encoded csv into lists column by
	column in the order that they appear in the csv. Omits
	column headers from lists if header=True"""
	with open(namestr_dotcsv, 'rb') as f:
		reader = UnicodeReader(f)
		ncol=len(next(reader))
		my_list_of_lists = [list() for _ in xrange(ncol)]
		f.seek(0,0)
		reader = UnicodeReader(f)
		if header:
			f.readline()
		for row in reader:
			for col_index in range(ncol):
				my_list_of_lists[col_index].append(row[col_index])
	return my_list_of_lists
	
	
##from list back into single csv column
def write_unicode_list_into_unicode_csv(namestr_dotcsv, my_list):
	with open(namestr_dotcsv, 'wb') as f:
		writer = UnicodeWriter(f)
		for item in my_list:
			writer.writerow([item])

##lists to csv with multiple columns where each list is a column
def write_unicode_lists_to_csv_cols_head(namestr_dotcsv, list_of_headers, *lists):	
	"""Takes in a string to name the csv, a list of headers,
	and utf-8 lists in the order that they appear in the list of headers
	and writes them to a utf-8 encoded csv"""
	rows = zip(*lists)
	#rows = [list(rows) for row in rows]
	with open(namestr_dotcsv, 'wb') as f:
		writer = UnicodeWriter(f)
		writer.writerow(list_of_headers)
		for row in rows:
			writer.writerow(row)

##lists to csv with multiple columns where each list is a row
def write_unicode_lists_into_csv_listsasrows(namestr_dotcsv, my_list_of_lists, list_of_headers):
	with open(namestr_dotcsv, 'wb') as f:
		writer = UnicodeWriter(f)
		writer.writerow(list_of_headers)
		for item in my_list_of_lists:
			writer.writerow(item)
		
	


##from excel file into list

##from list back into excel column