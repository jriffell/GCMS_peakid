from xlrd import open_workbook #loading open_workbook package from xlrd library
import csv



def get_cas_and_name_and_area_from_gcms(xls_filename):
    """
    reads in gcms excel data from file name passed in; returns a list of
    chemicals and their areas
    """
    #makes a doc string (what interpreter brings up if you help(fxn))


    
    workbook = open_workbook(xls_filename)

    sheet = workbook.sheet_by_name(u'LibRes')
    #our relevant data is in sheet 'LibRes';
    #u = unicode (allows Python to represent odd characters like Greek, etc.)
    cas_and_name_and_area_triples = []
    #creates big list of single chem name and area pair lists

    number_of_rows = sheet.nrows 
    for row_index in range(9, number_of_rows):
        #extracting data from row 9 till last row in sheet
        #GC program puts no usable data until row 9

        # col 3 is area
        # col 8 is the chemical name
        # col 11 is cas number
        area_cell = sheet.cell(row_index, 3)
        area_value = area_cell.value
        if not area_value:
            continue
        name_cell = sheet.cell(row_index, 8)
        name_value = name_cell.value
        cas_cell = sheet.cell(row_index, 11)
        cas_value = cas_cell.value
        cas_name_area_triple = [cas_value, name_value, area_value]

        
        cas_and_name_and_area_triples.append(cas_name_area_triple)
    return cas_and_name_and_area_triples

def write_to_csv(filename, rows, header=None):
    """writes a csv with specified row data and header"""
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        if header is not None:
            writer.writerow(header)
        for row in rows:
            writer.writerow(row)
