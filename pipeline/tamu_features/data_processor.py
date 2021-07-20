"""
Texas A&M DARPA SCORE Feature Processing/Aggregation
"""

from datetime import date
import pandas as pd
import numpy as np
import requests
import warnings
import json
import ast
import pdb
from tamu_features.sentiment_model import Sentiment
from collections import defaultdict

class DataProcessor:
    def __init__(self, training_dir, google_scholar_data, verbose=0):
        # self.sciBertAPi = sciBertAPi
        self.google_scholar_data = google_scholar_data
        self.verbose = verbose
        self.TRAINING_DIR = training_dir
        self.imputed_list = []
        self.training_data = pd.read_csv(self.TRAINING_DIR + r"/processed_gold_data.csv")
        self.classify = Sentiment()

    def accumulate_author_stats(self, author_data, authors):
        author_ids = [s for s in ast.literal_eval(str(authors)) if s is not None]
        #if not self.google_scholar_data:
        #   author_ids = [int(s) for s in author_ids]
        author_mat = []
        auth_columns = ['Publications', 'h-index', 'Citations']
        if not self.google_scholar_data:
            auth_columns.append('Highly Influential Citations')
        for author_id in author_ids:
            if not self.google_scholar_data:
                publication, h_index, citations, high_inf_citations = (author_data.loc[author_data['authorId'] == author_id][auth_columns]).iloc[0]
                if str(publication) == 'nan':
                    continue
                author_mat.append([int(publication), int(h_index), int(citations), int(high_inf_citations)])
            else:
                publication, h_index, citations = \
                    (author_data.loc[author_data['authorId'] == author_id][auth_columns]).iloc[0]
                author_mat.append([int(publication), int(h_index), int(citations)])
        author_mat = np.asarray(author_mat)
        return author_mat

    def get_average_stats(self, author_mat):
        if len(author_mat) == 0:
            if not self.google_scholar_data:
                return [0] * 4
            else:
                return [0] * 3
        return np.mean(author_mat, axis=0)

    def get_max_stats(self, author_mat):
        if len(author_mat) == 0:
            if not self.google_scholar_data:
                return [0] * 4
            else:
                return [0] * 3
        return np.max(author_mat, axis=0)

    def get_first_author_stats(self, author_mat):
        if len(author_mat) == 0:
            if not self.google_scholar_data:
                return [0] * 4
            else:
                return [0] * 3
        return author_mat[0]

    def get_last_author_stats(self, author_mat):
        if len(author_mat) == 0:
            if not self.google_scholar_data:
                return [0] * 4
            else:
                return [0] * 3
        return author_mat[-1]

    def impute_author_data(self, df):
        column_list = ['avg_pub', 'avg_hidx', 'avg_auth_cites',
                       'max_pub', 'max_hidx', 'max_auth_cites',
                       'first_pub', 'first_hidx', 'first_auth_cites',
                       'last_pub', 'last_hidx', 'last_auth_cites']
        self.imputed_list.extend(column_list)
        val_list = self.training_data[column_list].mean().values
        for i in range(len(column_list)):
            df[column_list[i]] = 0.0
            df[column_list[i]][0] = val_list[i]
        return df

    def process_auth_data_google_scholar(self, df, author_data):
        if df.empty:
            defaults = {k: 0 for k in df.columns}
            df = df.append(defaults, ignore_index=True)
        if len(author_data) == 0:
            return self.impute_author_data(df)
        df['avg_pub'], df['avg_hidx'], df['avg_auth_cites'] = '', '', ''
        df['max_pub'], df['max_hidx'], df['max_auth_cites'] = '', '', ''
        df['first_pub'], df['first_hidx'], df['first_auth_cites'] = '', '', ''
        df['last_pub'], df['last_hidx'], df['last_auth_cites'] = '', '', ''
        authors = str(list(author_data['authorId']))
        for index, row in df.iterrows():
            if df['avg_pub'][index] == '':
                author_mat = self.accumulate_author_stats(author_data, authors)
                df['avg_pub'][index], df['avg_hidx'][index], df['avg_auth_cites'][index] = self.get_average_stats(
                    author_mat)
                df['max_pub'][index], df['max_hidx'][index], df['max_auth_cites'][index] = \
                    self.get_max_stats(author_mat)
                df['first_pub'][index], df['first_hidx'][index], df['first_auth_cites'][
                    index] = self.get_first_author_stats(author_mat)
                df['last_pub'][index], df['last_hidx'][index], df['last_auth_cites'][index] = \
                    self.get_last_author_stats(author_mat)
            # print("Done with Index: " + str(index))

        df = df.astype({"avg_pub": float, "avg_hidx": float, "avg_auth_cites": float,
                        "max_pub": float, "max_hidx": float, "max_auth_cites": float,
                        "first_pub": float, "first_hidx": float, "first_auth_cites": float,
                        "last_pub": float, "last_hidx": float, "last_auth_cites": float})
        # Adding citation count per year
        current_year = date.today().year
        df['citation_count_per_year'] = df['citations_count'] / (current_year - df['year'] + 1)
        return df

    def process_auth_data(self, df, author_data):
        if len(author_data)==0:
            return pd.DataFrame()
        if self.google_scholar_data:
            return self.process_auth_data_google_scholar(df, author_data)
        # Adding author stats
        df['avg_pub'], df['avg_hidx'], df['avg_auth_cites'], df['avg_high_inf_cites'] = '', '', '', ''
        df['max_pub'], df['max_hidx'], df['max_auth_cites'], df['max_high_inf_cites'] = '', '', '', ''
        df['first_pub'], df['first_hidx'], df['first_auth_cites'], df['first_high_inf_cites'] = '', '', '', ''
        df['last_pub'], df['last_hidx'], df['last_auth_cites'], df['last_high_inf_cites'] = '', '', '', ''
        authors = str(list(author_data['authorId']))
        for index, row in df.iterrows():
            if df['avg_pub'][index] == '':
                author_mat = self.accumulate_author_stats(author_data, authors)
                df['avg_pub'][index], df['avg_hidx'][index], df['avg_auth_cites'][index], df['avg_high_inf_cites'][
                    index] = self.get_average_stats(author_mat)
                df['max_pub'][index], df['max_hidx'][index], df['max_auth_cites'][index], df['max_high_inf_cites'][
                    index] = self.get_max_stats(author_mat)
                df['first_pub'][index], df['first_hidx'][index], df['first_auth_cites'][index], \
                    df['first_high_inf_cites'][index] = self.get_first_author_stats(author_mat)
                df['last_pub'][index], df['last_hidx'][index], df['last_auth_cites'][index], df['last_high_inf_cites'][
                    index] = self.get_last_author_stats(author_mat)
            # print("Done with Index: " + str(index))

        df = df.astype({"avg_pub": float, "avg_hidx": float, "avg_auth_cites": float, "avg_high_inf_cites": float,
                        "max_pub": float, "max_hidx": float, "max_auth_cites": float, "max_high_inf_cites": float,
                        "first_pub": float, "first_hidx": float, "first_auth_cites": float,
                        "first_high_inf_cites": float,
                        "last_pub": float, "last_hidx": float, "last_auth_cites": float, "last_high_inf_cites": float})
        # Adding citation count per year
        #current_year = date.today().year
        #df['citation_count_per_year'] = df['citations_count'] / (current_year - df['year'] + 1)
        # Adding influential citation count per year
        #current_year = date.today().year
        #df['inf_citation_count_per_year'] = df['influentialCitationCount'] / (current_year - df['year'] + 1)
        return df

    def processFieldOfStudy(self, df):
        df['fos'].fillna('', inplace=True)
        df['fos_Physcology'] = df.apply(lambda row: 1 if 'Psychology' in row['fos'] else 0, axis=1)
        df['fos_Business_Economics'] = df.apply(lambda row: 1 if 'Business & Economics' in row['fos'] else 0, axis=1)
        df['fos_Government_Law'] = df.apply(lambda row: 1 if 'Governmenr & Law' in row['fos'] else 0, axis=1)
        df['fos_Sociology'] = df.apply(lambda row: 1 if 'Sociology' in row['fos'] else 0, axis=1)
        df['fos_Education_Educational_Research'] = df.apply(
            lambda row: 1 if 'Education & Educational Research' in row['fos'] else 0, axis=1)
        df['fos_International_Relations'] = df.apply(lambda row: 1 if 'International Relations' in row['fos'] else 0,
                                                     axis=1)
        df['fos_Public_Administration'] = df.apply(lambda row: 1 if 'Public Administration' in row['fos'] else 0,
                                                   axis=1)
        df['fos_Other'] = df.apply(
            lambda row: 0 if (row['fos_Physcology'] or row['fos_Business_Economics'] or row['fos_Government_Law']
                              or row['fos_Sociology'] or row['fos_Education_Educational_Research']
                              or row['fos_International_Relations'] or row['fos_Public_Administration']) else 1, axis=1)
        del df['fos']
        return df

    def processMiscFeatures(self, df):
        df['paper_age'] = date.today().year - df['year']
        if self.google_scholar_data:
            columns_to_be_dropped = ['title', 'abstract', 'claim2_abstract', 'claim4_inftest', 'claim3a_concretehyp',
                                     'claim3b_testspec']
        else:
            columns_to_be_dropped = ['arxivId', 'authors', 'corpusId', 'doi', 'url', 'is_publisher_licensed',
                                     'influentialCitationCount',
                                     'year', 'citations', 'venue', 'fieldsOfStudy', 'title', 'abstract',
                                     'claim2_abstract', 'claim4_inftest', 'claim3a_concretehyp', 'claim3b_testspec']
        df = df.drop(columns_to_be_dropped, axis=1)
        return df
    def processDownstreamData(self,base_df,downstream):
        toKey={'Target Sentiment Not Found':0,'Positive-Consistent':1,'Negative-Inconsistent':2}
        di=defaultdict()
        di[-1] = -1
        try:
            for i,row in downstream.iterrows():
                try:
                    if isinstance(row.abstract,str):
                        label=self.classify.classify(row.abstract)
                        if label in di.keys():
                            di[label]+=1
                        else:
                            di[label]=1
                except:
                    continue
            #pdb.set_trace()
            print(di)
            if 'Target Sentiment Not Found' in di.keys():
                del di['Target Sentiment Not Found']
            key = max(di, key=di.get)
            if key == -1:
                key = 'Target Sentiment Not Found'
            if key in toKey.keys():
                base_df['sentiment_agg'] = int(toKey[key])
            else:
                base_df['sentiment_agg'] = 0
        except Exception as e:
            print(str(e))
            base_df['sentiment_agg'] = 0
            return base_df
        return base_df
        
        
    def processData(self, df, auth_df, downstream_df=None):
        df_intermediate = self.process_auth_data(df, auth_df)
        #df_intermediate = self.processFieldOfStudy(df_intermediate)
        # if not self.google_scholar_data:
        #     df_intermediate = self.processDownstreamData(df_intermediate, downstream_df)
        # df_intermediate = self.processTextData(df_intermediate)
        #processed_df = self.processMiscFeatures(df_intermediate)
        df_intermediate = self.processDownstreamData(df_intermediate,downstream_df)
        return df_intermediate, self.imputed_list
