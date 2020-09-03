from models import Paper, Author, Organization, Address, Citation
from fuzzywuzzy import process
from utilities import elem_to_text
from bs4 import BeautifulSoup
from ack_pairs import *
from elsevier_api import getapi
import pickle

"""
Object models for the Processing Pipeline to generate features for the DARPA SCORE project
-----------------Includes the pre-processing step for the Predition Market----------------
"""

_author_ = "Arjun Menon"
_copyright_ = "Copyright 2020, Penn State University"
_license_ = ""
_version_ = "1.0"
_maintainer_ = "Arjun Menon"
_email_ = "amm8987@psu.edu"


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


class TEIExtractor:
    def __init__(self, file):
        self.file = file
        self.uni_rank = ReadPickle('uni_rank.pickle')
        self.sjr = ReadPickle('journal_dictionary.pkl')
        with open(file, 'rb') as tei:
            self.soup = BeautifulSoup(tei, features="lxml")

    def extract_paper_info(self):
        paper = Paper()
        # DOI
        doi = self.soup.teiheader.find("idno")
        if doi:
            paper.doi = elem_to_text(doi)
        # Title
        title = self.soup.teiheader.find("title")
        if title:
            paper.title = elem_to_text(title)
        # Authors
        authors = self.get_authors(self.soup.analytic.find_all('author'))
        if authors:
            paper.authors = authors
        # Year
        published = self.soup.analytic.find("publicationstmt")
        if published:
            paper.year = elem_to_text(published.find("date", type="when"))
        # Organization / Affiliations
        affiliations = self.soup.analytic.find_all('affiliation')
        for affiliation in affiliations:
            org = Organization()
            org.type = "institution"
            org.name = elem_to_text(affiliation.find("orgname", type="institution"))
            address = Address()
            addr = affiliation.find("address")
            if addr:
                address.place = elem_to_text(addr.find("settlement"))
                address.region = elem_to_text(addr.find("region"))
                address.country = elem_to_text(addr.find("country"))
            org.address = address
            paper.affiliations.append(org)
        # University Ranking
        if paper.affiliations:
            if paper.affiliations[0] != '':
                paper.uni_rank = self.uni_rank.get_rank(paper.affiliations[0].name)
            elif len(paper.affiliations) > 1:
                paper.uni_rank = self.uni_rank.get_rank(paper.affiliations[1].name)
        else:
            paper.uni_rank = self.uni_rank.get_rank('Random')
        # Citations
        bibliography = self.soup.listbibl.find_all('biblstruct')
        for bibl in bibliography:
            citation = Citation()
            cited_paper = bibl.analytic
            if cited_paper:
                citation.title = elem_to_text(cited_paper.find("title", type="main"))
                citation_authors = self.get_authors(cited_paper.find_all("author"))
                citation.doi = elem_to_text(cited_paper.find("idno", type="DOI"))
                if citation_authors:
                    citation.authors = citation_authors
            cited_journal = bibl.monogr
            if cited_journal:
                citation.source = elem_to_text(cited_journal.find("title"))
                try:
                    citation.publish_year = cited_journal.imprint.date['when']
                except TypeError:
                    pass
            paper.citations.append(citation)
        # NER - Ack pairs - Funding status
        paper.ack_pairs = self.get_funding_status()
        er_list = [org for (entity, org) in paper.ack_pairs]
        if 'ORG' in er_list:
            paper.funded = 1
        else:
            paper.funded = 0
        # SJR
        api_resp = self.get_sjr(paper)
        if api_resp:
            paper.cited_by_count = api_resp["cited_by"]
            paper.sjr = api_resp["sjr"]
            paper.subject = api_resp["subject"]
        # Set self-citations
        paper.self_citations = paper.set_self_citations()
        # return paper
        return {"doi": paper.doi, "title": paper.title, "num_citations": paper.cited_by_count, "author_count": len(paper.authors),
                "sjr": paper.sjr, "u_rank": paper.uni_rank, "funded": paper.funded,
                "self_citations": paper.self_citations, "subject": paper.subject}

    @staticmethod
    def get_authors(authors):
        authors_list = []
        for author in authors:
            person = Author()
            pers_name = author.persname
            if not pers_name:
                continue
            person.first_name = elem_to_text(pers_name.find("forename", type="first"))
            person.middle_name = elem_to_text(pers_name.find("forename", type="middle"))
            person.surname = elem_to_text(pers_name.surname)
            person.set_name()
            if not any(auth.name == person.name for auth in authors_list):
                authors_list.append(person)
        return authors_list

    def get_funding_status(self):
        pairs = NER(XML2ack(self.file))
        return pairs

    @staticmethod
    def get_sjr(paper):
        if not paper.doi:
            return None
        else:
            api = getapi(paper.doi,paper.title)
            if api.empty:
                return None
            else:
                try:
                    cited_by = api['citedby-count'][0]
                except KeyError:
                    cited_by = 0
                try: 
                    subject = api['subject']
                except:
                    subject = None
                try:
                    sjr_score = api['SJR'][0]
                except KeyError:
                    sjr_score = 0
        return {"sjr": sjr_score, "cited_by": cited_by, "subject": subject}


if __name__ == "__main__":

    uni_rank = ReadPickle('uni_rank.pickle')
    sjr = ReadPickle('journal_dictionary.pkl')

    test = r"C:\Users\arjun\Downloads\teregowda-hotcloud-10.tei.xml"
    extractor = TEIExtractor(test)
    test_paper = extractor.extract_paper_info()
    print(test_paper)
