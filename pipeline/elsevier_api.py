# %%
import requests 
import pandas as pd
from fuzzywuzzy import fuzz
import os
import math
from datetime import datetime
from collections import Counter
import pdb


# %%
class getcrossref:
    
    def __init__(self,doi,title):
        self.doi = doi
        self.title =title
        self.refcount = 0
        self.citedby = 0
        self.coverdate = 0
        self.ab = ''

    def get_row(self):
        query = self.doi
        if type(query)== str:
            url = 'https://api.crossref.org/works/' + str(query) +'?mailto=rfn5089@psu.edu'
            r = requests.get(url)
            x = 'doi'
            if r.status_code!=200:
                return {'doi':self.doi,'title':self.title,'citedby':self.citedby,'coverdate':self.coverdate,'references-count':self.refcount}
            data = r.json()
            items = data['message']
            data = pd.json_normalize(items)
        else:
            if query and math.isnan(query)==True:
                query=self.title
                if type(query)== str:
                    title =str(query).replace(' ','+')  # For generating the URL correctly
                    url = 'https://api.crossref.org/works?query=' + title + '?mailto=rfn5089@psu.edu'
                    r = requests.get(url)
                    if r.status_code!=200:
                        return {'doi':self.doi,'title':self.title,'citedby':self.citedby,'coverdate':self.coverdate,'references-count':self.refcount}
                    x = 'title'
                    data = r.json()
                    try:
                        data = data['message']
                        items = data['items']
                        data = pd.json_normalize(items)
                    except:
                        try:
                            items = data['message']
                            data = pd.json_normalize(items)
                        except:
                            data = pd.json_normalize(data)
                else:
                    return {'doi':self.doi,'title':self.title,'citedby':self.citedby,'coverdate':self.coverdate,'references-count':self.refcount}
            else:
                return {'doi':self.doi,'title':self.title,'citedby':self.citedby,'coverdate':self.coverdate,'references-count':self.refcount}
        try:
            dois = data['DOI']
            titles = data['title']
        except:
            dois = data['doi']
            titles = data['title']
        flag=0
        if x=='doi':
            for i in range(0,len(dois)):
                doi_check = dois[i]
                if str(doi_check.lower()) == str(query.lower()):
                    flag=0
                    index = i
                    self.doi = dois[i]
                    title = titles[i]
                    self.title = title
                    break
                else:
                    flag=1
        if x=='title':
            for i in range(0,len(titles)):
                title_check = titles[i]
                if isinstance(title_check, list):  
                    title_check = title_check[0]
                else:
                    flag =1
                    break
                ratio = fuzz.partial_ratio(query.lower(),title_check.lower())
                if ratio>=95:
                    flag=0
                    index = i
                    self.doi = dois[i]
                    title = titles[i]
                    self.title = title[0]
                    break
                else:
                    flag=1
        if flag==1:
            return {'doi':self.doi,'title':self.title,'citedby':self.citedby,'coverdate':self.coverdate,'references-count':self.refcount}

        # Selecting only necessary features
        if 'created.date-parts' in data.columns:
            date = data.loc[index,'created.date-parts'] 
            date = date[0] #selecting the first in the list
            self.coverdate = date[0] #selecting the year
        if 'is-referenced-by-count' in data.columns:
            select = data.loc[index,'is-referenced-by-count']
            self.citedby = select
        if 'reference-count' in data.columns:
            select = data.loc[index,'reference-count']
            self.refcount = select
        if 'abstract' in data.columns:
            self.ab = data.loc[index,'abstract']
      
        return {'doi':self.doi,'title':self.title,'citedby':self.citedby,'coverdate':self.coverdate,'references-count':self.refcount,'abstract':self.ab}

