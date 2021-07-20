from utilities import read_darpa_tsv, csv_writer, csv_write_field_header, csv_write_record, select_keys, \
    tamu_select_features
from grobid_client.grobid_client import run_grobid
from extractor import TEIExtractor
from p_value import extract_p_values
from tamu_features.adapter import get_tamu_features
from collections import namedtuple
from os import listdir, rename, system, name, path, getcwd
from databases import Database
import time
import argparse
import random
import traceback
import pandas as pd
import logcontrol
import timelogger
import pdb
import subprocess
import os
import shutil

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Pipeline - Process PDFS - Market Pre-processing")
    parser.add_argument("-in", "--pdf_input", help="parent folder that contains all pdfs")
    parser.add_argument("-out", "--grobid_out",  help="grobid output path")
    parser.add_argument("-m", "--mode", default="extract-test", help="pipeline mode")
    parser.add_argument("-n", default=1, help="concurrency for service usage")
    parser.add_argument("-f", "--file", help="DARPA metadata tsv/csv for test")
    parser.add_argument("-csv", "--csv_out", default=getcwd(), help="CSV output path")
    parser.add_argument("-l", "--label", help="Assign y value | label for training set")
    parser.add_argument("-lr", "--label_range", help="Assign y value within range for training set | Ex: 0.7-1")

    #python process_docs.py -out ../../tei10 -in ../../pdf10 -m generate-train" -csv ../
    database_path = path.expanduser('~/data/database')
    database = Database(database_path)
  
    args = parser.parse_args()
    logcontrol.register_logger(timelogger.logger, "timelogger")
    logcontrol.set_level(logcontrol.DEBUG, group="timelogger")
    #logcontrol.log_to_console(group="timelogger")
    logcontrol.set_log_file(args.csv_out + '/main_log.txt')

    # Debug parameters config
    #args.mode = "extract-test"
    #args.grobid_out = r"C:\Users\arjun\dev\GROBID_processed\test"
    #args.pdf_input = r"C:\Users\arjun\dev\test\pdfs"
    args.data_file = r"~/data/2400set/data.csv"
    #args.csv_out = r"C:\Users\arjun\dev"

    # Process PDFS -> Generate XMLs and txt files
    if args.mode == "process-pdfs":
        # Change pdf names (Some PDFs have '-' instead of '_' in the names)
        for count, filename in enumerate(listdir(args.pdf_input)):
            print("Processing: ", filename, ", file number: ", count)
            new_name = filename.replace('-', '_')
            rename(args.pdf_input+'/'+filename, args.pdf_input+'/'+new_name)
            # Generate text files from PDFs
            if name == 'nt':
                command = r"C:\Users\arjun\dev\xpdf-tools-win-4.02\bin64\pdftotext {0}/".format(args.pdf_input) + \
                          filename
            else:
                command = "pdftotext {0}/{1}".format(args.pdf_input, filename)
            system(command)
        # Process PDFs to generate GROBID TEI XML
        run_grobid(args.pdf_input, args.grobid_out, args.n)

    # Generate Training data
    elif args.mode == "generate-train":

        fields = ('doi', 'title', 'num_citations', 'author_count', 'sjr', 'u_rank','self_citations',
                  'upstream_influential_methodology_count', 'subject','subject_code','citationVelocity',
                  'influentialCitationCount','references_count','openaccessflag','normalized_citations',
                  'influentialReferencesCount','reference_background','reference_result','reference_methodology',
                  'citations_background','citations_result','citations_methodology','citations_next','coCite2',
                  'coCite3', 'reading_score', 'subjectivity', 'sentiment',
                  'num_hypo_tested','real_p', 'real_p_sign', 'p_val_range', 'num_significant', 'sample_size',
                  "extend_p", "funded", "Venue_Citation_Count", "Venue_Scholarly_Output",
                  "Venue_Percent_Cited", "Venue_CiteScore", "Venue_SNIP", "Venue_SJR", "avg_pub", "avg_hidx",
                  "avg_auth_cites", "avg_high_inf_cites","sentiment_agg", "age", "supporting_sentences", "refuting_sentences", "ratio_support", "y")

        os.chdir("/scifact/")
        shutil.rmtree('/data')  #delete the data folder in scifact 
        shellscript = subprocess.Popen(["./script/download-data.sh"], stdin=subprocess.PIPE)#delete the data folder in scifact 
        shellscript.stdin.close()
        returncode = shellscript.wait()   # blocks until shellscript is done

        os.chdir("../")
        record = namedtuple('record', fields)
        record.__new__.__defaults__ = (None,) * len(record._fields)
        # CSV output file (Delete the file manually if you wish to generate fresh output, default appends
        if path.isfile(args.csv_out + "/train.csv"):
            write_head = False
        else:
            write_head = True
        writer = csv_writer(r"{0}/{1}".format(args.csv_out, "train.csv"), append=True)
        header = list(fields)
        if write_head:
            csv_write_field_header(writer, header)
        # Run pipeline
        xmls = listdir(args.grobid_out)
        for xml in xmls:
            try:
                print("Processing ", xml)
                extractor = TEIExtractor(args.grobid_out + '/' + xml,database, xml, args.data_file)
                extraction_stage = extractor.extract_paper_info()
                issn = extraction_stage['ISSN']
                auth = extraction_stage['authors']
                citations = extraction_stage['citations']
                del extraction_stage['ISSN']
                del extraction_stage['authors']
                del extraction_stage['citations']
                p_val_stage = extract_p_values(args.pdf_input + '/' + xml.replace('.tei.xml', '.txt'))
                features = dict(**extraction_stage, **p_val_stage)
                #pdb.set_trace()
                # Get TAMU features
                paper_id = xml.split('_')[-1].replace('.xml', '')
                tamu_features = get_tamu_features(args.data_file, paper_id, issn, auth, citations,database)
                select_tamu_features = select_keys(tamu_features, tamu_select_features)
                features.update(select_tamu_features)
                print(features)
                if args.label_range:
                    label_range = args.label_range.split('-')
                    features['y'] = random.uniform(float(label_range[0]), float(label_range[1]))
                else:
                    features['y'] = float(args.label)
                try:
                    csv_write_record(writer, features, header)
                except UnicodeDecodeError:
                    print("CSV WRITE ERROR", features["ta3_pid"])
                except UnicodeEncodeError:
                    print("CSV WRITE ERROR", features["ta3_pid"])
            except Exception as e:
                print(str(e))
                print(traceback.format_exc())

    # Generate DARPA SCORE Test set
    elif args.mode == "extract-test":
        start = time.time()
        
        fields = ('ta3_pid', 'doi', 'title', 'num_citations', 'author_count', 'sjr', 'u_rank', 'self_citations',
                  'upstream_influential_methodology_count', 'subject','subject_code','citationVelocity',
                  'influentialCitationCount','references_count','openaccessflag', 'normalized_citations',
                  'influentialReferencesCount','reference_background','reference_result', 'reference_methodology',
                  'citations_background','citations_result','citations_methodology','citations_next','coCite2',
                  'coCite3','reading_score', 'subjectivity', 'sentiment',
                  'num_hypo_tested', 'real_p', 'real_p_sign', 'p_val_range', 'num_significant',
                  'sample_size',"extend_p", "funded", "Venue_Citation_Count", "Venue_Scholarly_Output",
                  "Venue_Percent_Cited", "Venue_CiteScore", "Venue_SNIP", "Venue_SJR", "avg_pub", "avg_hidx",
                  "avg_auth_cites", "avg_high_inf_cites","sentiment_agg", "age")

        record = namedtuple('record', fields)
        record.__new__.__defaults__ = (None,) * len(record._fields)
        # CSV output file
        writer = csv_writer(r"{0}/{1}".format(args.csv_out, "test.csv"))
        header = list(fields)
        csv_write_field_header(writer, header)
        args.data_file = args.file
        for document in read_darpa_tsv(args.file):
            try:
                print("Processing ", document['pdf_filename'])
                extractor = TEIExtractor(args.grobid_out + '/' + document['pdf_filename'] + '.tei.xml', document)
                extraction_stage = extractor.extract_paper_info()
                p_val_stage = extract_p_values(args.pdf_input + '/' + document['pdf_filename'] + '.txt', document['claim4'])
                features = dict(**extraction_stage, **p_val_stage)
                issn = extraction_stage['ISSN']
                auth = extraction_stage['authors']
                citations = extraction_stage['citations']
                del extraction_stage['ISSN']
                del extraction_stage['authors']
                del extraction_stage['citations']
                # Get TAMU features
                paper_id = document['pdf_filename'].split('_')[-1].replace('.pdf', '')
                #TAMU
                tamu_features = get_tamu_features(args.data_file, paper_id, issn, auth, citations,database)
                select_tamu_features = select_keys(tamu_features, tamu_select_features)
                
                #tamu_features, imputed_list = get_tamu_features(args.file, paper_id, extraction_stage[''])

                #select_tamu_features = select_keys(tamu_features, tamu_select_features)
                features.update(select_tamu_features)

                features['ta3_pid'] = document['ta3_pid']
                try:
                    csv_write_record(writer, features, header)
                except UnicodeDecodeError:
                    print("CSV WRITE ERROR", features["ta3_pid"])
                except UnicodeEncodeError:
                    print("CSV WRITE ERROR", features["ta3_pid"])
            except Exception as e:
                print(str(e))
                print(traceback.format_exc())
        end = time.time()
        print("Execution time: ", end-start)
    elif args.mode == "2400set":
        csv = pd.read_csv(args.file)
        want = [ 'kw_cs_m5', 'kw_cs_m3', 'kw_cs_m10', 'um_cs_m1', 'um_cs_m2', 'um_cs_m3', 'um_cs_m4','paper_id']
        fields = ('doi', 'title', 'num_citations', 'author_count', 'sjr', 'u_rank', 'self_citations',
                  'upstream_influential_methodology_count', 'subject','subject_code','citationVelocity',
                  'influentialCitationCount','references_count','openaccessflag', 'normalized_citations',
                  'influentialReferencesCount','reference_background','reference_result', 'reference_methodology',
                  'citations_background','citations_result','citations_methodology','citations_next','coCite2',
                  'coCite3','reading_score', 'subjectivity', 'sentiment',
                  'num_hypo_tested', 'real_p', 'real_p_sign', 'p_val_range', 'num_significant',
                  'sample_size',"extend_p", "funded", "Venue_Citation_Count", "Venue_Scholarly_Output",
                  "Venue_Percent_Cited", "Venue_CiteScore", "Venue_SNIP", "Venue_SJR", "avg_pub", "avg_hidx",
                  "avg_auth_cites", "avg_high_inf_cites","sentiment_agg", "age")
        fields = fields + tuple(want)
        record = namedtuple('record', fields)
        record.__new__.__defaults__ = (None,) * len(record._fields)
        # CSV output file (Delete the file manually if you wish to generate fresh output, default appends
        if path.isfile(args.csv_out + "/2400train.csv"):
            write_head = False
        else:
            write_head = True
        writer = csv_writer(r"{0}/{1}".format(args.csv_out, "2400train.csv"), append=True)
        header = list(fields)
        if write_head:
            csv_write_field_header(writer, header)
        # Run pipeline
        xmls = listdir(args.grobid_out)
        for xml in xmls:
            try:
                timelogger.start("overall")
                print("Processing ", xml)
                #pdb.set_trace()
                timelogger.start("metadata_apis")
                extractor = TEIExtractor(args.grobid_out + '/' + xml,database)
                extraction_stage = extractor.extract_paper_info()
                issn = extraction_stage['ISSN']
                auth = extraction_stage['authors']
                citations = extraction_stage['citations']
                del extraction_stage['ISSN']
                del extraction_stage['authors']
                del extraction_stage['citations']
                timelogger.stop("metadata_apis")
                
                timelogger.start("p-value")
                p_val_stage = extract_p_values(args.pdf_input + '/' + xml.replace('.tei.xml', '.txt'))
                features = dict(**extraction_stage, **p_val_stage)
                timelogger.stop("p-value")

                # Get TAMU features
                timelogger.start("tamu")
                paper_id = xml.split('_')[-1].replace('.xml', '')
                tamu_features = get_tamu_features(args.data_file, paper_id, issn, auth, citations,database)
                select_tamu_features = select_keys(tamu_features, tamu_select_features)
                features.update(select_tamu_features)
                timelogger.stop("tamu")
                print(features)
                if args.label_range:
                    label_range = args.label_range.split('-')
                    features['y'] = random.uniform(float(label_range[0]), float(label_range[1]))
                else:
                    #pdb.set_trace()
                    for i in want:
                        features[i] = csv[csv['pdf_filename']==xml.replace('.tei.xml', '').strip()][i].values[0]
                 
                try:
                    #print(features)
                    csv_write_record(writer, features, header)
                except UnicodeDecodeError:
                    print("CSV WRITE ERROR", features["ta3_pid"])
                except UnicodeEncodeError:
                    print("CSV WRITE ERROR", features["ta3_pid"])
            except Exception as e:
                print(str(e))
                print(traceback.format_exc())
            finally:
                timelogger.stop("overall")
