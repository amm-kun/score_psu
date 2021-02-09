from models import Paper, Author, Organization, Address, Citation
from fuzzywuzzy import process
from utilities import elem_to_text
from bs4 import BeautifulSoup
from ack_pairs import *
from elsevier_api import getcrossref
from elsevier_api import getelsevier
from elsevier_api import getsemantic
import pickle
import pdb
from scripts.coCitation import coCite
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
    def __init__(self, file, test_tsv=None):
        self.file = file
        self.uni_rank = ReadPickle('uni_rank.pickle')
        self.sjr = ReadPickle('journal_dictionary.pkl')
        self.document = test_tsv
        self.paper = Paper()
        with open(file, 'rb') as tei:
            self.soup = BeautifulSoup(tei, features="lxml")

    # TODO: return paper | redesign extractor to make it more modular to test individual components

    def get_self_citations(self):
        # DOI
        doi = self.soup.teiheader.find("idno", type="DOI")
        if doi:
            self.paper.doi = elem_to_text(doi)
        elif self.document:
            self.paper.doi = self.document['doi']
        # Title
        title = self.soup.teiheader.find("title")
        if title:
            self.paper.title = elem_to_text(title)
        # Authors
        authors = self.get_authors(self.soup.analytic.find_all('author'))
        if authors:
            self.paper.authors = authors
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
            self.paper.citations.append(citation)
        self.paper.set_self_citations()
        return {'doi': self.paper.doi, 'title': self.paper.title, 'total_citations': len(self.paper.citations),
                'self_citations': self.paper.self_citations}

    def extract_paper_info(self):
        # DOI
        doi = self.soup.teiheader.find("idno", type="DOI")
        if doi:
            self.paper.doi = elem_to_text(doi)
        elif self.document:
            self.paper.doi = self.document['doi']
        # Title
        title = self.soup.teiheader.find("title")
        if title:
            self.paper.title = elem_to_text(title)
        # Authors
        authors = self.get_authors(self.soup.analytic.find_all('author'))
        if authors:
            self.paper.authors = authors
        # Year
        published = self.soup.analytic.find("publicationstmt")
        if published:
            self.paper.year = elem_to_text(published.find("date", type="when"))
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
            self.paper.affiliations.append(org)
        # University Ranking
        if self.paper.affiliations:
            if self.paper.affiliations[0] != '':
                self.paper.uni_rank = self.uni_rank.get_rank(self.paper.affiliations[0].name)
            elif len(self.paper.affiliations) > 1:
                self.paper.uni_rank = self.uni_rank.get_rank(self.paper.affiliations[1].name)
        else:
            self.paper.uni_rank = self.uni_rank.get_rank('Random')
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
            self.paper.citations.append(citation)
        # NER - Ack pairs - Funding status
        self.paper.ack_pairs = self.get_funding_status()
        er_list = [org for (entity, org) in self.paper.ack_pairs]
        if 'ORG' in er_list:
            self.paper.funded = 1
        else:
            self.paper.funded = 0
        # SJR
        api_resp = self.get_sjr(self.paper.doi, self.paper.title)
        if api_resp:
            self.paper.cited_by_count = api_resp["num_citations"]
            self.paper.sjr = api_resp["sjr"]
            self.paper.subject = api_resp["subject"]
            self.paper.subject_code = api_resp["subject_code"]
            self.paper.normalized = api_resp["normalized_citations"]
            self.paper.velocity = api_resp["citationVelocity"]
            self.paper.influentialcitations = api_resp["influentialCitationCount"]
            self.paper.references = api_resp["references_count"]
            self.paper.flag = api_resp["openaccessflag"]
            self.paper.influentialref = api_resp["influentialReferencesCount"]
            self.paper.ref_background = api_resp["reference_background"]
            self.paper.ref_result = api_resp["reference_result"]
            self.paper.ref_method = api_resp["reference_methodology"]
            self.paper.cite_background = api_resp["citations_background"]
            self.paper.cite_result = api_resp["citations_result"]
            self.paper.cite_method = api_resp["citations_methodology"]
            self.paper.cite_next = api_resp["citations_next"]
            self.paper.influential_references_methodology = api_resp["upstream_influential_methodology_count"]
            self.paper.issn = api_resp["ISSN"]
            self.paper.auth = api_resp["authors"]
        # Set self-citations
        self.paper.self_citations = self.paper.set_self_citations()
        # return paper

        t2,t3 = coCite(self.paper.doi)
        return {"doi": self.paper.doi, "title": self.paper.title, "num_citations": self.paper.cited_by_count,
                "author_count": len(self.paper.authors),"sjr": self.paper.sjr, "u_rank": self.paper.uni_rank,
                "funded": self.paper.funded,"self_citations": self.paper.self_citations, "subject": self.paper.subject,
                "subject_code": self.paper.subject_code, "citationVelocity": self.paper.velocity,
                "influentialCitationCount": self.paper.influentialcitations, "references_count": self.paper.references,
                "openaccessflag": self.paper.flag, "influentialReferencesCount": self.paper.influentialref,
                "normalized_citations": self.paper.normalized, "reference_background": self.paper.ref_background,
                "reference_result": self.paper.ref_result, "reference_methodology": self.paper.ref_method,
                "citations_background": self.paper.cite_background, "citations_result": self.paper.cite_result,
                "citations_methodology": self.paper.cite_method, "citations_next": self.paper.cite_next,
                "upstream_influential_methodology_count": self.paper.influential_references_methodology,
                "coCite2":t2, "coCite3":t3, "ISSN":self.paper.issn, "authors":self.paper.auth}


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
    def get_sjr(doi,title):

        
        response = getsemantic(doi,title)
        crossref = response.get_row()
        scopus_search = response.return_search()
        serial_title = response.return_serialtitle()
        semantic = response.return_semantic()
        final = {"doi":response.doi, "title":response.title, "sjr": response.sjr, "num_citations": response.citedby,"subject":response.subject,"subject_code":response.subject_code,"normalized_citations":response.normalized,"citationVelocity":response.velocity,"influentialCitationCount":response.incite,"references_count":response.refcount,"openaccessflag":response.openaccess,"influentialReferencesCount":response.inref, "reference_background": response.refback, "reference_result":response.refresult, "reference_methodology":response.refmeth,"citations_background":response.cback,"citations_result":response.cresult,"citations_methodology":response.cmeth, "citations_next":response.next, "upstream_influential_methodology_count": response.upstream_influential_methodology_count, "ISSN": response.issn, "authors":response.auth}
        return final

if __name__ == "__main__":

    uni_rank = ReadPickle('uni_rank.pickle')
    sjr = ReadPickle('journal_dictionary.pkl')

    test = r"C:\Users\arjun\dev\GROBID_processed\test\Gelfand_covid_n8dr9.tei.xml"
    extractor = TEIExtractor(test)
    test_paper = extractor.extract_paper_info()
    print(test_paper)
