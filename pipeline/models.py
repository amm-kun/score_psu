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


class Paper:
    def __init__(self):
        self.doi = None
        self.ta3_pid = None
        self.title = None
        self.sjr = 0
        self.uni_rank = 0
        self.year = 0
        self.funded = 0
        self.cited_by_count = 0
        self.citations = []
        self.authors = []
        self.affiliations = []
        self.ack_pairs = []


class Author:
    def __init__(self):
        self.first_name = None
        self.middle_name = None
        self.surname = None
        self.name = None

    def set_name(self):
        self.name = ' '.join([self.first_name, self.middle_name, self.surname])


class Organization:
    def __init__(self):
        self.type = None
        self.name = None
        self.address = Address()


class Address:
    def __init__(self):
        self.place = None
        self.region = None
        self.country = None


class Citation:
    def __init__(self):
        self.title = None
        self.authors = []
        self.source = None
        self.doi = None
        self.publish_year = None
