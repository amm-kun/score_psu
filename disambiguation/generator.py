# Author: Arjun Menon <amm8987@psu.edu>

"""
This script generates pairs from inventors data.
"""

from pair_feature_extraction import Pair
from collections import namedtuple
from itertools import combinations, product
from utilities import check_file
import argparse
import csv

fields = ('patent_id', 'cluster', 'title', 'inventor_id', 'name_first', 'name_last', 'section', 'subsection',
          'group', 'sub_group',  'city', 'state', 'long_lat', 'organization')
inventorRecord = namedtuple('inventor', fields)

parser = argparse.ArgumentParser(description='Specify target inventor csv')
parser.add_argument('-f', '--file', help='specify the inventor features csv file', type=check_file)
file = parser.parse_args()

# inventors = r'C:\Users\Arjun Menon\Desktop\SCORE\test.csv'


def read_data(path):
    with open(path, 'rU') as data:
        reader = csv.reader(data)
        next(reader)  # Skip first fields line
        for record in map(inventorRecord._make, reader):
            yield record


def gen_features_positive():
    cluster = []
    inventor_clusters = []
    for inv_id, row in enumerate(read_data(file.file)):   # Update with inventors for test
        if not cluster:
            cluster.append(row)
        else:
            if cluster[-1].cluster == row.cluster:
                cluster.append(row)
            else:
                inventor = InventorCluster(cluster)
                inventor_clusters.append(inventor)
                inventor.generate_pos_pairs()
                inventor.pairwise_feature_extraction(1)
                cluster = [row]
                print('--------------------NEXT INVENTOR @ ', inv_id, '--------------------')
    inventor = InventorCluster(cluster)
    inventor_clusters.append(inventor)
    inventor.generate_pos_pairs()
    inventor.pairwise_feature_extraction(1)
    return inv_clusters


def gen_features_random_negative(inventor_clusters, num_pairs):
    count = 0
    for i in range(len(inventor_clusters)):
        for j in range(i+1, len(inventor_clusters)):
            pairs = list(product(inventor_clusters[i].cluster, inventor_clusters[j].cluster))
            for pair in pairs:
                inventor1, inventor2 = pair
                pair = Pair(inventor1, inventor2)
                feature_vector = pair.generate_vector_pair(0)
                print(feature_vector)
                count += 1
                if count == num_pairs:
                    return


class InventorCluster:
    def __init__(self, inventor_cluster):
        self.cluster = inventor_cluster
        self.pairs = []

    def generate_pos_pairs(self):
        self.pairs = list(combinations(self.cluster, 2))

    def pairwise_feature_extraction(self, label):
        for pair in self.pairs:
            inventor1, inventor2 = pair
            pair = Pair(inventor1, inventor2)
            feature_vector = pair.generate_vector_pair(label)
            print(feature_vector)


if __name__ == "__main__":
    inv_clusters = gen_features_positive()
    print("-----------------Negative Random------------------")
    gen_features_random_negative(inv_clusters, 20)
    print('Success')

