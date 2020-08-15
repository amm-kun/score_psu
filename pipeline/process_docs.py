from utilities import read_darpa_tsv, csv_writer, csv_write_field_header, csv_write_record
from extractor import TEIExtractor
from p_value import extract_p_values
from collections import namedtuple
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Pipeline - Process PDFS - Market Pre-processing")
    parser.add_argument("-in", "--pdf_input", help="parent folder that contains all pdfs")
    parser.add_argument("-out", "--grobid_out",  help="grobid output path")
    parser.add_argument("-m", "--mode", default="processFulltextDocument", help="grobid mode")
    parser.add_argument("-n", default=1, help="concurrency for service usage")
    parser.add_argument("-f", "--file", help="DARPA tsv for test")

    args = parser.parse_args()

    fields = ('ta3_pid', 'title', 'num_citations', 'author_count', 'sjr', 'u_rank', 'num_hypo_tested', 'real_p',
              'real_p_sign', 'p_val_range', 'num_significant', 'sample_size', "extend_p", "funded")
    record = namedtuple('record', fields)
    record.__new__.__defaults__ = (None,) * len(record._fields)

    # CSV output file
    writer = csv_writer(r"C:\Users\arjun\dev\test.csv")
    header = list(fields)
    csv_write_field_header(writer, header)

    # Debug parameters
    args.mode = "extract-test"
    args.grobid_out = r"C:\Users\arjun\dev\GROBID_processed\test"
    args.pdf_input = r"C:\Users\arjun\dev\test\pdfs"
    args.file = r"C:\Users\arjun\dev\covid_ta3.tsv"

    # Read tsv
    if args.mode == "extract-test":
        for document in read_darpa_tsv(args.file):
            print("Processing ", document['pdf_filename'])
            extractor = TEIExtractor(args.grobid_out + '/' + document['pdf_filename'] + '.tei.xml')
            extraction_stage = extractor.extract_paper_info()
            p_val_stage = extract_p_values(args.pdf_input + '/' + document['pdf_filename'] + '.txt', document['claim4'])
            features = dict(**extraction_stage, **p_val_stage)
            features['ta3_pid'] = document['ta3_pid']
            try:
                csv_write_record(writer, features, header)
            except UnicodeDecodeError:
                print("CSV WRITE ERROR", features["ta3_pid"])
            except UnicodeEncodeError:
                print("CSV WRITE ERROR", features["ta3_pid"])
