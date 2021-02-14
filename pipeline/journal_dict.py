
# importing library 
import requests 
import pandas as pd
from fuzzywuzzy import fuzz
import os
os.chdir('D:/Grad/Work/Score/Elsevier/Journal dictonary/')

def serial_title(query):

        x = query.replace(' ','%20')
        url = 'https://api.elsevier.com/content/serial/title?title=' + str(x) + '&apiKey=7ee01b8a5bea998e4081b9a3ae9ce249'
        return url

def return_row(r,query):
            status = r.status_code

            #Checking the status code: success_code = 200. Otherwise, return empty row
            if status!=200:
                print('Error_status', status)
                empty = {'dc:title':query}
                empty= pd.DataFrame(empty, index = [0])
                return empty
            else:
                # Interpretating the Json response to give a dataframe
                data = r.json()
                search_results = data['serial-metadata-response']
                df = search_results['entry']
                search = pd.json_normalize(df)
                titles = search['dc:title']
                titles = titles.tolist()
                flag = 0
                #entry = pd.json_normalize(df[0])
                for i in range(0,len(titles)):
                    check = titles[i]
                    ratio = fuzz.ratio(query.lower(),check.lower())
                    if ratio==100:
                        flag = 0
                        entry = pd.json_normalize(df[i])
                        break
                    else:
                        flag=1
                if flag==1:
                        empty = {'dc:title':query}
                        empty= pd.DataFrame(empty, index = [0])
                        print('no title match')
                        return empty 

                # Selecting only necessary features
                columns = ['source-id','dc:title','SJRList.SJR','SNIPList.SNIP','citeScoreYearInfoList.citeScoreCurrentMetric','citeScoreYearInfoList.citeScoreTracker','subject-area' ]
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
                    if 'citeScoreYearInfoList.citeScoreCurrentMetric' in entry.columns:
                        new_columns.append('citeScoreYearInfoList.citeScoreCurrentMetric')
                    if 'citeScoreYearInfoList.citeScoreTracker' in entry.columns:
                        new_columns.append('citeScoreYearInfoList.citeScoreTracker')
                    if 'subject-area' in entry.columns:
                        new_columns.append('subject-area')
                    entry = pd.DataFrame(data = entry.loc[:,new_columns])
                row = entry
               
                # SJR and SNIP indicator json responses to columns
                if 'SJRList.SJR' in entry.columns:
                    SJR = entry['SJRList.SJR']
                    SJR = pd.json_normalize(SJR[0])
                    SJR = SJR.rename(columns={"$":"SJR"})
                    SJR = SJR.drop(["@_fa", "@year"],axis = 1)
                    row = row.drop('SJRList.SJR', axis = 1)
                    row = pd.concat([row, SJR],ignore_index=False, axis =1)
                if 'SNIPList.SNIP' in entry.columns:
                    SNIP = entry['SNIPList.SNIP']
                    SNIP = pd.json_normalize(SNIP[0])
                    SNIP = SNIP.rename(columns={"$":"SNIP"})
                    SNIP = SNIP.drop(["@_fa","@year"],axis = 1)
                    row = row.drop('SNIPList.SNIP', axis = 1)
                    row = pd.concat([row, SNIP],ignore_index=False, axis =1)
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

data = pd.read_csv('journals_list.txt', sep='\n', header=None)

journals = data.iloc[:,0]
journals = journals.tolist()

#Query is the title for Serial Title API

output2 = pd.DataFrame()
for i in range(0, len(journals)):
    query =journals[i]
    # api-endpoint: 
    URL = serial_title(query)
    # sending get request and saving the response as response object 
    r = requests.get(URL)
    response = return_row(r,query)
    output2 = output2.append(response, ignore_index=True)


output2.to_pickle('journal_dictionary.pkl')

#Coverting to pickle and reading it
journal_dict = pd.read_pickle('journal_dictionary.pkl')
print(journal_dict.head())