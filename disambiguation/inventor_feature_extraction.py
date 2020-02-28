# Author: Arjun Menon <amm8987@psu.edu>

"""
This script performs lookups on the USPTO PatentsView
database to build a CSV dataset for the task of Inventor Disambiguation
given a .txt file input which contains a list of inventor IDs.

Usage: inventor_feature_extraction.py -f <input>
"""

from utilities import mysql_breckenridge, check_file, patent_sections
from mysql_conn import connect_db
import argparse
import csv

con = connect_db(**mysql_breckenridge)
# Get Cursor object
cursor = con.cursor()

writer = csv.writer(open("inventors.csv", 'w'))
writer.writerow(['patent_id', 'inventor_id', 'name_first', 'name_last', 'section', 'subsection',
                 'group', 'sub_group',  'city', 'state', 'long|lat', 'organization'])
# Co-authors for patent?

parser = argparse.ArgumentParser(description='Specify target inventor list')
parser.add_argument('-f', '--file', help='specify the inventor list txt file', type=check_file)
file = parser.parse_args()

inventor_ids = []
with open(file.file) as inventor_list:
    for inventor in inventor_list:
        patent_id, sequence = inventor.split()[0].split('-')
        inventor_ids.append([patent_id, sequence])

for inventor in inventor_ids:
    patent_id, sequence = inventor

    inventor_query = ("SELECT inventor_id, rawlocation_id, name_first, name_last FROM rawinventor WHERE"
                      " patent_id = {0} and sequence = {1}".format(patent_id, sequence))
    try:
        cursor.execute(inventor_query)
    except TypeError as e:
        print(e)
        print("Couldn't process ", patent_id)
        continue
    (inventor_id, rawloc_id, name_first, name_last) = cursor.fetchone()

    loc_query = "SELECT location_id, city, state from rawlocation where id = '{0}'".format(rawloc_id)
    cursor.execute(loc_query)
    try:
        (long_lat, city, state) = cursor.fetchone()
    except TypeError as e:
        print(e)
        print("Couldn't process ", patent_id)
        continue

    # Patent may have several classes, for now info for the first primary class is retrieved
    class_query = ("SELECT current.patent_id, current.section_id, cpc_subsection.title as sub_sec, "
                   "cpc_group.title as cpc_group, cpc_subgroup.title as cpc_subgroup "
                   "FROM cpc_current current "
                   "LEFT JOIN cpc_subsection on current.subsection_id = cpc_subsection.id "
                   "LEFT JOIN cpc_group on current.group_id = cpc_group.id "
                   "LEFT JOIN cpc_subgroup on current.subgroup_id = cpc_subgroup.id "
                   "WHERE current.patent_id = '{0}' AND current.category='primary' "
                   "AND current.sequence=0".format(patent_id))
    cursor.execute(class_query)
    try:
        (pat_id, cpc_section_id, cpc_subsec, cpc_group, cpc_subgroup) = cursor.fetchone()
        cpc_section = patent_sections[cpc_section_id]
    except TypeError as e:
        print(e)
        print("Couldn't process ", patent_id)
        continue

    organization_query = "SELECT organization FROM rawassignee where patent_id = '{0}'".format(patent_id)
    cursor.execute(organization_query)
    try:
        organization = cursor.fetchone()
    except TypeError as e:
        print(e)
        print("Couldn't process ", patent_id)
        continue

    writer. writerow([patent_id, inventor_id, name_first, name_last, cpc_section, cpc_subsec,
                      cpc_group, cpc_subgroup, city, state, long_lat, organization[0]])

    print("CSV record for inventor:", inventor, " inserted")
