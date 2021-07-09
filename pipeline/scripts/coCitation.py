# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 11:56:24 2020
@author: weixi
"""

#cocitationAll is "append" dict
#output paperID
#only look at papers that cited the source paper 3 years after  (YearGap)

import requests
import json
import csv
import time
import numpy as np
import pickledb
from ratelimit import limits, sleep_and_retry
import pdb

#===============================================================================================
# Main part, Construct cocitation
#===============================================================================================

#===============================================================================================
# Rate Limit Enforcing
#===============================================================================================
@sleep_and_retry
@limits(calls=180, period=1)
def call_api(query):
    headers = {'x-api-key': 'I6SO5Ckndk67RitJNJOFR4d7jDiVpWOgaMFUhgkM'}
    url = 'https://partner.semanticscholar.org/v1/paper/' + query
    r = requests.get(url,headers=headers)
    if r.status_code != 200:
        print('API response: {}'.format(r.status_code))
        raise Exception('API response: {}'.format(r.status_code))
    return r.json()
        
def coCite(doi,db) :   
    cocitationsAll = {}
    YearGap = 3          # change this to control the publish time of papers that cited the source paper
    counter_sourceDOI = 0
    dt2={}
    dt3={}
    if db.cocite.get(doi,False):
        return db.cocite.get(doi,False)
    try:
        if isinstance(doi,str):
            dataapi = call_api(doi)
            #dataapi = r.json()   # a dictionary for the source paper

            citations = dataapi.get('citations')
            pubYear = dataapi.get('year')
            sourceid = dataapi.get('paperId')

            if citations is None or len(citations) == 0:  #sometimes 'citations' is empty
                counter_sourceDOI +=1
                return 0,0


            else:

                #references = dataapi.get('references')

                ciID = []
                dict = {}
                counter = 0
                counter_year = 0
                rm_sourceid = 0
                try:
                    for i in range(0, len(citations)):#check each paper in 'citations'
                        #time.sleep(1)
                        id = citations[i].get('paperId')
                        year_becited = citations[i].get('year')    # about year
                        if year_becited != None and year_becited-pubYear <= YearGap:       # Select the papers publishes less than or equal to 3 years after the original paper
                            ciID.append(id)
                            data_cite = call_api(id)
                            references_cite = data_cite.get('references')
                            if references_cite is None or len(references_cite) == 0:
                                counter +=1
                            else:
                                for j in range(0, len(references_cite)):

                                    id = references_cite[j].get('paperId')


                                    if id not in dict:
                                        dict[id] = 1
                                    else:
                                        dict[id] +=1

                            if sourceid in dict:           
                                del dict[sourceid]#remove the source paper
                            else:
                                rm_sourceid +=1

                        else:
                            counter_year+=1
                except Exception as e:
                    print(e)
                cnt3 = 0
                cnt3 = sum(1 for k,v in dict.items() if int(v)>=3)
                cnt2 = 0
                cnt2 = sum(1 for k,v in dict.items() if int(v)>=2)
                print("*****WRITING COCITE", doi, cnt2,cnt3)
                db.cocite[doi] = (cnt2,cnt3)
                return cnt2,cnt3
        else:
            return 0,0
    except Exception as e:
        print(str(e))
        return 0,0