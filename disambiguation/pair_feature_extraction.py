# Author: Arjun Menon <amm8987@psu.edu>

"""
Generates feature vector from a given pair of inventors
"""

from extractor.tokens import TokenStringSimilarity
from extractor.string import StringSimilarity
from extractor.distance import DistanceMeasure
from utilities import token_fields, string_fields


class Pair:
    def __init__(self, inventor1, inventor2):
        self.inventor1 = inventor1
        self.inventor2 = inventor2

    # Calc token similarity for the title, section, subsection, group, subgroup, organization fields
    def token_similarity(self, field):
        tokens = TokenStringSimilarity(self.inventor1.__getattribute__(field),
                                       self.inventor2.__getattribute__(field))
        return tokens.cosine(), tokens.jaccard()

    def string_similarity(self, field):
        strings = StringSimilarity(self.inventor1.__getattribute__(field),
                                   self.inventor2.__getattribute__(field))
        return strings.jaro_winkler(), strings.soundex()

    def get_distance(self):
        distance_pair = DistanceMeasure(self.inventor1.long_lat, self.inventor2.long_lat)
        return distance_pair.haversine()

    def generate_vector_pair(self, ground_truth):
        features = {}
        for field in token_fields:
            cosine, jaccard = self.token_similarity(field)
            features[field+'_cosine'] = cosine
            features[field+'_jaccard'] = jaccard
        for field in string_fields:
            jaro_winkler, soundex = self.string_similarity(field)
            features[field+'_jw'] = jaro_winkler
            features[field+'_soundex'] = soundex
        features['distance'] = self.get_distance()
        features['truth'] = ground_truth
        return features
