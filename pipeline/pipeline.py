from utilities import  p_val_sign, elem_to_text
from bs4 import BeautifulSoup
from ingestion.utilities import parse_dir_xml
from elsevier_api import get_elsevier
from grobid_client.grobid_client import run_grobid
import math
import random
from collections import namedtuple
from disambiguation.utilities import csv_writer, csv_write_field_header, csv_write_record
import argparse
from ack_pairs import *
import pickle
from fuzzywuzzy import  process


class ReadPickle:
    def __init__(self, filename):
        with open(filename, 'rb') as handle:
            self.d = pickle.load(handle)

    def get_rank(self, university):
        t = process.extractOne(university, self.d.keys())
        if t[1] > 95:
            return 1 - (self.d[t[0]]/101)
        else:
            return 2

    def get_sjr(self, journal):
        t = process.extractOne(journal, self.d['dc:title'].to_list())
        if t[1] > 95:
            return self.d.loc[self.d['dc:title'] == t[0]]['SJR'][0]


def get_p_val_darpa_tsv(claim):
    pattern_p = re.search("p\\s?[<>=]\\s?\\d?\\.\\d+e?[-–]?\\d*", claim)
    if pattern_p:
        return pattern_p.group()
    else:
        return None


def extract_p_values(file, doi):
    p_val_list = []
    sample_list = []
    filtered_sent = []
    sentences = []
    max_sample_size = 0
    range_p_values = 0
    real_p_sign = 0
    num_hypo_test = 0
    real_p_value = 1
    number_significant = 0
    extended_p_val = 0

    try:
        text = open(file, "r", encoding="utf8")
        text1 = text.read()
    except UnicodeDecodeError:
        return {"num_hypo_tested": num_hypo_test, "real_p": real_p_value, "real_p_sign": real_p_sign,
                "p_val_range": range_p_values, "num_significant": number_significant, "sample_size": max_sample_size,
                "extend_p": extended_p_val}
    except FileNotFoundError:
        return {"num_hypo_tested": num_hypo_test, "real_p": real_p_value, "real_p_sign": real_p_sign,
                "p_val_range": range_p_values, "num_significant": number_significant, "sample_size": max_sample_size,
                "extend_p": extended_p_val}

    #  "nlp" Object is used to create documents with linguistic annotations.
    doc = nlp(text1)
    filtered_sent = []
    # create list of sentence tokens
    for word in doc:
        if word.is_stop == False:
            filtered_sent.append(word)

    sentences = []
    for sent in doc.sents:
        sentences.append(sent.text)

    for i in range(0, len(sentences) - 1):

        # ********REGEX FOR PA FORMATTED DISTRIBUTIONS******************

        # expression for t distribution vs p value
        pattern_t_list = re.finditer(
            "t\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
            sentences[i])

        # expression for f distribution vs p value
        pattern_f_list = re.finditer(
            "F\\s?\\(\\s?\\d*\\.?(I|l|\\d+)\\s?,\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|([Pp]\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
            sentences[i])

        # expression for correlation r vs p value
        pattern_cor_list = re.finditer(
            "r\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
            sentences[i])

        # expression for z distribution
        pattern_z_list = re.finditer(
            "[^a-z]z\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
            sentences[i])

        # expression for chi square distribution vs p value
        pattern_chi_list = re.finditer(
            "((\\[CHI\\]|\\[DELTA\\]G)\\s?|(\\s[^trFzQWBn ]\\s?)|([^trFzQWBn ]2\\s?))2?\\(\\s?\\d*\\.?\\d+\\s?(,\\s?N\\s?\\=\\s?\\d*\\,?\\d*\\,?\\d+\\s?)?\\)\\s?[<>=]\\s?\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=]\\s?\\d?\\.\\d+e?-?\\d*))",
            sentences[i])

        # expression for q distribution vs p value
        pattern_q_list = re.finditer(
            "Q\\s?-?\\s?(w|within|b|between)?\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=]\\s?\\d?\\.\\d+e?-?\\d*))",
            sentences[i])

        # expression for beta distribution vs p value

        # expression for b value - p value distribution
        pattern_b_list = re.finditer(
            "b\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
            sentences[i])

        # *****************REGEX FOR P VALUE EXPRESSION FROM DISTRIBUTION**************
        # expression for p value expression
        pattern_p = re.search("p\\s?[<>=]\\s?\\d?\\.\\d+e?-?\\d*", sentences[i])

        # --------------------------------------T-DISTRIBUTION---------------------------------------------

        for pattern_t in pattern_t_list:
            if pattern_t:
                expression = pattern_t.group()
                reported_pval_exp = pattern_p.group()
                p_val_list.append(reported_pval_exp)
                sentence = pattern_t.string
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = 'NULL'
                    df1 = s[0]
                    sample_t = df1 + 1
                    sample_list.append(sample_t)

                else:
                    df2 = s[1]
                    df1 = s[0]
                    sample_t = df1 + 1
                    sample_list.append(sample_t)

        # --------------------------------------------------F-DISTRIBUTION--------------------------------

        for pattern_f in pattern_f_list:
            if pattern_f:
                expression = pattern_f.group()
                if pattern_p:
                    reported_pval_exp = pattern_p.group()
                    p_val_list.append(reported_pval_exp)
                # p_val_list.append(reported_pval_exp)
                sentence = pattern_f.string
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = s[1]
                    df1 = s[0]
                    constant = df1 + 1
                    sample_f = constant + df2
                    sample_list.append(sample_f)

                else:
                    df2 = s[1]
                    df1 = s[0]
                    constant = df1 + 1
                    sample_f = constant + df2
                    sample_list.append(sample_f)

        # ------------------------------------------- CORRELATION ----------------------------------------------------

        for pattern_cor in pattern_cor_list:
            if pattern_cor:
                expression = pattern_cor.group()
                reported_pval_exp = pattern_p.group()
                p_val_list.append(reported_pval_exp)
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = 'NULL'
                    df1 = s[0]
                    sample_cor = df1 + 2
                    sample_list.append(sample_cor)


                else:
                    df2 = s[1]
                    df1 = s[0]
                    sample_cor = df1 + 2
                    sample_list.append(sample_cor)

        # ----------------------------------- b value in distribution ------------------------------------------------

        for pattern_b in pattern_b_list:
            if pattern_b:
                expression = pattern_b.group()
                reported_pval_exp = pattern_p.group()
                p_val_list.append(reported_pval_exp)
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = 'NULL'
                    df1 = s[0]
                else:
                    df2 = s[1]
                    df1 = s[0]

        # ---------------------------------------------- Z-DISTRIBUTION ----------------------------------------------

        for pattern_z in pattern_z_list:
            if pattern_z:
                expression = pattern_z.group()
                reported_pval_exp = pattern_p.group()
                p_val_list.append(reported_pval_exp)
                sentence = pattern_z.string
                distribution = "z"
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 2:
                    df2 = 'NULL'
                    df1 = 'NULL'

        # ------------------------------------ CHI SQUARE DISTRIBUTION---------------------------------------------

        for pattern_chi in pattern_chi_list:
            if pattern_chi:
                expression = pattern_chi.group()
                reported_pval_exp = pattern_p.group()
                p_val_list.append(reported_pval_exp)
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 4:
                    sample_chi = 'NULL'
                    df1 = s[1]
                else:
                    sample_chi = s[2]
                    df1 = s[1]
                    # chi_value = s[3]
                    sample_list.append(sample_chi)

        # --------------------------------------------------- Q-DISTRIBUTION ---------------------------------------------

        for pattern_q in pattern_q_list:
            if pattern_q:
                expression = pattern_q.group()
                reported_pval_exp = pattern_p.group()
                p_val_list.append(reported_pval_exp)
                claim = sentences[i]
                sentence = pattern_q.string
                distribution = "q"
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = 'NULL'
                    df1 = s[0]
                else:
                    df2 = s[1]
                    df1 = s[0]

    just_pvalues_list = []
    if len(p_val_list) == 0:
        extended_p_val = 1
        for i in range(0, len(sentences) - 1):

            # *****************REGEX FOR P VALUE EXP from sentences **************
            # expression for p value expression
            pattern_p_list = re.finditer("p\\s?[<>=]\\s?\\d?\\.\\d+e?[-–]?\\d*", sentences[i])

            # --------------------------------------T-DISTRIBUTION---------------------------------------------

            for pattern_p in pattern_p_list:
                if pattern_p:
                    # expression = pattern_t.group()
                    reported_pval = pattern_p.group()
                    just_pvalues_list.append(reported_pval)
        print("statistical p-values not found, all p-values of pdf", just_pvalues_list)
        p_val_list = just_pvalues_list

    if len(p_val_list) == 0:
        p_val_list.append(get_p_val_darpa_tsv(doi))

    try:
        # p_val_num_list = [float(string.split()[2]) for string in p_val_list]
        p_val_num_list = []
        for string in p_val_list:
            try:
                p_val_num_list.append(float(string.split()[2]))
            except ValueError:
                string = string.replace('–', '-')
                p_val_num_list.append(float(string.split()[2]))
    except IndexError:
        print("Index error in P-Val script")
        p_val_num_list = []
    print("vector of p-value numbers:", p_val_num_list)
    if len(p_val_list) > 0 and len(p_val_num_list) > 0:
        num_hypo_test = len(p_val_list)
        real_p_value = min(p_val_num_list)
        print("Number of hypothesis tested:", num_hypo_test)
        print("Real p-value:", real_p_value)

        number_significant = 0
        for string in p_val_list:
            if string.split()[1] == '<' or string.split()[1] == '=':
                try:
                    if float(string.split()[2]) <= 0.05:
                        number_significant += 1
                except ValueError:
                    string = string.replace('–', '-')
                    if float(string.split()[2]) <= 0.05:
                        number_significant += 1
        print("Number Significant:", number_significant)

        print("vector of p-values", p_val_list)
        if sample_list:
            print("vector of sample sizes", max(sample_list))
            max_sample_size = max(sample_list)
            range_p_values = max(p_val_num_list) - min(p_val_num_list)
            real_p_sign = p_val_list[p_val_num_list.index(min(p_val_num_list))].split()[1]
            try:
                real_p_sign = p_val_sign[real_p_sign]
            except KeyError:
                real_p_sign = 0
        print("Max Sample size: ", max_sample_size)
        print("Range of p-values: ", range_p_values)
        print("Real p-value sign: ", real_p_sign)
    else:
        no_p_values.append(file)
    return {"num_hypo_tested": num_hypo_test, "real_p": real_p_value, "real_p_sign": real_p_sign,
            "p_val_range": range_p_values, "num_significant": number_significant, "sample_size": max_sample_size,
            "extend_p": extended_p_val}


