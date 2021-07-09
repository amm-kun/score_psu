from collections import namedtuple
import pandas as pd
import csv
import re
import string

p_val_sign = {
    '<': -1,
    '=': 0,
    '>': 1
}

#{'Citation Count': 'Venue_Citation_Count', 'Scholarly Output': 'Venue_Scholarly_Output',
#                           'Percent Cited': 'Venue_Percent_Cited', 'CiteScore': 'Venue_CiteScore', 'SNIP': 'Venue_SNIP',
 #                          'SJR': 'Venue_SJR'}
tamu_select_features = ["Venue_Citation_Count", "Venue_Scholarly_Output", "Venue_Percent_Cited", "Venue_CiteScore",
                        "Venue_SNIP", "Venue_SJR", "avg_pub", "avg_hidx", "avg_auth_cites",
                        "avg_high_inf_cites","sentiment_agg"]

def remove_accents(text: str):
    text = re.sub('[âàäáãå]', 'a', text)
    text = re.sub('[êèëé]', 'e', text)
    text = re.sub('[îìïí]', 'i', text)
    text = re.sub('[ôòöóõø]', 'o', text)
    text = re.sub('[ûùüú]', 'u', text)
    text = re.sub('[ç]', 'c', text)
    text = re.sub('[ñ]', 'n', text)
    text = re.sub('[ÂÀÄÁÃ]', 'A', text)
    text = re.sub('[ÊÈËÉ]', 'E', text)
    text = re.sub('[ÎÌÏÍ]', 'I', text)
    text = re.sub('[ÔÒÖÓÕØ]', 'O', text)
    text = re.sub('[ÛÙÜÚ]', 'U', text)
    text = re.sub('[Ç]', 'C', text)
    text = re.sub('[Ñ]', 'N', text)
    return text


def strip_punctuation(text: str):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    text = re.sub(regex, "", text)
    text = text.strip()
    return text


def read_darpa_tsv(file):
    df = pd.read_csv(file, sep="\t")
    for index, row in df.iterrows():
        try:
            yield {"title": row['title_CR'], "pub_year": row['pub_year_CR'], "doi": row['DOI_CR'],
               "ta3_pid": row['ta3_pid'], "pdf_filename": row['pdf_filename'], "claim4": row['claim4_inftest']}
        except KeyError:
            ta3_pid = row['pdf_filename'].split()[-1]
            yield {"title": row['title_CR'], "pub_year": row['pub_year_CR'], "doi": row['DOI_CR'],
                   "ta3_pid": ta3_pid, "pdf_filename": row['pdf_filename'], "claim4": row['claim4_inftest']}


def elem_to_text(elem, default=''):
    if elem:
        return elem.getText()
    else:
        return default


# Return CSV writer object
def csv_writer(filename, append=False):
    if append:
        writer = csv.writer(open(filename, 'a', newline='', encoding='utf-8'))
    else:
        writer = csv.writer(open(filename, 'w', newline='', encoding='utf-8'))
    return writer


# Write header into CSV
def csv_write_field_header(writer, header):
    writer.writerow(header)


# Write dict based record into CSV in order
def csv_write_record(writer, record, header):
    nt_record = namedtuple('dis_features', header)
    sim_record = nt_record(**record)
    writer.writerow(list(sim_record))


# Read selected values from dictionary
def select_keys(input_data , projection=None):
    output_projection = {}
    for key in projection:
        try:
            output_projection[key] = input_data[key].values[0]
        except:
            output_projection[key] = 0
    return output_projection

