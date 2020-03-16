# Author: Arjun Menon <amm8987@psu.edu>

"""
This script generates pairs from inventors data.
"""

from pair_feature_extraction import Pair
from collections import namedtuple
from itertools import combinations
import math
import csv
import pandas as pd
import random

fields = ('patent_id', 'cluster', 'title', 'inventor_id', 'name_first', 'name_last', 'section', 'subsection',
          'group', 'sub_group',  'city', 'state', 'long_lat', 'organization')
inventorRecord = namedtuple('inventor', fields)

inventors = r'C:\Users\Arjun Menon\Desktop\SCORE\test.csv'


def read_data(path):
    with open(path, 'rU') as data:
        reader = csv.reader(data)
        next(reader)  # Skip first fields line
        for record in map(inventorRecord._make, reader):
            yield record


def gen_features_positive():
    cluster = []
    for inv_id, row in enumerate(read_data(inventors)):
        if not cluster:
            cluster.append(row)
        else:
            if cluster[-1].cluster == row.cluster:
                cluster.append(row)
            else:
                inventor = InventorCluster(cluster)
                inventor.generate_pairs()
                inventor.pairwise_feature_extraction(1)
                cluster = [row]
                print('--------------------NEXT INVENTOR @ ', inv_id, '--------------------')
    inventor = InventorCluster(cluster)
    inventor.generate_pairs()
    inventor.pairwise_feature_extraction(1)


def gen_features_random_negative(num_pairs):
    data_frame = pd.read_csv(inventors)
    sample = data_frame.sample(round(math.sqrt(num_pairs*2)), replace=False)
    print(sample)

#
#     while count < num_pairs:
#         line_number1 = random.randrange(lines)
#         line_number2 = random.randrange(lines)
#         with open(inventors) as f:
#             reader = csv.reader(f)
#             chosen_row = next(row for row_number, row in enumerate(reader)
#                               if row_number == line_number)


class InventorCluster:
    def __init__(self, inventor_cluster):
        self.cluster = inventor_cluster
        self.pairs = []

    def generate_pairs(self):
        self.pairs = list(combinations(self.cluster, 2))

    def pairwise_feature_extraction(self, label):
        for pair in self.pairs:
            inventor1, inventor2 = pair
            pair = Pair(inventor1, inventor2)
            feature_vector = pair.generate_vector_pair(label)
            print(feature_vector)


if __name__ == "__main__":
    # gen_features_positive()
    gen_features_random_negative(3)
