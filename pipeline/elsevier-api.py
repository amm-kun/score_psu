# importing library 
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

def getapi(doi):
    # overall response from both apis: Elsevier and CrossRef is returned
    
    def getelsevier(doi):

        #URL generator: Incase the key exhausts the limit, go to https://dev.elsevier.com/index.html to generate a new one
        def scopus_search(query):

            # Example of DOI input: '10.1016/j.jesp.2018.04.001'

            doi = query.replace('/','%2F')  # For generating the URL correctly
            url = 'https://api.elsevier.com/content/search/scopus?query=' + doi + '&apiKey=f81795bcd97d071e6a60f88e6c3329a8'
            return url

        def serial_title(query):

            # Example of ISSN input: '00221031'

            issn = query
            url = 'https://api.elsevier.com/content/serial/title/issn/' + issn + '?apiKey=f81795bcd97d071e6a60f88e6c3329a8'
            return url

        #Return result as row
        def return_scopus(r,query):
                status = r.status_code
                query = str(query)
                row = {'prism:doi':query, 'prism:issn':'0', 'source-id':'0', 'prism:coverDate':'0', 'citedby-count':'0'}
                empty= pd.DataFrame(data = row, index = [0])

                #Checking the status code: success_code = 200. Otherwise, return empty row
                if status!=200:
                    return empty
                
                # Interpretating the Json response to give a dataframe
                data = r.json()
                search_results = data['search-results']
                df_search = pd.json_normalize(search_results)
                results = df_search['opensearch:totalResults']
                if results[0]=='0':
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
                        aff= pd.json_normalize(list[i])
                        col2 = "affilname_"+str(i)
                        col3 = "affiliation-city_"+str(i)
                        col4 = "affiliation-country_"+str(i)
                        aff = aff.rename(columns={"affilname": col2,"affiliation-city":col3, "affiliation-country":col4})
                        aff = aff.drop(['@_fa', col3],axis=1)
                        aff_row = pd.concat([aff_row,aff], axis = 1)
                except:
                    aff_row = pd.DataFrame()

                # Selecting only necessary features
                columns = ['prism:issn', 'prism:doi','source-id','prism:coverDate', 'citedby-count', 'openaccessFlag']
                if set(columns).issubset(entry.columns):
                    doi_entry = entry['prism:doi']
                    entry = pd.DataFrame(data = entry.loc[:,columns])
                else:
                    new_columns = []
                    if 'prism:issn' in entry.columns:
                        new_columns.append('prism:issn')
                    elif 'prism:eIssn' in entry.columns:
                        entry = entry.rename(columns = {'prism:eIssn':'prism:issn'})
                        new_columns.append('prism:issn')
                    else:
                        entry['prism:issn'] ='0'
                        new_columns.append('prism:issn')
                    if 'prism:doi' in entry.columns:
                        doi_entry = entry['prism:doi']
                        new_columns.append('prism:doi')
                    if 'source-id' in entry.columns:
                        new_columns.append('source-id')
                    else:
                        entry['source-id'] ='0'
                        new_columns.append('source-id')
                    if 'prism:coverDate' in entry.columns:
                        new_columns.append('prism:coverDate')
                    if 'citedby-count' in entry.columns:
                        new_columns.append('citedby-count')
                    if 'openaccessFlag' in entry.columns:
                        new_columns.append('openaccessFlag')
                    entry = pd.DataFrame(data = entry.loc[:,new_columns])

                entry = pd.concat([entry,aff_row], axis=1)
                # Getting the entry matches the doi of required paper otherwsie return empty row
                for i in range(len(entry)):
                    doi_check = str(doi_entry[i])
                    if doi_check.lower()==query.lower():
                        row = entry.iloc[i,:]
                        row = pd.DataFrame(row)
                        date = row.loc['prism:coverDate']
                        x = datetime.strptime(date[i], '%Y-%m-%d')
                        row.loc['prism:coverDate'] = (x.year)
                        row = row.transpose()
                        return row
                return empty

        def return_row(r,query,source):
                status = r.status_code
                empty = {'source-id':source}
                empty= pd.DataFrame(empty, index = [0])
                
                #Checking the status code: success_code = 200. Otherwise, return empty row
                if status!=200:
                    return empty
                else:
                    # Interpretating the Json response to give a dataframe
                    data = r.json()
                    search_results = data['serial-metadata-response']
                    df = search_results['entry']
                    flag = 0
                    #entry = pd.json_normalize(df[0])
                    for i in range(len(df)):
                        entry = pd.json_normalize(df[i])
                        id1 = entry['source-id'].tolist()
                        id1 = id1[0]
                        id2 = output['source-id'].tolist()
                        id2 = id2[0]
                        if id1==id2:
                            flag=1
                            j=i
                    if flag==1:
                        entry = pd.json_normalize(df[j])
                    else:
                        return empty 
        
                    # Selecting only necessary features
                    columns = ['source-id','SJRList.SJR','SNIPList.SNIP','citeScoreYearInfoList.citeScoreCurrentMetric', 'citeScoreYearInfoList.citeScoreCurrentMetricYear','citeScoreYearInfoList.citeScoreTracker','citeScoreYearInfoList.citeScoreTrackerYear','subject-area']
                    if set(columns).issubset(entry.columns):
                        entry = entry.loc[:,columns]
                    else:
                        new_columns = []
                        if 'source-id' in entry.columns:
                            new_columns.append('source-id')
                        if 'SJRList.SJR' in entry.columns:
                            new_columns.append('SJRList.SJR')
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
                            return empty
                    
                    row = entry
                    # Subject-area json response to columns(only subject is chosen as feature)
                    # SJR and SNIP indicator json responses to columns
                    if 'SNIPList.SNIP' in entry.columns:
                        SNIP = entry['SNIPList.SNIP']
                        SNIP = pd.json_normalize(SNIP[0])
                        SNIP = SNIP.rename(columns={"@year": "@year_SNIP", "$":"SNIP"})
                        SNIP = SNIP.drop(["@_fa"],axis = 1)
                        row = row.drop('SNIPList.SNIP', axis = 1)
                        row = pd.concat([row, SNIP],ignore_index=False, axis =1)

                    if 'SJRList.SJR' in entry.columns:
                        SJR = entry['SJRList.SJR']
                        SJR = pd.json_normalize(SJR[0])
                        SJR = SJR.rename(columns={"@year": "@year_SJR", "$":"SJR"})
                        SJR = SJR.drop(["@_fa"],axis = 1)
                        row = row.drop('SJRList.SJR', axis = 1)
                        row = pd.concat([row, SJR],ignore_index=False, axis =1)
                    
                    if 'subject-area' in entry.columns:
                        sub = entry['subject-area']
                        list = sub[0]
                        sub_list = []
                        for i in range(len(list)):
                            subject= pd.json_normalize(list[i])
                            subject = subject["$"]
                            sub_list.append(subject[0])
                        sub_list = {'Subject' : str(sub_list)}
                        subject_row = pd.DataFrame(sub_list, index=[0]) 
                        row = row.drop('subject-area', axis = 1)
                        row = pd.concat([row, subject_row],ignore_index=False, axis =1)
                        
                    return row

        # Scopus search api
        output = pd.DataFrame()
        query =doi
        temp = query
        try:
            if math.isnan(temp)==True:
                row = {'prism:doi':query, 'prism:issn':'0', 'source-id':'0','prism:coverDate':'0','citedby-count':'0'}
                output= pd.DataFrame(data = row, index = [0]) 
        except :
            # api-endpoint: 
            URL = scopus_search(query)
            # sending get request and saving the response as response object 
            r = requests.get(URL)
            #print(r.content)
            output = return_scopus(r,query)

        # Add 0's in the beginning of output from Scopus Search API
        issn = output['prism:issn']
        issn = str(issn.iloc[0])
        l = len(issn)
        if l!=8:
            issn=issn.ljust(8, '0')
        source = output['source-id']
        source = source.iloc[0]

        # Serial Title API
        output2 = pd.DataFrame()
        query =issn
        # api-endpoint: 
        URL = serial_title(query)
        # sending get request and saving the response as response object 
        r = requests.get(URL)
        output2 = return_row(r,query,source)
    
        # Merging the output of the two apis to return Dataframe with required columns 
        final = pd.merge(output, output2,on='source-id', how = 'outer')
        
        return final

    def getCrosref(query):

        # URL generator: replace with personal id to be contacted for errors
        def meta_url(query):
            url = 'https://api.crossref.org/works/' + query +'?mailto=rfn5089@psu.edu'
            return url
        
        # Reponse from the api
        def get_row(r):
            row = {'doi_crossref':query, 'citedby-count-crossref':'0'}
            empty= pd.DataFrame(data = row, index = [0])

            #Checking the status code: success_code = 200. Otherwise, return empty row
            if r.status_code!=200:
                return empty
            # api response to dataframe 
            try:
                data = r.json()
                items = data['message']
                title = items['title']
                title = title[0] #response as list
                date = items['created']
                date = date['date-parts']
                date = date[0] #selecting the first created date
                date = date[0] #selecting the year
                items = pd.json_normalize(items)
                doi = items['DOI']
                doi = doi[0]
                select = items.loc[0,'is-referenced-by-count']
                d = {'doi_crossref': doi, 'title': title, 'coverdate_crossref': date, 'citedby-count-crossref': select}
                row = pd.DataFrame(data = d, index = [0])
                return row
            except:
                return empty
        
        try:
            # check if the value of doi is null
            if math.isnan(query)==True:
                row = {'doi_crossref':query, 'citedby-count-crossref':'0'}
                row = pd.DataFrame(data = row, index = [0]) 
        except:
            # api-endpoint
            URL = meta_url(query)
            r = requests.get(URL)
            row = get_row(r)
        return row
    
    def comparecitations(elsevier, crossref):
        output = pd.DataFrame()
        # Comparing the number of citations from both and choosing the highest one
        cite1 = elsevier.loc[:,'citedby-count']
        cite1 = cite1.fillna(0)
        cite2 = crossref.loc[:,'citedby-count-crossref']
        cite2 = cite2.fillna(0)
        cite = []
        c1 = int(cite1.iloc[0])
        c2 = int(cite2.iloc[0])
        
        if c1>c2:
            cite.append(c1)
        else:
            cite.append(c2)
        cite = pd.DataFrame(data = cite, columns = ['num_citations'])

        #Generating a single row output from both apis
        elsevier = elsevier.drop(['prism:issn','prism:doi','source-id','prism:coverDate','citedby-count'], axis=1)
        crossref = crossref.drop(['citedby-count-crossref'], axis = 1)
        output = pd.concat([crossref,cite], axis =1)
        output = pd.concat([output,elsevier], axis =1)
        output = output.rename(columns = {'doi_crossref':'doi','num_citations':'citedby-count', 'coverdate_crossref':'prism:coverDate'})
        return output

    elsevier = getelsevier(doi)
    crossref = getCrosref(doi)
    final = comparecitations(elsevier,crossref)
    
    return final