def parse_xml(directory, xml_file):
    doi = None
    cited_by = 0
    sjr = 0
    uni_rank = 2
    author_set = set()
    org_set = set()
    xml_path = directory
    xml_path += '/'
    with open(xml_path + xml_file, 'r', encoding="utf8") as tei_file:
        soup = BeautifulSoup(tei_file, features="lxml")
        print("-------------------")
        title = soup.title.getText()
        print(soup.title.getText())
        if soup.idno:
            doi = soup.idno.getText()
            print(doi)
        # Authors
        authors = soup.analytic.find_all('author')
        num_authors = len(authors)
        for author in authors:
            persname = author.persname
            if not persname:
                num_authors -= 1
                continue
            firstname = elem_to_text(persname.find("forename", type="first"))
            middlename = elem_to_text(persname.find("forename", type="middle"))
            surname = elem_to_text(persname.surname)
            PoN = [firstname, middlename, surname]
            name = ' '.join(PoN)
            author_set.add(name)
        print("Number of authors: ", len(author_set))

        # Year Published
        published = soup.analytic.find("publicationstmt")
        if published:
            year_published = elem_to_text(published.find("date", type="when"))
            print("Year Published is: ", year_published)

        affiliations = soup.analytic.find_all('affiliation')
        for affiliation in affiliations:
            org_set.add(elem_to_text(affiliation.find("orgname", type="institution")))
        print("Affliations", org_set)

        if org_set:
            orgs = list(org_set)
            if orgs[0] != '':
                uni_rank = c.get_rank(orgs[0])
            elif len(orgs) > 1:
                uni_rank = c.get_rank(orgs[1])
        else:
            uni_rank = c.get_rank('random')
        print("Uni_Rank is: ", uni_rank)

        if doi:
            api = get_elsevier(doi)
            try:
                if api.empty:
                    api_doi_errors.append(doi)
                    return {"author_count": len(author_set), "doi": doi, "u_rank": uni_rank, "num_citations": 0, "sjr": 0}
            except AttributeError:
                api_doi_errors.append(doi)
                return {"author_count": len(author_set), "doi": doi, "u_rank": uni_rank, "num_citations": 0, "sjr": 0}
            try:
                cited_by = api['citedby-count'][0]
                print("Number of citations:", cited_by)
            except KeyError:
                print("Missing citedby-count")
                cited_by = 0
            try:
                sjr = api['SJR'][0]
                print("SJR: ", sjr)
            except KeyError:
                print("Missing SJR")
                sjr = 0
            try:
                if uni_rank == 2:
                    print(api.affilname_0[0])
                    if math.isnan(api.affilname_0[0]):
                        pass
                    else:
                        uni_rank = c.get_rank(api.affilname_0[0])
            except AttributeError:
                pass
            except TypeError:
                pass

    return {"title": title, "num_citations": cited_by, "author_count": len(author_set), "sjr": sjr, "doi": doi,
            "u_rank": uni_rank}