# %%
class getelsevier(getcrossref):

    def __init__(self,doi,title):
        super().__init__(doi,title)
        self.issn = '0'
        self.source = 0
        self.openaccess = 0
        self.affilname = float('NaN')
        self.affilcountry = float('NaN')
        self.sjr = 0
        self.subject = 0
        self.subject_code = 900
        self.normalized = 0
        self.next = 0

    def getaff(self,aff):
        try:
            list = aff[0]
            affilname = list['affilname']
            affilcountry = list['affiliation-country']
            return affilname,affilcountry
        except:
            return float('NaN'),float('NaN')
    
    # Response from scopus-search api
    def return_search(self):
                output = pd.DataFrame()
                query =self.doi
                if type(query) == str: 
                    doi = query.replace('/','%2F')  # For generating the URL correctly
                    url = 'https://api.elsevier.com/content/search/scopus?query=' + doi + '&apiKey=60eac67a00256938d498a1f2ac68dc68'
                    r = requests.get(url)
                    status = r.status_code
                    x= 'doi'
                else:
                    if query and math.isnan(query)==True:
                        query = self.title
                        if type(query)==str:
                            title = str(query).replace(' ','%2F')  # For generating the URL correctly
                            url = 'https://api.elsevier.com/content/search/scopus?query=' + str(title) + '&apiKey=60eac67a00256938d498a1f2ac68dc68'
                            r = requests.get(url)
                            status = r.status_code
                            x = 'title'
                        else:
                            status = 900
                    else:
                        return {"doi":self.doi,"title":self.title,"ISSN":self.issn,"source-id":self.source,"coverDate":self.coverdate,"citedby":self.citedby,"openaccessFlag":self.openaccess}
                if status!=200:
                    return {"doi":self.doi,"title":self.title,"ISSN":self.issn,"source-id":self.source,"coverDate":self.coverdate,"citedby":self.citedby,"openaccessFlag":self.openaccess}

                query = str(query)
                # Interpretating the Json response to give a dataframe
                data = r.json()
                search_results = data['search-results']
                df_search = pd.json_normalize(search_results)
                results = df_search['opensearch:totalResults']
                if results[0]=='0':
                    return {"doi":self.doi,"title":self.title,"ISSN":self.issn,"source-id":self.source,"coverDate":self.coverdate,"citedby":self.citedby,"openaccessFlag":self.openaccess}
                df = df_search['entry']
                df = df.tolist()
                entry = pd.json_normalize(df[0])
                if 'prism:doi' in entry.columns:
                    doi_entry = entry['prism:doi']
                else:
                    doi_entry = float('NaN')
                if 'dc:title' in entry.columns:
                    title_entry = entry["dc:title"]
                else:
                    title_entry = float('NaN')
                flag = 0
                #Checking all entrys for the paper
                for i in range(len(entry)):
                    if x =='doi':
                        doi_check = str(doi_entry[i])
                        if doi_check.lower()==query.lower():
                            row = entry.loc[i,:]
                            row = pd.DataFrame(row)
                            entry = row.transpose()
                            index = i
                            flag = 1
                            break
                        
                    if x == 'title':
                            title_check = str(title_entry[i])
                            ratio = fuzz.partial_ratio(query.lower(),title_check.lower())
                            if ratio ==90:
                                row = entry.iloc[i,:]
                                row = pd.DataFrame(row)
                                entry = row.transpose()
                                index = i
                                flag =1
                                break
                if flag == 0:
                    return {"doi":self.doi,"title":self.title,"ISSN":self.issn,"source-id":self.source,"coverDate":self.coverdate,"citedby":self.citedby,"openaccessFlag":self.openaccess}
                
                # Selecting only necessary features
                columns = ['prism:issn', 'prism:doi','source-id','prism:coverDate', 'citedby-count', 'openaccessFlag', 'dc:title','affiliation','citedby-count']
                if 'prism:issn' in entry.columns:
                    self.issn = entry.loc[index,"prism:issn"]
                    issn = self.issn
                    issn = str(issn)
                    l = len(issn)
                    if l!=8:
                        issn=issn.ljust(8, '0')
                    self.issn = issn
                elif 'prism:eIssn' in entry.columns:
                    self.issn = entry.loc[index,'prism:eIssn']
                    issn = self.issn
                    issn = str(issn)
                    l = len(issn)
                    if l!=8:
                        issn=issn.ljust(8, '0')
                    self.issn = issn
                if 'source-id' in entry.columns:
                    self.source = entry.loc[index,"source-id"]
                if 'prism:coverDate' in entry.columns:
                    date = entry.loc[index,'prism:coverDate']
                    date = datetime.strptime(date, '%Y-%m-%d')
                    date = date.year
                    if self.coverdate >= date: #Choose the older published date (assumption)
                        self.coverdate = date
                if 'citedby-count' in entry.columns:
                    citedby = entry.loc[index,'citedby-count']
                    if int(citedby)>int(self.citedby):
                        self.citedby = citedby
                if 'openaccessFlag' in entry.columns:
                    self.openaccess = int(entry.loc[index,'openaccessFlag'])
                if 'dc:title' in entry.columns:
                    self.title = entry.loc[index,"dc:title"]
                if 'affiliation' in entry.columns:
                    self.affilname,self.affilcountry = self.getaff(entry.loc[i,'affiliation'])
                if 'prism:doi' in entry.columns:
                    self.doi = entry.loc[i,'prism:doi']

                return {"doi":self.doi,"title":self.title,"ISSN":self.issn,"source-id":self.source,"coverDate":self.coverdate,"citedby":self.citedby, "openaccessFlag":self.openaccess, "affilname":self.affilname,"affiliation-country":self.affilcountry}

    def check_dict(self,source):
        dict = pd.read_csv('journal_dictionary.csv')
        source_ids = dict.loc[:,'source-id']
        for i in range(len(source_ids)):
            if source_ids[i]==source:
                index = i
                break
            else: 
                index = 100
        if index==100:
            return {'SJR':self.sjr,'subject':self.subject,'subject_code':self.subject_code}
        else:
            self.sjr = dict.loc[i,'SJR']
            self.subject = dict.loc[i,'subject']
            self.subject_code = dict.loc[i,'subject_code']
            self.source = dict.loc[i,'source-id']
            return {'SJR':self.sjr,'subject':self.subject,'subject_code':self.subject_code}

    def getsub(self,sub):
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
        elif subject==1000:
            s = 5 # Multidisciplinary
        else:
            s = 0
        self.subject = s
        self.subject_code = subject
        return self.subject,self.subject_code

    # Response from serial-title api
    def return_serialtitle(self):
        # Add 0's in the beginning of output from Scopus Search API
        issn = str(self.issn)
        source = self.source
        query = issn
        url = 'https://api.elsevier.com/content/serial/title/issn/' + issn + '?apiKey=60eac67a00256938d498a1f2ac68dc68'
        r = requests.get(url)
        status = r.status_code
        #Checking the status code: success_code = 200. Otherwise, return empty row
        if status!=200:
            return self.check_dict(source)

        # Interpretating the Json response to give a dataframe
        data = r.json()
        search_results = data['serial-metadata-response']
        df = search_results['entry']
        flag = 0
        for i in range(len(df)):
            entry = pd.json_normalize(df[i])
            id = entry['source-id'].tolist()
            id = id[0]
            if id==source:
                flag=1
                j=i
                break
        if flag==1:
            entry = pd.json_normalize(df[j])
        else:
            return self.check_dict(source) 
                    
        # Selecting only necessary features
        columns = ['SJRList.SJR','subject-area']
        if set(columns).issubset(entry.columns):
            SJR = entry['SJRList.SJR']
            SJR = pd.json_normalize(SJR[0])
            self.sjr = SJR.loc[0,"$"]
            sub = entry['subject-area']
            self.subject,self.subject_code = self.getsub(sub)
        else:
            if 'SJRList.SJR' in entry.columns:
                SJR = entry['SJRList.SJR']
                SJR = pd.json_normalize(SJR[0])
                self.sjr = SJR.loc[0,"$"]
            if 'subject-area' in entry.columns:
                sub = entry['subject-area']
                self.subject,self.subject_code = self.getsub(sub)

        return {'SJR':self.sjr,'subject':self.subject,'subject_code':self.subject_code}


