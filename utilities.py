# Author: Arjun Menon <amm8987@psu.edu>

"""
This file contains utility functions that are commonly used across scripts
"""

from os import path, listdir


# Validate if user entered valid directory path
def check_dir(string):
    if path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def fix_dir_path(dir_path):
    if dir_path.path[-1] != '/':
        dir_path.path += '/'
    return dir_path


# Generate list files to be ingested from specified dir
def parse_dir_xml(xml_dir):
    xml_files = []
    for filename in listdir(xml_dir):
        if not filename.endswith('.xml'):
            continue
        else:
            xml_files.append(filename)
    return xml_files


