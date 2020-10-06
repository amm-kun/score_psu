# importing library 
import requests 
import pandas as pd
from fuzzywuzzy import fuzz
import os
import math
from datetime import datetime

_author_ = "Rajal Nivargi"
_copyright_ = "Copyright 2020, Penn State University"
_license_ = ""
_version_ = "1.0"
_maintainer_ = "Rajal Nivargi, Arjun Menon"
_email_ = "rfn5089@psu.edu"

def getapi(doi,title):
    # overall response from both apis: Elsevier and CrossRef is returned
    
    def getelsevier(doi,title):

        #URL generator: Incase the key exhausts the limit, go to https://dev.elsevier.com/index.html to generate a new one
        def scopus_search(query):

            # Example of DOI input: '10.1016/j.jesp.2018.04.001'

            doi = query.replace('/','%2F')  # For generating the URL correctly
            url = 'https://api.elsevier.com/content/search/scopus?query=' + doi + '&apiKey=60eac67a00256938d498a1f2ac68dc68'
            return url

        def serial_title(query):

            # Example of ISSN input: '00221031'
            issn = query
            url = 'https://api.elsevier.com/content/serial/title/issn/' + issn + '?apiKey=60eac67a00256938d498a1f2ac68dc68'
            return url

        def title_search(query):
            title = str(query).replace(' ','%2F')  # For generating the URL correctly
            url = 'https://api.elsevier.com/content/search/scopus?query=' + str(title) + '&apiKey=60eac67a00256938d498a1f2ac68dc68'
            return url

        #Return result as row
        def return_scopus(r,query,x):

                status = r.status_code
                query = str(query)
                if x == 'doi':
                    row = {'dc:title':float('NaN'),'prism:doi':query, 'prism:issn':'0', 'source-id':'0', 'prism:coverDate':'0', 'citedby-count':'0','openaccessFlag':'0'}
                    empty= pd.DataFrame(data = row, index = [0])
                if x == 'title':
                    row = {'prism:doi':float('NaN'),"dc:title":query, 'prism:issn':'0', 'source-id':'0', 'prism:coverDate':'0', 'citedby-count':'0','openaccessFlag':'0'}
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
                
                # Selecting only necessary features
                columns = ['prism:issn', 'prism:doi','source-id','prism:coverDate', 'citedby-count', 'openaccessFlag', 'dc:title','affiliation']
                if set(columns).issubset(entry.columns):
                    doi_entry = entry['prism:doi']
                    title_entry = entry["dc:title"]
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
                    if 'dc:title' in entry.columns:
                        new_columns.append('dc:title')
                    if 'affiliation' in entry.columns:
                        new_columns.append('affiliation')
                    if 'prism:doi' in entry.columns:
                        doi_entry = entry['prism:doi']
                    else:
                        entry['prism:doi']='none'
                    if 'dc:title' in entry.columns:
                        title_entry = entry["dc:title"]
                    else:
                        entry['dc:title'] = 'none'
                    entry = pd.DataFrame(data = entry.loc[:,new_columns])

                if 'affiliation' in entry.columns:
                    aff = entry['affiliation']
                    try:
                        list = aff[0]
                        aff_row = pd.DataFrame()
                        aff= pd.json_normalize(list[0])
                        aff = aff.drop(['@_fa', "affiliation-city"],axis=1)
                        aff_row = pd.concat([aff_row,aff], axis = 1)
                    except:
                        aff_row = pd.DataFrame()
                    entry = entry.drop(['affiliation'], axis = 1)
                    entry = pd.concat([entry,aff_row], axis=1)

                # Getting the entry matches the doi of required paper otherwsie return empty row
                for i in range(len(entry)):
                    if x =='doi':
                        doi_check = str(doi_entry[i])
                        if doi_check.lower()==query.lower():
                            row = entry.iloc[i,:]
                            row = pd.DataFrame(row)
                            date = row.loc['prism:coverDate']
                            x = datetime.strptime(date[i], '%Y-%m-%d')
                            row.loc['prism:coverDate'] = (x.year)
                            row = row.transpose()
                            return row
                    if x == 'title':
                            title_check = str(title_entry[i])
                            ratio = fuzz.partial_ratio(query.lower(),title_check.lower())
                            if ratio ==100:
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
                    columns = ['source-id','SJRList.SJR','SNIPList.SNIP','citeScoreYearInfoList.citeScoreCurrentMetric','citeScoreYearInfoList.citeScoreTracker','subject-area']
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
                        if 'citeScoreYearInfoList.citeScoreTracker' in entry.columns:
                            new_columns.append('citeScoreYearInfoList.citeScoreTracker')
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
                        SNIP = SNIP.rename(columns={"$":"SNIP"})
                        SNIP = SNIP.drop(["@_fa","@year"],axis = 1)
                        row = row.drop('SNIPList.SNIP', axis = 1)
                        row = pd.concat([row, SNIP],ignore_index=False, axis =1)

                    if 'SJRList.SJR' in entry.columns:
                        SJR = entry['SJRList.SJR']
                        SJR = pd.json_normalize(SJR[0])
                        SJR = SJR.rename(columns={"$":"SJR"})
                        SJR = SJR.drop(["@_fa","@year"],axis = 1)
                        row = row.drop('SJRList.SJR', axis = 1)
                        row = pd.concat([row, SJR],ignore_index=False, axis =1)
                    
                    if 'subject-area' in entry.columns:
                        sub = entry['subject-area']
                        list = sub[0]
                        sub_list = []
                        for i in range(len(list)):
                            subject= pd.json_normalize(list[i])
                            subject = subject["@code"]
                            sub_list.append(subject[0])
                        subject = int(sub_list[0])
                        if 1100<=subject<1200 or 1300<=subject<1400 or 2400<=subject<2500 or 2800<=subject<2900 or 3000<=subject<3100:
                            s = 1 # Life sciences
                        elif 1200<=subject<1300 or 1400<=subject<1500 or 1800<=subject<1900 or 2000<=subject<2100 or 3200<=subject<3400:
                            s = 2 # Social science and Humanities
                        elif 1500<=subject<1800 or 1900<=subject<2000 or 2100<=subject<2400 or 2500<=subject<2700 or 3100<=subject<3200:
                            s = 3 #Physical Sciences
                        elif 2700<=subject<2800 or 2900<=subject<3000 or 3400<=subject<3700:
                            s = 4 # Health Sciences
                        else:
                            s = 5 # Multidisciplinary
                        sub_list = {'subject' : s, 'subject_code':subject}
                        subject_row = pd.DataFrame(sub_list, index=[0])    
                        row = row.drop('subject-area', axis = 1)
                        row = pd.concat([row, subject_row],ignore_index=False, axis =1)
                        
                    return row
       
        # Scopus search api
        output = pd.DataFrame()
        query =doi
        if type(query) == str:
            # api-endpoint: 
            URL = scopus_search(query)
            # sending get request and saving the response as response object 
            r = requests.get(URL)
            #print(r.content)
            output = return_scopus(r,query,'doi')
        else:
            if query and math.isnan(query)==True:
                if type(title)==str:
                    URL = title_search(title)
                    r = requests.get(URL)
                    output = return_scopus(r,title,'title')
                    
                else:
                    output = {'dc:title':title,'prism:doi':query, 'prism:issn':'0', 'source-id':'0', 'prism:coverDate':'0', 'citedby-count':'0','openaccessFlag':'0'}
                    output = pd.DataFrame(data = output, index = [0])
            else:
                output = {'dc:title':title,'prism:doi':query, 'prism:issn':'0', 'source-id':'0', 'prism:coverDate':'0', 'citedby-count':'0','openaccessFlag':'0'}
                output = pd.DataFrame(data = output, index = [0])



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

    def getCrosref(query,title):

        # URL generator: replace with email id to be contacted for errors
        def meta_url(query):
            url = 'https://api.crossref.org/works/' + str(query) +'?mailto=rfn5089@psu.edu'
            return url

        def title_url(query):
            title =str(query).replace(' ','+')  # For generating the URL correctly
            url = 'https://api.crossref.org/works?query=' + title + '?mailto=rfn5089@psu.edu'
            return url

        # Reponse from the api
        def get_row(r, query,x):
            try:
                data = r.json()
                if x == 'doi':
                    items = data['message']
                    data = pd.json_normalize(items)
                    row = {'doi':query,'citedby-count-crossref':'0','coverdate':0}
                    empty= pd.DataFrame(data = row, index = [0])
                if x == 'title':
                    data = data['message']
                    items = data['items']
                    data = pd.json_normalize(items)
                    row = {'title':query,'doi':'0','citedby-count-crossref':'0','coverdate':0}
                    empty= pd.DataFrame(data = row, index = [0])
                if r.status_code!=200:
                    print('status-error')
                    return empty
                dois = data['DOI']
                titles = data['title']
                
                flag=0
                if x=='doi':
                    for i in range(0,len(dois)):
                        doi_check = dois[i]
                        if str(doi_check.lower()) == str(query.lower()):
                            flag=0
                            index = i
                            doi = dois[i]
                            title = titles[i]
                            title = title[0]
                            break
                        else:
                            flag=0
                if x=='title':
                    
                    for i in range(0,len(titles)):
                        title_check = titles[i]
                        title_check = title_check[0]
                        ratio = fuzz.partial_ratio(query.lower(),title_check.lower())
                        if ratio>=95:
                            flag=0
                            index = i
                            doi = dois[i]
                            title = titles[i]
                            title = title[0]
                            break
                        else:
                            flag=0
                if flag==1:
                    return empty

                # Selecting only necessary features
                if 'created.date-parts' in data.columns:
                    date = data.loc[index,'created.date-parts'] 
                    date = date[0] #selecting the first in the list
                    date = date[0] #selecting the year
                else:
                    date = float('NaN')
                # Will be using subject of journal instead from Elsevier API
                #if 'subject' in data.columns:
                    #subject = data.loc[index,'subject']
                    #subject = str(subject)
                #else:
                    #subject = float('NaN')
                if 'is-referenced-by-count' in data.columns:
                    select = data.loc[index,'is-referenced-by-count']
                else:
                    select = float('NaN')

                d = {'doi': doi, 'title': title, 'coverdate': date, 'citedby-count-crossref': select}
                row = pd.DataFrame(data = d, index = [0])
                return row

            except:
                if x == 'doi':
                    row = {'doi':query,'citedby-count-crossref':'0','coverdate':0}
                    empty= pd.DataFrame(data = row, index = [0])
                if x == 'title':
                    row = {'title':query,'doi':'0','citedby-count-crossref':'0','coverdate': 0}
                    empty= pd.DataFrame(data = row, index = [0])
                return empty

        
        if type(query)== str:
            URL = meta_url(query)
            r = requests.get(URL)
            row = get_row(r,query,'doi')
        else:
            if query and math.isnan(query)==True:
                URL = title_url(title)
                r = requests.get(URL)
                row = get_row(r,title,'title')
            else:
                row = {'doi':query,'title':title,'citedby-count-crossref':'0','coverdate':0}
                row= pd.DataFrame(data = row, index = [0])
                
        return row

    # Semantic scholor API
    def getsemantic(doi):

        query = str(doi)
        URL= 'https://api.semanticscholar.org/v1/paper/'+query
        r = requests.get(URL)
        row = {'doi': query, 'title': float('NaN'), 'citationVelocity': 0, 'influentialCitationCount': 0,'is_open_access':0}
        empty= pd.DataFrame(data = row, index = [0])
        empty= pd.DataFrame(row, index = [0])
        if r.status_code!=200:
            return empty
        data = r.json()
        data = pd.json_normalize(data)
        doi_api = data['doi']
        title_api = data['title']
        
        for i in range(0,len(doi_api)):
            doi_check = doi_api[i]
            if str(doi_check.lower()) == str(query.lower()):
                flag=0
                index = i
                doi = doi_api[i]
                title = title_api[i]
                break
            else:
                flag=1
        if flag==1:
            return empty

        # Selecting only necessary features
        if 'references' in data.columns:
            references = data.loc[index,'references']
            references_count = len(references)
        else:
            references_count = 0
        if 'citationVelocity' in data.columns:
            velocity = data.loc[index,'citationVelocity'] 
        else:
            velocity = float('NaN')
        if 'influentialCitationCount' in data.columns:
            influentialcitation = data.loc[index,'influentialCitationCount']
        else:
            influentialcitation = float('NaN')
        if 'is_open_access' in data.columns:
            openaccess = data.loc[index,'is_open_access']
            
        else:
            openaccess = float('NaN')
        
        d = {'doi': query, 'title': title, 'citationVelocity': velocity, 'influentialCitationCount': influentialcitation,'is_open_access':openaccess,'references_count':references_count}
        row = pd.DataFrame(d, index = [0])
        return row
    
    def comparecitations(elsevier, crossref,semantic):
        output = pd.DataFrame()
        # Comparing the number of citations from both and choosing the highest one
        cite1 = elsevier.loc[:,'citedby-count']
        cite1 = cite1.fillna(0)
        cite2 = crossref.loc[:,'citedby-count-crossref']
        cite2 = cite2.fillna(0)
        c1 = int(cite1.iloc[0])
        c2 = int(cite2.iloc[0])
        
        if c1>c2:
            cite=c1
        else:
            cite=c2
        currentYear = datetime.now().year
        coverdate = crossref.loc[0,'coverdate']
        if coverdate == 0:
            normalized_citations = 0
        else:
            years = currentYear - int(coverdate)
            if years == 0:
                years = 1
            normalized_citations = cite/years
        c = {'num_citations':cite,'normalized_citations':normalized_citations}
        cite = pd.DataFrame(c,index = [0])

        # Comparing open access flag
        open1 = elsevier.loc[:,'openaccessFlag']
        open1 = open1.fillna(0)
        open1 = int(open1)
        open2 = semantic.loc[:,'is_open_access']
        open2 = open2.fillna(0)
        open2 = int(open2)
        open = []

        if (open1 == open2):
            open.append(open1)
        else:
            if (open1==1 or open2==1):
                open.append('1')
            else:
                open.append('0')
        
        open = pd.DataFrame(data = open, columns = ['openaccessflag'])
        #Generating a single row output from both apis
        elsevier = elsevier.drop(['prism:issn','prism:doi','source-id','prism:coverDate','citedby-count','dc:title','openaccessFlag'], axis=1)
        crossref = crossref.drop(['citedby-count-crossref'], axis = 1)
        semantic = semantic.drop(['doi','title','is_open_access'],axis = 1)
        output = pd.concat([crossref,cite,open,semantic], axis =1)
        output = pd.concat([output,elsevier], axis =1)
        
        return output

    crossref = getCrosref(doi,title)
    elsevier = getelsevier(doi,title)
    
    if type(doi) == str:
        semantic = getsemantic(doi)
    else:
        if doi and math.isnan(doi)==True:
            doi = crossref.loc[0,'doi']
        semantic = getsemantic(doi)

    final = comparecitations(elsevier,crossref,semantic)
    
    return final
