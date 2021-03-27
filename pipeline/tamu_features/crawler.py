"""
Texas A&M DARPA SCORE Feature Extraction
"""

from bs4 import BeautifulSoup
from scholarly import scholarly
import pandas as pd
import requests
import time
import ast
import re
import pickledb
import pdb

class PaperInfoCrawler:
    def __init__(self, input_file, venue_metadata_file, database, verbose=0):
        self.INPUT_FILE = input_file
        self.VENUE_METADATA_FILE = venue_metadata_file
        #self.paperid_database = pickledb.load(database + '/paperid.db',True)
        #self.author_database =  pickledb.load(database + '/author.db',True)
        self.paperid_database = False
        self.author_database = False
        self.verbose = False
        # self.socketio = socketio
        self.topN = 50

    @staticmethod
    def get_list(data_list, key):
        id_list = list()
        for data in data_list:
            id_list.append(data[key])
        return id_list

    def fetch_paper(self, search_query, db, data_row=None):
        if db.papers.get(search_query,False):
            paper=db.papers.get(search_query,False)
        else:
            api_url = 'https://partner.semanticscholar.org/v1/paper/'
            headers = {'x-api-key': 'I6SO5Ckndk67RitJNJOFR4d7jDiVpWOgaMFUhgkM'}
            result = requests.get(api_url + search_query, headers=headers)
            paper = result.json()
            db.papers[search_query] = paper
            #self.paperid_database.set(search_query,result.json())
            #self.paperid_database.dump()
        if 'error' in paper.keys():
            if paper['error'] == 'Paper not found':
                return None
        if 'message' in paper.keys():
            if paper['message'] == 'Forbidden':
                #time.sleep(300)
                result = requests.get(api_url + search_query)
                paper = result.json()
                db.papers[search_query] = paper
                #self.paperid_database.set(search_query,result.json())
                #self.paperid_database.dump()
        author_list = paper['authors']
        citations_list = paper['citations']
        author_id_list = self.get_list(author_list, 'authorId')
        citation_paper_id_list = self.get_list(citations_list, 'paperId')
        paper['authors'] = author_id_list
        paper['citations'] = citation_paper_id_list
        paper['citations_count'] = len(paper['citations'])
        if data_row is not None:
            paper['ISSN'] = data_row['ISSN_CR']
            if data_row['category'] == "":
                paper['fos'] = ', '.join(paper['fieldsOfStudy'])
            else:
                paper['fos'] = data_row['category']
            paper['claim2_abstract'] = data_row['claim2_abstract']
            paper['claim4_inftest'] = data_row['claim4_inftest']
            paper['claim3a_concretehyp'] = data_row['claim3a_concretehyp']
            paper['claim3b_testspec'] = data_row['claim3b_testspec']
            paper['pid'] = data_row['paper_id']
        del paper['references']
        del paper['topics']
        del paper['is_open_access']
        return paper

    def fetch_auth_data_google_scholar(self):
        base_url = 'https://scholar.google.com/citations?user='
        authors = []

        for aid in self.google_search_result.bib['author_id']:
            if aid is not None:
                author = scholarly.search_author_id(aid)
                authors.append(author.fill(sections=['basics', 'indices', 'publications']))

        author_info = []
        for author in authors:
            a_dict = {'authorId': author.id}
            auth_url = base_url + a_dict['authorId']
            a_dict['Publications'] = len(author.publications)
            a_dict['Citations'] = author.citedby
            a_dict['h-index'] = author.hindex
            front_end_info = {'meta': 'auth_meta', 'name': author.name, 'publications': a_dict['Publications'],
                              'url': auth_url,
                              'citations': a_dict['Citations'], 'h_index': a_dict['h-index']}
            print("GScholar Info: ", front_end_info)
            # self.socketio.emit('server_response', front_end_info, namespace='')
            author_info.append(a_dict)
        if len(author_info) == 0:
            front_end_info = {'meta': 'auth_meta', 'author_info_not_found': '1'}
            # self.socketio.emit('server_response', front_end_info, namespace='')
            print("GScholar Info: ", front_end_info)
        return pd.DataFrame(author_info)

    def fetchAuthorMetadata(self, author_url):
        if self.verbose: print('Hit: ' + author_url)
        try:
            authPage = requests.get(author_url)
            authSoup = BeautifulSoup(authPage.text, 'html.parser')
            stats = authSoup.find_all(class_='author-detail-card__meta-section__author-stats')[0].get_text()
            name = authSoup.find_all(class_='author-detail-card__author-name')[0].get_text()
            return stats, name
        except:
            print("Exception occured while fetching author metadata.")

    def fetchAuthData(self,df, auth, db, paper_not_found=False):
        if paper_not_found:
            return self.fetch_auth_data_google_scholar()
        if self.verbose:
            print("\nFETCHING AUTHOR FEATURES")
            print("--------------------------")
        start_time = time.time()
        BASE_URL = 'https://www.semanticscholar.org/author/'
        #authorIds = []
        #for auth_list in list(auth):
        #    authorIds = [int(s) for s in ast.literal_eval(str(auth_list)) if s is not None]
        auth_dict = []
        for authId in auth:
            authId.replace("'", '')
            d = {}
            d['authorId'] = authId
            if db.authors.get(authId,False):
                stats, name = db.authors.get(authId,False)
            else:
                authUrl = BASE_URL + str(authId)
                stats, name = self.fetchAuthorMetadata(authUrl)
                db.authors[authId] = (stats,name)
                #self.author_database.set(authId,(stats,name))
            data = re.findall('.*?[0-9,]+', stats)
            for info in data:
                info_detail = re.split(r'([\d+,]*\d+)', info)
                d[info_detail[0]] = int(info_detail[1].replace(",", ""))
            auth_dict.append(d)
            # self.socketio.emit('server_response', frontEndInfo, namespace='')
        # time.sleep(1)
        if self.verbose: 
            print("\nFetched " + str(len(auth)) + " author details in %s seconds." % (time.time() - start_time))
        if len(auth_dict) == 0:
            return None
        return pd.DataFrame(auth_dict)

    def addVenueFeatures(self, df, issn):
        columns = ['Print ISSN', 'Citation Count', 'Scholarly Output', 'Percent Cited', 'CiteScore', 'SNIP', 'SJR',
                   'RANK', 'Rank Out Of']
        all_venues = pd.read_csv(self.VENUE_METADATA_FILE)
        venue_info = all_venues[columns]
        df_with_venue = pd.merge(df, venue_info, left_on='ISSN', right_on='Print ISSN', how='left')
        imputed = False
        if df_with_venue['CiteScore'].isnull().values.any():
            for index, row in df_with_venue.iterrows():
                if len(all_venues[all_venues['E-ISSN'] == row['ISSN']]) != 0:
                    a, b, c, d, e, f, g, h, i = all_venues[all_venues['E-ISSN'] == row['ISSN']][columns].iloc[0]
                    df_with_venue['Citation Count'][index], df_with_venue['Scholarly Output'][index], \
                    df_with_venue['Percent Cited'][index] = b, c, d
                    df_with_venue['CiteScore'][index], df_with_venue['SNIP'][index], df_with_venue['SJR'][
                        index] = e, f, g
                    df_with_venue['RANK'][index], df_with_venue['Rank Out Of'][index] = h, i
                else:
                    print("Imputing venue!!")
                    imputed = True
                    venue_info = all_venues[columns[1:]]
                    for col, val in venue_info.mean().iteritems():
                        df_with_venue[col][index] = val
        df_with_venue['Venue Rank Ratio'] = df_with_venue['RANK'] / df_with_venue['Rank Out Of']
        #frontEndInfo = {'meta': 'venue_meta', 'citation_count': str(int(df_with_venue['Citation Count'][0])),
        #                'scholarly_output': str(int(df_with_venue['Scholarly Output'][0])),
        #                'percent_cited': str(round(df_with_venue['Percent Cited'][0], 2)),
        #                'cite_score': str(round(df_with_venue['CiteScore'][0], 2)),
        #                'snip': str(round(df_with_venue['SNIP'][0], 2)),
        #                'sjr': str(round(df_with_venue['SJR'][0], 2)),
        #                'rank_ratio': str(round(df_with_venue['Venue Rank Ratio'][0], 2))}
        #if not imputed:
            # self.socketio.emit('server_response', frontEndInfo, namespace='')
            # print("Venue Features: ", frontEndInfo)
        df_with_venue = df_with_venue.drop(['ISSN', 'Print ISSN', 'RANK', 'Rank Out Of'], axis=1)
        venue_name_dict = {'Citation Count': 'Venue_Citation_Count', 'Scholarly Output': 'Venue_Scholarly_Output',
                           'Percent Cited': 'Venue_Percent_Cited', 'CiteScore': 'Venue_CiteScore', 'SNIP': 'Venue_SNIP',
                           'SJR': 'Venue_SJR'}

        df_with_venue.rename(columns=venue_name_dict, inplace=True)
        return df_with_venue

    def fetchDownStreamData(self, citations, db):
        if self.verbose:
            print("\nFETCHING DOWNSTREAM PAPERS")
            print("--------------------------")
        start_time = time.time()
        fetchedPapers = []
        citations = self.get_list(citations, 'paperId')
        downstreamPapersIds = set(citations)
        p_count = 0
        if len(downstreamPapersIds) == 0:
            frontEndInfo = {'meta': 'downstream_meta', 'no_citations_found': '1'}
            # self.socketio.emit('server_response', frontEndInfo, namespace='')
        for paperId in downstreamPapersIds:
            if p_count == self.topN: break
            search_attempt = 1
            while True:
                try:
                    paper = self.fetch_paper(paperId,db)
                    if paper == None:
                        print("Paper not found for query: ", paperId)
                        break
                    fetchedPapers.append(paper)
                    frontEndInfo = {'meta': 'downstream_meta', 'paper_id': paper['paperId'], 'title': paper['title'],
                                    'url': paper['url'], 'year': paper['year']}
                    if 'doi' in paper and paper['doi'] is not None:
                        frontEndInfo['doi'] = paper['doi']
                    if 'abstract' in paper and paper['abstract'] is not None:
                        frontEndInfo['abstract'] = paper['abstract'][:min(350, len(paper['abstract']))] + '...'
                    # self.socketio.emit('server_response', frontEndInfo, namespace='')
                    if self.verbose: print(str(paperId) + ' done.')
                    p_count += 1
                    break
                except Exception as e:
                    print("\nException for query: ", paperId + " " + str(e))
                    if search_attempt == 3:
                        print("Failed paper with paperId: ", paperId)
                        time.sleep(10)
                        break
                    search_attempt += 1
        if self.verbose: print(
            "\nFetched " + str(len(downstreamPapersIds)) + " papers in %s seconds." % (time.time() - start_time))
        return pd.DataFrame(fetchedPapers)

    def crawl(self, paper_id):
        if self.verbose:
            print("\nFETCHING BASE FEATURES")
            print("--------------------------")
        if 'tsv' in self.INPUT_FILE:
            input_file = pd.read_csv(self.INPUT_FILE, sep='\t')
        else:
            input_file = pd.read_csv(self.INPUT_FILE)
        try:
            input_file = input_file.loc[input_file['paper_id'] == paper_id]
        except KeyError:
            input_file = input_file.loc[input_file['ta3_pid'] == paper_id]
        input_file["category"].fillna("", inplace=True)
        input_file["publication_CR"].fillna("", inplace=True)
        fetchedPapers = []
        DOI_list = list(input_file['DOI_CR'])
        notFoundList = []
        start_time = time.time()
        paper_not_found = False
        for index, row in input_file.iterrows():
            DOI = row['DOI_CR']
            search_attempt = 1
            while True:
                try:
                    paper = self.fetch_paper(DOI, row)
                    if paper == None:
                        if self.verbose: print("Paper not found for query: ", DOI)
                        paper_not_found = True
                        notFoundList.append(DOI)
                        break
                    fetchedPapers.append(paper)
                    publication = row['publication_CR']
                    if publication == "":
                        publication = paper['venue']
                    frontEndInfo = {'meta': 'paper_meta', 'paper_found': '1', 'title': paper['title'],
                                    'abstract': paper['abstract'],
                                    'url': paper['url'], 'cite_count': paper['citations_count'], 'year': paper['year'],
                                    'publication': publication, 'category': paper['fos']}
                    # print("Info: ", frontEndInfo)
                    # self.socketio.emit('server_response', frontEndInfo, namespace='')
                    if self.verbose: print(str(DOI) + ' done.')
                    break
                except Exception as e:
                    print("\nException for query: ", DOI)
                    if search_attempt == 3:
                        # print("Failed paper with DOI: ", DOI)
                        #time.sleep(120)
                        break
                    search_attempt += 1
        downstream_df = None
        if paper_not_found:
            input_file.reset_index(inplace=True)
            try:
                df = input_file[['paper_id', 'title_CR', 'abstract', 'pub_year_CR', 'ISSN_CR', 'category', 'claim2_abstract',
                        'claim3a_concretehyp', 'claim3b_testspec', 'claim4_inftest']]
            except KeyError:
                df = input_file[['ta3_pid', 'title_CR', 'abstract', 'pub_year_CR', 'ISSN_CR', 'category', 'claim2_abstract',
                        'claim3a_concretehyp', 'claim3b_testspec', 'claim4_inftest']]
            search_query = scholarly.search_pubs(df['title_CR'][0])
            self.google_search_result = next(search_query)
            try:
                citations_count = self.google_search_result.bib['cites']
            except KeyError:
                citations_count = 0
            df['citations_count'] = int(citations_count)
            try:
                url = self.google_search_result.bib['url']
            except KeyError:
                url = ''
            frontEndInfo = {'meta': 'paper_meta', 'paper_found': '0', 'title': df['title_CR'][0],
                            'abstract': df['abstract'][0],
                            'url': url, 'cite_count': int(citations_count), 'year': int(df['pub_year_CR'][0]),
                            'publication': input_file['publication_CR'][0], 'category': df['category'][0]}
            # self.socketio.emit('server_response', frontEndInfo, namespace='')
            # print("Info:", frontEndInfo)
            df.rename(columns={'paper_id': 'pid', 'title_CR': 'title', 'pub_year_CR': 'year', 'ISSN_CR': 'ISSN',
                               'category': 'fos'}, inplace=True)
            auth_df = self.fetchAuthData(df, paper_not_found)
        else:
            if self.verbose: print(
                "\nFetched " + str(len(input_file)) + " papers in %s seconds." % (time.time() - start_time))
            df = pd.DataFrame(fetchedPapers)
            # self.socketio.emit('server_response', {'meta': 'store_paperId_session', 'paperId': df['paperId'].iloc[0]},
            #                    namespace='')
            # print("Meta: ",  {'meta': 'store_paperId_session', 'paperId': df['paperId'].iloc[0]})
            df = self.addVenueFeatures(df)
            auth_df = self.fetchAuthData(df, paper_not_found)
            # Commenting out downstream for now
            # downstream_df = self.fetchDownStreamData(df)
        # return df, auth_df, downstream_df, notFoundList
        return df, auth_df, notFoundList

    def simple_crawl(self, p_id, issn, auth, citations,db):
        if issn == '-1':
            try:
                input_file = None
                if 'tsv' in self.INPUT_FILE:
                    input_file = pd.read_csv(self.INPUT_FILE, sep='\t')
                else:
                    input_file = pd.read_csv(self.INPUT_FILE)
                if input_file and input_file[input_file['DOI_CR'] == p_id]['ISSN_CR'].values:
                    issn = input_file[input_file['DOI_CR'] == p_id]['ISSN_CR'].values[0]
            except Exception as e:
                print(e)
        #df with ISSN hopefully
        print("*****ISSN ", issn )
        venue_df,auth_df,downstream_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        try:
            if issn!='-1':
                data = {'ISSN':issn}
                df = pd.DataFrame(data,index = [0])
                venue_df = self.addVenueFeatures(df, issn)
            if auth:
                paper_not_found = False
                auth_df = self.fetchAuthData(venue_df ,auth , db, paper_not_found)
            if len(citations)>0:
                downstream_df = self.fetchDownStreamData(citations,db)
            #return df,auth_df,downstream_df
            notFoundList = []
            return venue_df, auth_df, downstream_df
        except Exception as e:
            print(traceback.format_exc())
            return venue_df, auth_df, downstream_df