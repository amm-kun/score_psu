# Author: Arjun Menon <amm8987@psu.edu>

"""
This file contains utility functions that are commonly used across scripts
"""

from os import path

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

# Validate if user entered valid file
def check_file(string):
    if path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)
