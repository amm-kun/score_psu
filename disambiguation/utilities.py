# Author: Arjun Menon <amm8987@psu.edu>

"""
This file contains utility functions that are commonly used across scripts
"""

from collections import namedtuple
from os import path
import csv

# Credentials for USPTO database on Breckenridge
mysql_breckenridge = {
    'user': 'kunho',
    'password': 'aubonpain1007',
    'host': 'breckenridge',
    'database': 'uspto_patent'}


patent_sections = {
    'A': 'Human Necessities',
    'B': 'Performing Operations; Transporting',
    'C': 'Chemistry; Metallurgy',
    'D': 'Textile; Paper',
    'E': 'Fixed Constructions',
    'F': 'Mechanical Engineering; Lighting; Heating; Weapons; Blasting Engines or Pumps',
    'G': 'Physics',
    'H': 'Electricity',
    'Y': 'General Tagging of New Technological Developments'
}

token_fields = ['title', 'section', 'subsection', 'group', 'sub_group', 'organization']
string_fields = ['name_first', 'name_last', 'city', 'state']

fields = ('patent_id', 'cluster', 'title', 'inventor_id', 'name_first', 'name_last', 'section', 'subsection',
          'group', 'sub_group',  'city', 'state', 'long_lat', 'organization')


# Validate if user entered valid file
def check_file(string):
    if path.isfile(string):
        return string
    else:
        raise FileNotFoundError(string)


# Return CSV writer object
def csv_writer(filename):
    writer = csv.writer(open(filename, 'w'))
    return writer


# Write header into CSV
def csv_write_field_header(writer, header):
    writer.writerow(header)


# Write dict based record into CSV in order
def csv_write_record(writer, record, header):
    nt_record = namedtuple('dis_features', header)
    sim_record = nt_record(**record)
    writer.writerow(list(sim_record))

