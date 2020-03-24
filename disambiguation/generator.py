# Author: Arjun Menon <amm8987@psu.edu>

"""
This script generates pairs from inventors data.
"""

from feature_extractor import get_patents_similar_inventor, get_patent_features, get_inventor_features
from utilities import csv_writer, csv_write_field_header, csv_write_record
from utilities import token_fields, string_fields
from pair_feature_extraction import Pair
from collections import namedtuple
from mysql_conn import connect_db
from itertools import combinations, product
from utilities import check_file, mysql_breckenridge
from mysql.connector.errors import Error, InternalError
import argparse
import csv

fields = ('patent_id', 'cluster', 'title', 'inventor_id', 'name_first', 'name_last', 'section', 'subsection',
          'group', 'sub_group',  'city', 'state', 'long_lat', 'organization')
inventorRecord = namedtuple('inventor', fields)
inventorRecord.__new__.__defaults__ = (None,) * len(inventorRecord._fields)

parser = argparse.ArgumentParser(description='Specify target inventor csv')
parser.add_argument('-f', '--file', help='specify the inventor features csv file', type=check_file)
parser.add_argument('-o', '--output', help='specify computed pair feature vector output file')
file = parser.parse_args()

# inventors = r'C:\Users\Arjun Menon\Desktop\SCORE\test.csv'


def read_data(path):
    with open(path, 'rU') as data:
        reader = csv.reader(data)
        next(reader)  # Skip header field line
        for record in map(inventorRecord._make, reader):
            yield record


def get_csv_header():
    title = [tfield + '_cosine' for tfield in token_fields]
    title.extend([tfield + '_jaccard' for tfield in token_fields])
    title.extend([sfield + '_jw' for sfield in string_fields])
    title.extend([sfield + '_soundex' for sfield in string_fields])
    title.extend(['distance', 'truth'])
    return title


def gen_features_positive():
    cluster = []
    inventor_clusters = []
    tot_count = 0
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
                count = inventor.pairwise_feature_extraction(writer, 1)
                cluster = [row]
                print('--------------------NEXT INVENTOR @ ', inv_id, '--------------------')
                tot_count += count
    inventor = InventorCluster(cluster)
    inventor_clusters.append(inventor)
    inventor.generate_pos_pairs()
    count = inventor.pairwise_feature_extraction(writer, 1)
    tot_count += count
    print('Total postive pairs are: ', tot_count)
    return inventor_clusters, tot_count


def gen_features_random_negative(inventor_clusters, num_pairs):
    count = 0
    for i in range(len(inventor_clusters)):
        for j in range(i+1, len(inventor_clusters)):
            pairs = list(product(inventor_clusters[i].cluster, inventor_clusters[j].cluster))
            for pair in pairs:
                inventor1, inventor2 = pair
                pair = Pair(inventor1, inventor2)
                try:
                    feature_vector = pair.generate_vector_pair(0)
                except ValueError:
                    continue
                csv_write_record(writer, feature_vector, header)
                count += 1
                print('Random Negative Pair :', count, ' processed')
                if count == num_pairs:
                    return


def gen_negative_similar_name(inventor_clusters, num_pairs):
    count = 0
    for cluster in inventor_clusters:
        for inventor in cluster.cluster:
            try:
                patent_ids = get_patents_similar_inventor(cursor, inventor.name_first,
                                                      inventor.name_last, inventor.patent_id)
            except Error:
                print("Possible SQL query error --- skipping")
                continue
            for patent in patent_ids:
                try:
                    (p_title, p_section, p_subsec, p_group, p_subgroup, p_org) = get_patent_features(cursor, patent)
                    (i_long_lat, i_city, i_state) = get_inventor_features(cursor, patent, inventor.name_first,
                                                                          inventor.name_last)
                except TypeError:
                    continue
                temp_dict = {'title': p_title, 'name_first': inventor.name_first, 'name_last': inventor.name_last,
                             'section': p_section, 'subsection': p_subsec, 'group': p_group, 'sub_group': p_subgroup,
                             'city': i_city, 'long_lat': i_long_lat, 'state': i_state, 'organization': p_org}
                inventor_sim = inventorRecord(**temp_dict)
                pair = Pair(inventor, inventor_sim)
                try:
                    feature_vector = pair.generate_vector_pair(0)
                except (AttributeError, ValueError, InternalError):
                    print(inventor, ' Second:', inventor_sim)
                    continue
                csv_write_record(writer, feature_vector, header)
                count += 1
                print('Similar Negative Pair :', count, ' processed')
                if count == num_pairs:
                    return


class InventorCluster:
    def __init__(self, inventor_cluster):
        self.cluster = inventor_cluster
        self.pairs = []

    def generate_pos_pairs(self):
        self.pairs = list(combinations(self.cluster, 2))

    def pairwise_feature_extraction(self, csv_w, label):
        count = 0
        for pair in self.pairs:
            inventor1, inventor2 = pair
            pair = Pair(inventor1, inventor2)
            try:
                feature_vector = pair.generate_vector_pair(label)
            except ValueError:
                continue
            csv_write_record(csv_w, feature_vector, header)
            print('Positive Pair :', count, ' processed')
            count += 1
        return count


if __name__ == "__main__":
    con = connect_db(**mysql_breckenridge)
    # Get Cursor object
    cursor = con.cursor()
    # Get CSV writer object
    writer = csv_writer(file.output)
    header = get_csv_header()
    csv_write_field_header(writer, header)
    print("-----------------Positive------------------")
    inv_clusters, pos_count = gen_features_positive()
    print("-----------------Negative Random------------------")
    gen_features_random_negative(inv_clusters, round((3/4)*pos_count))   # Still experimenting with the second parameter
    print("-----------------Negative Similar------------------")
    gen_negative_similar_name(inv_clusters, round((1/4)*pos_count))  # Still experimenting with the second parameter
    print('Success')

