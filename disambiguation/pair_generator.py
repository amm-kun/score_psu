# Author: Arjun Menon <amm8987@psu.edu>

"""
This script generates pairs from inventors data.
"""

from collections import namedtuple
from itertools import combinations
import csv

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


class InventorCluster:
    def __init__(self, inventor_cluster):
        self.cluster = inventor_cluster
        self.pairs = []

    def generate_pairs(self):
        self.pairs = list(combinations(self.cluster, 2))

    def pairwise_feature_extraction(self):
        for pair in self.pairs:
            inventor1, inventor2 = pair


if __name__ == "__main__":
    cluster = []

    for row in read_data(inventors):
        if not cluster:
            cluster.append(row)
        else:
            if cluster[-1].cluster == row.cluster:
                cluster.append(row)
            else:
                inventor = InventorCluster(cluster)
                inventor.generate_pairs()
                cluster = [row]
                print('--------------------NEXT INVENTOR--------------------')
    inventor = InventorCluster(cluster)
    inventor.generate_pairs()