# %%
class getsemantic(getelsevier):
    
    def __init__(self,doi,title,db):
        super().__init__(doi,title)
        self.velocity = -1
        self.incite = -1
        self.inref = -1
        self.refback = -1
        self.refresult = -1
        self.refmeth = -1
        self.cback = -1
        self.cresult = -1
        self.cmeth = -1
        self.upstream_influential_methodology_count = 0
        self.auth = [] 
        self.citations = []
        self.years = []
        self.ab = ''
        self.db = db
        self.age = 0

    def return_semantic(self):
        try:
            currentYear = datetime.now().year
            if self.coverdate == 0:
                self.normalized = 0
                self.age = 0
            elif self.coverdate == currentYear:
                self.normalized = self.citedby
                self.age = 1
            else:
                years = currentYear - int(self.coverdate)
                self.age = years
                self.normalized = int(self.citedby)/years

            query = self.doi
            if self.db.papers.get(query,False):
                data = self.db.papers.get(query)
            else:
                url = 'https://api.semanticscholar.org/v1/paper/'+str(query)
                r = requests.get(url)
                row = {"upstream_influential_methodology_count": self.upstream_influential_methodology_count, "normalized_citations":self.normalized, 'doi': self.doi, 'title':self.title, 'citationVelocity':self.velocity, 'influentialCitationCount':self.incite,'is_open_access':self.openaccess,'references_count':self.refcount,'influentialReferencesCount':self.inref,'reference_background':self.refback,'reference_result':self.refresult,'reference_methodology':self.refmeth,'citations_background':self.cback,'citations_result':self.cresult,'citations_methodology':self.cmeth}

                if r.status_code != 200:
                    return row

                data = r.json()
                self.db.papers[query] = r.json()

            # Get influential_methodology_references
            if self.doi:
                inf_meth_ref_count = 0
                try:
                    references = data['references']
                    for reference in references:
                        try:
                            if 'methodology' in reference['intent'] and reference['isInfluential']:
                                inf_meth_ref_count += 1
                        except KeyError:
                            continue
                except KeyError:
                    pass
                self.upstream_influential_methodology_count = inf_meth_ref_count

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
                return row

            # Selecting only necessary features
            #pdb.set_trace()
            if 'abstract' in data.columns:
                self.ab = data.loc[index,'abstract']
            if 'references' in data.columns:
                references = data.loc[index,'references']
                ref = pd.json_normalize(references)
                if 'isInfluential' in ref.columns:
                    inf = ref['isInfluential']
                    inf = inf.tolist()
                    self.inref = sum(bool(x) for x in inf)
                if 'intent' in ref.columns:
                    intent = ref['intent']
                    intent = intent.tolist()
                    flat_list = [item for sublist in intent for item in sublist]
                    self.refback = flat_list.count('background')
                    self.refresult = flat_list.count('result')
                    self.refmeth = flat_list.count('methodology')
                references_count = len(references)
                if references_count>int(self.refcount):
                    self.refcount = references_count
            if 'citationVelocity' in data.columns:
                self.velocity = data.loc[index,'citationVelocity'] 
            if 'influentialCitationCount' in data.columns:
                self.incite = data.loc[index,'influentialCitationCount']
            if 'is_open_access' in data.columns:
                openaccess = data.loc[index,'is_open_access']
                if openaccess>int(self.openaccess):
                    self.openaccess = int(openaccess)
            if 'citations' in data.columns:
                self.citations = data.loc[index,'citations']
                cit = pd.json_normalize(self.citations)
                if 'intent' in cit.columns:
                    cintent = cit['intent']
                    cintent = cintent.tolist()
                    cflat_list = [item for sublist in cintent for item in sublist]
                    self.cback = cflat_list.count('background')
                    self.cresult = cflat_list.count('result')
                    self.cmeth = cflat_list.count('methodology')
                if 'year' in cit.columns:
                    year = cit['year']
                    year = year.tolist()
                    year = [num for num in year if num]
                    c = [y for y in year if y-self.coverdate<=3]
                    self.next = sum(Counter(c).values())
            if 'authors' in data.columns:
                author_list = data.loc[index,'authors']
                id_list = list()
                for data in author_list:
                  id_list.append(data['authorId'])
                author_id_list = id_list
                self.auth = author_id_list


            row = {'doi': self.doi, 'title': self.title, 'citationVelocity': self.velocity,
                   'influentialCitationCount': self.incite,'openaccessFlag': self.openaccess,
                   'references-count': self.refcount, 'influentialReferencesCount': self.inref,
                   'reference_background': self.refback, 'reference_result': self.refresult,
                   'reference_methodology': self.refmeth, 'citations_background': self.cback,
                   'citations_result': self.cresult, 'citations_methodology': self.cmeth,
                   "citation_next": self.next, "normalized_citations": self.normalized,
                   "upstream_influential_methodology_count": self.upstream_influential_methodology_count, "authors":self.auth,"citations":self.citations,"age":self.age,"abstract":self.ab}

            return row
        except Exception as e:
            print(traceback.format_exc())
            row = {"upstream_influential_methodology_count": self.upstream_influential_methodology_count, "normalized_citations":self.normalized, 'doi': self.doi, 'title':self.title, 'citationVelocity':self.velocity, 'influentialCitationCount':self.incite,'is_open_access':self.openaccess,'references_count':self.refcount,'influentialReferencesCount':self.inref,'reference_background':self.refback,'reference_result':self.refresult,'reference_methodology':self.refmeth,'citations_background':self.cback,'citations_result':self.cresult,'citations_methodology':self.cmeth}
            return row