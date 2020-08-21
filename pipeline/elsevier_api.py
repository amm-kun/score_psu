import requests
import pandas as pd
import os
import math
from datetime import datetime

_author_ = "Rajal Nivargi"
_copyright_ = "Copyright 2020, Penn State University"
_license_ = ""
_version_ = "1.0"
_maintainer_ = "Rajal Nivargi, Arjun Menon"
_email_ = "rfn5089@psu.edu"


def get_elsevier(doi):
    # URL generator: In case the key exhausts the limit, go to https://dev.elsevier.com/index.html to generate a new one
    def scopus_search(query):

        # Example of DOI input: '10.1016/j.jesp.2018.04.001'

        doi = query.replace('/', '%2F')  # For generating the URL correctly
        url = 'https://api.elsevier.com/content/search/scopus?query=' + doi + '&apiKey=f81795bcd97d071e6a60f88e6c3329a8'
        return url

    def serial_title(query):

        # Example of ISSN input: '00221031'

        issn = query
        url = 'https://api.elsevier.com/content/serial/title/issn/' + issn + '?apiKey=f81795bcd97d071e6a60f88e6c3329a8'
        return url

    # Function to return result as row

    # Return result as row
    def return_scopus(r, query):
        status = r.status_code
        query = str(query)

        # Checking the status code: success_code = 200. Otherwise, return empty row
        if status != 200:
            # print('Error_status ', status, ' DOI: ', query)
            row = {'prism:doi': query, 'prism:issn': '0', 'source-id': '0'}
            empty = pd.DataFrame(data=row, index=[0])
            return empty

        # Interpretating the Json response to give a dataframe
        data = r.json()
        search_results = data['search-results']
        df_search = pd.json_normalize(search_results)
        results = df_search['opensearch:totalResults']
        if results[0] == '0':
            row = {'prism:doi': query, 'prism:issn': '0', 'source-id': '0'}
            empty = pd.DataFrame(data=row, index=[0])
            return empty
        df = df_search['entry']
        df = df.tolist()
        entry = pd.json_normalize(df[0])

        # Affiliation json response t columns(affiliation city is not returned)
        try:
            aff = entry['affiliation']
            list = aff[0]
            aff_row = pd.DataFrame()
            for i in range(len(list)):
                aff = pd.json_normalize(list[i])
                col2 = "affilname_" + str(i)
                col3 = "affiliation-city_" + str(i)
                col4 = "affiliation-country_" + str(i)
                aff = aff.rename(columns={"affilname": col2, "affiliation-city": col3, "affiliation-country": col4})
                aff = aff.drop(['@_fa', col3], axis=1)
                aff_row = pd.concat([aff_row, aff], axis=1)
        except:
            aff_row = pd.DataFrame()

        # Selecting only necessary features
        columns = ['prism:issn', 'prism:doi', 'source-id', 'prism:coverDate', 'citedby-count', 'openaccessFlag']
        if set(columns).issubset(entry.columns):
            doi_entry = entry['prism:doi']
            entry = pd.DataFrame(data=entry.loc[:, columns])
        else:
            new_columns = []
            if 'prism:issn' in entry.columns:
                new_columns.append('prism:issn')
            elif 'prism:eIssn' in entry.columns:
                entry = entry.rename(columns={'prism:eIssn': 'prism:issn'})
                new_columns.append('prism:issn')
            else:
                entry['prism:issn'] = '0'
                new_columns.append('prism:issn')
            if 'prism:doi' in entry.columns:
                doi_entry = entry['prism:doi']
                new_columns.append('prism:doi')
            if 'source-id' in entry.columns:
                new_columns.append('source-id')
            else:
                entry['source-id'] = '0'
                new_columns.append('source-id')
            if 'prism:coverDate' in entry.columns:
                new_columns.append('prism:coverDate')
            if 'citedby-count' in entry.columns:
                new_columns.append('citedby-count')
            if 'openaccessFlag' in entry.columns:
                new_columns.append('openaccessFlag')
            entry = pd.DataFrame(data=entry.loc[:, new_columns])

        entry = pd.concat([entry, aff_row], axis=1)
        # Getting the entry which matches the title of the required paper otherwsie return empty row
        for i in range(len(entry)):
            doi_check = str(doi_entry[i])
            if doi_check.lower() == query.lower():
                row = entry.iloc[i, :]
                row = pd.DataFrame(row)
                date = row.loc['prism:coverDate']
                x = datetime.strptime(date[i], '%Y-%m-%d')
                row.loc['prism:coverDate'] = (x.year)
                row = row.transpose()
                return row
        # print('Error:', query)
        row = {'prism:doi': query, 'prism:issn': '0', 'source-id': '0'}
        empty = pd.DataFrame(data=row, index=[0])
        return empty

    def return_row(r, query):
        status = r.status_code
        empty = {'source-id': '0'}
        # Checking the status code: success_code = 200. Otherwise, return empty row
        if status != 200:
            # print('Error_status', status)
            empty = pd.DataFrame(empty, index=[0])
            return empty
        else:
            # Interpretating the Json response to give a dataframe
            data = r.json()
            search_results = data['serial-metadata-response']
            df = search_results['entry']
            flag = 0
            # entry = pd.json_normalize(df[0])
            for i in range(len(df)):
                entry = pd.json_normalize(df[i])
                id1 = entry['source-id'].tolist()
                id1 = id1[0]
                id2 = output['source-id'].tolist()
                id2 = id2[0]
                if id1 == id2:
                    flag = 1
                    j = i
            if flag == 1:
                entry = pd.json_normalize(df[j])
            else:
                empty = pd.DataFrame(empty, index=[0])
                return empty

                # Selecting only necessary features
            columns = ['source-id', 'SJRList.SJR', 'SNIPList.SNIP', 'citeScoreYearInfoList.citeScoreCurrentMetric',
                       'citeScoreYearInfoList.citeScoreCurrentMetricYear', 'citeScoreYearInfoList.citeScoreTracker',
                       'citeScoreYearInfoList.citeScoreTrackerYear', 'subject-area']
            if set(columns).issubset(entry.columns):
                entry = entry.loc[:, columns]
            else:
                new_columns = []
                if 'source-id' in entry.columns:
                    new_columns.append('source-id')
                if 'SJRList.SJR' in entry.columns:
                    new_columns.append('SNIPList.SNIP')
                if 'SNIPList.SNIP' in entry.columns:
                    new_columns.append('SNIPList.SNIP')
                if 'prism:coverDate' in entry.columns:
                    new_columns.append('prism:coverDate')
                if 'citeScoreYearInfoList.citeScoreCurrentMetric' in entry.columns:
                    new_columns.append('citeScoreYearInfoList.citeScoreCurrentMetric')
                if 'citeScoreYearInfoList.citeScoreCurrentMetricYear' in entry.columns:
                    new_columns.append('citeScoreYearInfoList.citeScoreCurrentMetricYear')
                if 'citeScoreYearInfoList.citeScoreTracker' in entry.columns:
                    new_columns.append('citeScoreYearInfoList.citeScoreTracker')
                if 'citeScoreYearInfoList.citeScoreTrackerYear' in entry.columns:
                    new_columns.append('citeScoreYearInfoList.citeScoreTrackerYear')
                if 'subject-area' in entry.columns:
                    new_columns.append('subject-area')
                try:
                    entry = pd.DataFrame(data=entry.loc[:, new_columns])
                except KeyError:
                    empty = pd.DataFrame(empty, index=[0])
                    return empty

            row = entry
            # Subject-area json response to columns(only subject is chosen as feature)
            # SJR and SNIP indicator json responses to columns
            if 'SNIPList.SNIP' in entry.columns:
                SNIP = entry['SNIPList.SNIP']
                SNIP = pd.json_normalize(SNIP[0])
                SNIP = SNIP.rename(columns={"@year": "@year_SNIP", "$": "SNIP"})
                SNIP = SNIP.drop(["@_fa"], axis=1)
                row = row.drop('SNIPList.SNIP', axis=1)
                row = pd.concat([row, SNIP], ignore_index=False, axis=1)

            if 'SJRList.SJR' in entry.columns:
                SJR = entry['SJRList.SJR']
                SJR = pd.json_normalize(SJR[0])
                SJR = SJR.rename(columns={"@year": "@year_SJR", "$": "SJR"})
                SJR = SJR.drop(["@_fa"], axis=1)
                row = row.drop('SJRList.SJR', axis=1)
                row = pd.concat([row, SJR], ignore_index=False, axis=1)

            if 'subject-area' in entry.columns:
                sub = entry['subject-area']
                list = sub[0]
                subject_row = pd.DataFrame()
                for i in range(len(list)):
                    subject = pd.json_normalize(list[i])
                    col1 = "@_fa_Subject_" + str(i)
                    col2 = "@code_subject_" + str(i)
                    col3 = "@abbrev_" + str(i)
                    col4 = "Subject_" + str(i)
                    subject = subject.rename(columns={"@_fa": col1, "@code": col2, "@abbrev": col3, "$": col4})
                    subject = subject.drop([col1, col2, col3], axis=1)
                    subject_row = pd.concat([subject_row, subject], axis=1)
                row = row.drop('subject-area', axis=1)
                row = pd.concat([row, subject_row], ignore_index=False, axis=1)

            return row

    # Scopus search api
    output = pd.DataFrame()

    query = doi
    temp = query
    try:
        if math.isnan(temp) == True:
            # print('Error_no_input')
            row = {'prism:doi': query, 'prism:issn': '0', 'source-id': '0'}
            output = pd.DataFrame(data=row, index=[0])
    except:
        # api-endpoint:
        URL = scopus_search(query)
        # sending get request and saving the response as response object
        r = requests.get(URL)
        # print(r.content)
        output = return_scopus(r, query)

    # Add 0's in the beginning of output from Scopus Search API
    issn = output['prism:issn']
    issn = str(issn.iloc[0])
    l = len(issn)
    if l != 8:
        issn = issn.ljust(8, '0')

    # Serial Title API
    output2 = pd.DataFrame()
    query = issn
    # api-endpoint:
    URL = serial_title(query)
    # sending get request and saving the response as response object
    r = requests.get(URL)
    response = return_row(r, query)
    output2 = output2.append(response, ignore_index=True)

    # Merging the output of the two apis to return Dataframe with required columns
    final = pd.merge(output, output2, on='source-id', how='outer')

    return final
