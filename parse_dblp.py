# Author: Arjun Menon <amm8987@psu.edu>

"""
This script allows you to parse XML documents into JSON format and
perfrom inserts to a MongoDB instance. Current version is hardcoded
to perform inserts to localhost, default port to a specified DB instance
and collection. The path to the XML dir can be specified by using the -p
/--path option. Default behavior if not specified is to use the script's
local directory
"""

import xml.etree.ElementTree as EleT
from lxml import etree
import argparse
from os import path, listdir, getcwd, chdir
from pymongo import MongoClient


# Connect to DB Instance
def connect_db():
    client = MongoClient('localhost', 27017)
    db_obj = client['dblp']
    return db_obj, client


# Single insert into collection
def insert_record(db_obj, collection, record):
    records = db_obj[collection]
    result = records.insert_one(record)
    print("Insert successful with ID: ", result.inserted_id)


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
            if not isinstance(final[tag], list):
                final[tag] = [final[tag]]
                final[tag].append(result)
            else:
                final[tag].append(result)
        else:
            final[tag] = result
    return final


# Generate list of XML files to be ingested from specified dir
def parse_dir_xml(xml_dir):
    xml_files = []
    for filename in listdir(xml_dir):
        if not filename.endswith('.xml'):
            continue
        else:
            xml_files.append(filename)
    return xml_files


# Validate if user entered valid directory path
def dir_path(string):
    if path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


parser = argparse.ArgumentParser(description='Specify Target XML Directory')
parser.add_argument('-p', '--path', help='full path to XML directory', type=dir_path, default=getcwd())
xml_path = parser.parse_args()
if xml_path.path[-1] != '/':
    xml_path.path += '/'

# Connect to DB
db, session = connect_db()
xml = parse_dir_xml(xml_path.path)
chdir(xml_path.path)

# Initializing the Parser Object
parser = etree.XMLParser(dtd_validation=True)

for doc in xml:
    print('Parsing ', doc)
    count = 0
    tree = EleT.parse(doc, parser=parser)
    root = tree.getroot()
    for child in root.getchildren():
        json_record = parse_children([child])
        for key in json_record.keys():
            insert_record(db, key, json_record[key])
        count += 1
    print("Ingestion completed for ", doc)
