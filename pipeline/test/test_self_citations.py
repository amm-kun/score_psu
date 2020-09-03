from utilities import csv_writer, csv_write_field_header, csv_write_record
from extractor import TEIExtractor
from collections import namedtuple
from os import getcwd, listdir
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Test Self-Citations")
    # parser.add_argument("-in", "--xml_input", help="parent folder that contains all TEI XMLs")
    # parser.add_argument("-csv", "--csv_out", default=getcwd(), help="CSV output path")
    #
    args = parser.parse_args()

    args.xml_input = r"C:\Users\arjun\dev\GROBID_processed\test"
    args.csv_out = r"C:\Users\arjun\dev"

    fields = ('doi', 'title', 'filename', 'total_citations', 'self_citations')
    record = namedtuple('record', fields)
    record.__new__.__defaults__ = (None,) * len(record._fields)

    writer = csv_writer(r"{0}/{1}".format(args.csv_out, "self_citations_eval.csv"))
    header = list(fields)
    csv_write_field_header(writer, header)

    # Extract Data from XML and generate self-citations
    for count, filename in enumerate(listdir(args.xml_input)):
        print("Processing: ", filename, ", file number: ", count)
        extractor = TEIExtractor(args.xml_input + '/' + filename)
        payload = extractor.get_self_citations()
        payload['filename'] = filename
        csv_write_record(writer, payload, header)
