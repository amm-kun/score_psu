# Author: Arjun Menon <amm8987@psu.edu>

"""
This script allows you to parse XML documents into JSON format and
perfrom inserts to a MongoDB instance. Current version is hardcoded
to perform inserts to localhost, default port to a specified DB instance
and collection. The path to the XML dir can be specified by using the -p
/--path option. Default behavior if not specified is to use the script's
local directory
"""

from ingestion.utilities import check_dir, parse_dir_xml, fix_dir_path
from ingestion.mongo_conn import connect_db, insert_record
from os import getcwd
import xml.etree.ElementTree as EleT
import argparse


# Splits tag into uri and tag fields in cases where there is a namespace
def split_name_space(tag):
    if tag[0] == "{":
        return tag[1:].split("}")
    else:
        return None, tag


# Parse through the attribute fields of a tag into key, value pairs at outermost level
def parse_attributes(attribs):
    ns = set()
    for attrib in attribs.keys():
        # Namespace Handler - since we do not care about namespaces, they are ignored
        if ':' in attrib:
            return {}
    if len(ns) == 0:
        return attribs
    else:
        result = {}
        for x in ns:
            result[x] = {}
        for attrib, value in attribs.items():
            if ':' in attrib:
                thisns, tag = attrib.split(':')
                result[thisns]['@' + tag] = value
            else:
                result[attrib] = value
        return result


# Recursion function
def parse_children(tags):
    final = {}
    for x in tags:
        prepend = {}
        result = ''
        uri, tag = split_name_space(x.tag)
        # Handle tags attributes
        if len(x.attrib) > 0:
            prepend = dict(**parse_attributes(x.attrib))

        # Construct result json
        if len(x) == 0:
            if x.text is not None:
                if len(prepend) == 0:
                    result = x.text
                else:
                    result = dict(**prepend, **{tag: x.text})
            else:
                if len(prepend) > 0:
                    result = prepend
        else:
            if len(prepend) == 0:
                result = parse_children(x.getchildren())
            else:
                result = dict(**prepend, **parse_children(x.getchildren()))

        # If tag is a list of elements, append result to the list --make nested
        if tag in final:
            if isinstance(final[tag], list):
                final[tag] = [final[tag]]
                final[tag].append(result)
        else:
            final[tag] = result
    return final


parser = argparse.ArgumentParser(description='Specify Target XML Directory')
parser.add_argument('-p', '--path', help='full path to XML directory', type=check_dir, default=getcwd())
xml_path = parser.parse_args()

# Connect to DB
db, session = connect_db('WoS')
xml = parse_dir_xml(xml_path.path)

for doc in xml:
    print('Parsing ', doc)
    count = 0
    xml_path = fix_dir_path(xml_path)
    tree = EleT.parse(xml_path.path+doc)
    root = tree.getroot()
    for child in root.getchildren():
        json_record = parse_children([child])
        insert_record(db, 'records', json_record['REC'])
        count += 1
    print('Completed ingestion for ', doc, '\n Inserted ', count, 'documents')