def process_directory(xml_dir, txt_dir, label=None):
    xmls = parse_dir_xml(xml_dir)
    for tei in xmls:
        print("Processing File: ", tei)
        stage_1 = parse_xml(xml_dir, tei)
        txt_file = tei.strip("tei.xml") + ".txt"
        filename = txt_dir + '/' + txt_file
        stage_2 = extract_p_values(filename, stage_1["doi"])
        features = dict(**stage_1, **stage_2)
        xml_path = xml_dir + "/" + tei
        stage_3 = NER(XML2ack(xml_path))
        er_list = [org for (entity, org) in stage_3]
        if 'ORG' in er_list:
            features["funded"] = 1
        else:
            features["funded"] = 0
        if not label:
            pass
        elif label == -1:
            features["y"] = random.uniform(0.7, 1) # For PrePub
        elif label == -2:
            features["y"] = random.uniform(0, 0.3)
        else:
            features["y"] = label
        try:
            csv_write_record(writer, features, header)
        except UnicodeDecodeError:
            print("CSV WRITE ERROR", features["doi"])
        except UnicodeEncodeError:
            print("CSV WRITE ERROR", features["doi"])
    print("API errors", api_doi_errors)
    print("No P-Vals", no_p_values)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Pipeline - Process PDFS - Market Pre-processing")
    parser.add_argument("-in", "--pdf_input", help="parent folder that contains all pdfs")
    parser.add_argument("-out", "--grobid_out", help="grobid output path")
    parser.add_argument("-m", "--mode", default="processFulltextDocument", help="grobid mode")
    parser.add_argument("-n", default=10, help="concurrency for service usage")
    no_p_values
    args = parser.parse_args()

    run_grobid(args.pdf_input, args.grobid_out, args.n, args.mode)

    fields = ('doi', 'title', 'num_citations', 'author_count', 'sjr', 'u_rank', 'num_hypo_tested', 'real_p',
              'real_p_sign', 'p_val_range', 'num_significant', 'sample_size',  "extend_p", "funded")
    record = namedtuple('record', fields)
    record.__new__.__defaults__ = (None,) * len(record._fields)

    # CSV output file
    writer = csv_writer(r"C:\Users\arjun\dev\out.csv")
    header = list(fields)
    csv_write_field_header(writer, header)


    # nlp = spacy.load("en_core_web_sm")
    # # Load English tokenizer, tagger, parser, NER and word vectors
    # nlp = English()
    # # Create the pipeline 'sentencizer' component
    # sbd = nlp.create_pipe('sentencizer')
    # # Add the component to the pipeline
    # nlp.add_pipe(sbd)

    api_doi_errors = []
    no_p_values = []

    # xml_dir1 = [r"C:\Users\arjun\dev\GROBID_processed\PublishPre", r"C:\Users\arjun\dev\GROBID_processed\RetractedErrorData",
    #            r"C:\Users\arjun\dev\GROBID_processed\ReplicationProject\TRUE", r"C:\Users\arjun\dev\GROBID_processed\ReplicationProject\FALSE"]
    # txt_dir1 = [r"C:\Users\arjun\dev\text_files\publishPre", r"C:\Users\arjun\dev\text_files\retractedErrorData",
    #            r"C:\Users\arjun\dev\text_files\replicationProject\TRUE", r"C:\Users\arjun\dev\text_files\replicationProject\FALSE"]

    c = ReadPickle('uni_rank.pickle')
    sjr = ReadPickle('journal_dictionary.pkl')

    print(c.get_rank('Harvard'))

    print(sjr.get_sjr('American Economic Review'))

    # for i in range(len(xml_dir1)):
    #     if i == 0:
    #         process_directory(xml_dir1[i], txt_dir1[i], -1)
    #     elif i == 1:
    #         process_directory(xml_dir1[i], txt_dir1[i], 0)
    #     elif i == 2:
    #         process_directory(xml_dir1[i], txt_dir1[i], 1)
    #     elif i == 3:
    #         process_directory(xml_dir1[i], txt_dir1[i], -2)

    xml_dir1 = r"C:\Users\arjun\dev\GROBID_processed\test"
    txt_dir1 = r"C:\Users\arjun\dev\text_files\test"

    process_directory(xml_dir1, txt_dir1)





    # xmls = parse_dir_xml(xml_dir)
    # for tei in xmls:
    #     print("Processing File: ", tei)
    #     stage_1 = parse_xml(xml_dir, tei)
    #     txt_file = tei.strip("tei.xml")+".txt"
    #     filename = txt_dir+'/'+txt_file
    #     stage_2 = extract_p_values(filename)
    #     features = dict(**stage_1, **stage_2)
    #     xml_path = xml_dir + "/" + tei
    #     stage_3 = NER(XML2ack(xml_path))
    #     er_list = [org for (entity, org) in stage_3]
    #     if 'ORG' in er_list:
    #         features["funded"] = 1
    #     else:
    #         features["funded"] = 0
    #     # features["y"] = random.uniform(0.7, 1) # For PrePub
    #     features["y"] = 0
    #     try:
    #         csv_write_record(writer, features, header)
    #     except UnicodeDecodeError:
    #         print("CSV WRITE ERROR", features["doi"])
    #     except UnicodeEncodeError:
    #         print("CSV WRITE ERROR", features["doi"])
    # print("API errors", api_doi_errors)
    # print("No P-Vals", no_p_values)
    # ------END

    # python pipeline/pipeline.py --path C:\Users\arjun\repos\grobid_client\ --input C:\Users\arjun\dev\pdfs --grobid_out C:\Users\arjun\dev\xmls
    # os.chdir(args.path)
    # os.chdir(r"C:\Users\arjun\repos\grobid_client")
    # command = "grobid_client.py --input {0} --output {1} {2}".format(args.input, args.grobid_out, args.mode)
    # command = r"grobid_client.py --input C:\Users\arjun\dev\pdfs --output  C:\Users\arjun\dev\xmls processFulltextDocument"
    # os.system(command)

    # # # # Generate text files from PDF
    # pdfs = parse_dir_pdf(r"C:\Users\arjun\dev\test\pdfs")
    # count = 0
    # for pdf in pdfs:
    #     print(count)
    #     command = r"C:\Users\arjun\dev\xpdf-tools-win-4.02\bin64\pdftotext C:\Users\arjun\dev\test\pdfs/" + pdf
    #     os.system(command)
    #     count += 1

    # print("Coverting PDF to TXT")
    # # os.system(r"C:\Users\arjun\dev\xpdf-tools-win-4.02\bin64\pdftotext C:\Users\arjun\dev\pdfs\*")
    # xml = parse_dir_xml(args.grobid_out)
    # xml = parse_dir_xml(r"C:\Users\arjun\dev\xmls")
    # for file in xml:
    #     parse_xml(file)
    # print(perNER(XML2ack(r'C:\Users\arjun\dev\xmls\4.tei.xml')))
    # print(NER(XML2ack(r'C:\Users\arjun\dev\xmls\4.tei.xml')))