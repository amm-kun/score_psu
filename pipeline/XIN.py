# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 17:04:38 2020
@author: weixi
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 00:06:09 2020
@author: weixi
"""

import string
import re
import stanza

nlp = stanza.Pipeline('en', use_gpu=False)


# text = open("ak01.txt",'r')
# contents=text.read()
# print(contents)
# def tokenize(contents):
#    textnlp = nlp(contents)
#    return [sentence.text for sentence in textnlp.sentences]

# print(tokenize(contents))
# sentencelist=tokenize(contents)

# sent=['The authors thank Ms. T. Inoue for her excellent technical assistance.','ational Business, Nanyang Business School, Nanyang Technological University.', 'The authors thank the Institute for the Study of Business Markets (ISBM) at Pennsylvania State Univer-sity for generously funding this research.', 'This research also benefited from the helpful comments of served as associate editor for this article.']
def NERs(sentencelist):
    # print('i love q')
    out = []
    out2 = []
    entlistall2 = []
    entlistall3 = []
    for x in range(0, len(sentencelist)):
        nn = sentencelist[x]

        nnn = nn

        counter1 = 0

        def subj_part(doc):
            for sentence in doc.sentences:
                for word in sentence.words:
                    if word.deprel == "root":
                        pre_text = word.text
            subj_part = nn.split(pre_text)[0]
            # print("subj_part:", subj_part)
            return subj_part

        def find_entity(sentencelist):
            subjpart = subj_part(doc=doc_semi)
            for x in range(0, len(m)):  # deals with each subsentence
                m[x] = m[x].rstrip()
                m[x] = m[x].rstrip(",")
                m[x] = m[x].rstrip(".")
                w = m[x] + "."
                # print("\n")
                # print("subsentence:", w)

                doc = nlp(w)
                # Look for subject and predicate
                entlist = []
                entlist2 = []
                entlist3 = []

                for sentence in doc.sentences:

                    #      for word in sentence.words:
                    #         if word.deprel == "root" and word.head == 0:
                    #            rootid = word.id

                    #    for word in sentence.words:
                    #       if word.deprel == "nsubj:pass" and word.head == int(rootid):
                    #          try:
                    #              pass_extraction(doc)
                    #          except:
                    #             counter1=counter1+1
                    #             print("counter1:", counter1)
                    #             continue

                    #     elif  word.deprel == "nsubj" and word.head == int(rootid):
                    #         try:
                    #             act_extraction(doc)
                    #         except:
                    #             counter1=counter1+1
                    #             print("counter1:", counter1)
                    #             continue

                    for x in range(0, len(sentence.ents)):
                        if bool(re.search(r'\d', sentence.ents[x].text)) == False and len(sentence.ents[x].text) > 2:
                            if sentence.ents[x].type == "PERSON" or sentence.ents[x].type == "ORG":
                                # if sentence.ents[x].type != "CARDINAL" and sentence.ents[x].type != "WORK_OF_ART" and sentence.ents[x].type != "GPE":
                                # print(sentence.ents[x].text, ":",  sentence.ents[x].type)
                                if sentence.ents[x].text[:3] == 'the':
                                    entlist.append(sentence.ents[x].text[4:])
                                    entlist2.append((sentence.ents[x].text[4:], sentence.ents[x].type))
                                else:
                                    entlist.append(sentence.ents[x].text)
                                    entlist2.append((sentence.ents[x].text, sentence.ents[x].type))

                                # print("entlist appended:", entlist)

                for x in range(0, len(entlist)):
                    if subjpart.find(entlist[x]) != -1:
                        entlist[x] = None
                        entlist2[x] = None

                # print("entlist:", entlist)
                while None in entlist:
                    entlist.remove(None)
                    entlist2.remove(None)
                    # print("entlist:", entlist)

                if entlist != []:
                    entlistall.append(entlist[0])
                    entlistall2.append(entlist2[0])

            # print("\n")
            # print("entlistall:", entlistall)

        # *************************************************************************
        # Print what is obtained by Stanza
        #
        # *************************************************************************
        # print("\n")
        doc = nlp(nn)
        # for sentence in doc.sentences:
        # for x in range(0, len(sentence.ents)):
        # print(sentence.ents[x].text, ":",  sentence.ents[x].type)

        # *************************************************************************
        # Organize and clear the original sentencelist sentence
        #
        # *************************************************************************

        nn = re.sub(u" Universiti", " University", nn)
        nn = re.sub(u" laboratory", " LAB", nn)
        nn = re.sub(u" lab", " LAB", nn)
        nn = re.sub(u"Prof. ", "", nn)
        nn = re.sub(u"Dr. ", "", nn)
        nn = re.sub(u"Drs.", "", nn)
        nn = re.sub(u"'s", "", nn)
        nn = re.sub(u" \\(.*?\\)|\\{.*?}|\\[.*?]", "", nn)  # the first one is a space

        # remove "and" by "&" in entity names
        # print("\n")
        for sentence in doc.sentences:
            for x in range(0, len(sentence.ents)):
                if sentence.ents[x].text.find(" and") != -1:
                    get_and = sentence.ents[x].text
                    # print("Entity with and:", get_and)
                    get_and_new = get_and.replace(' and', ' &')
                    # print("get_and_new:", get_and_new)
                    nn = nn.replace(get_and, get_and_new)

        # print("without and in entity:", nn)

        # *************************************************************************
        # Look for consecutive PERSON names (greater or equal to 3)
        # *************************************************************************

        entlist_name = []

        # ************************************************************************
        nn_semi = nn
        doc_semi = nlp(nn_semi)
        # print("\n")
        # print(*[f'id: {word.id}\tword: {word.text}\thead id: {word.head}\thead: {sent.words[word.head-1].text if word.head > 0 else "root"}\tdeprel: {word.deprel}\tupos: {word.upos}\txpos: {word.xpos}' for sent in doc.sentences for word in sent.words], sep='\n')

        # print("\n","OriginalSentence:", nnn,"\n")

        # ********************************************************************
        # Main part
        #
        # ********************************************************************

        if nn.find(" and") != -1:

            entlistall = []
            m = nn.split(" and")
            find_entity(sentencelist=nn)


        elif nn.find(" and") == -1:
            entlistall = []
            m = nn.split(" by")
            find_entity(sentencelist=nn)

        # ********************************************************************
        # Combine "entlist_name" and "entlistall"
        #
        # ********************************************************************
        entlist_name = []
        if entlist_name != []:
            for x in range(0, len(entlist_name)):
                entlist_name[x] = entlist_name[x].strip(string.punctuation)
                # print(entlist_name)

            for x in range(0, len(entlistall)):
                entlistall[x] = entlistall[x].strip(string.punctuation)
                # print(entlistall)

            for x in range(0, len(entlist_name)):
                if entlist_name[x] not in entlistall:  # entlistall is list, can't use ".find"
                    entlistall.append(entlist_name[x])

            # print("final result:", entlistall)

        for e in entlistall:
            for e2 in entlistall2:
                if e == e2[0]:
                    entlistall3.append(e2)
        # out = out + entlistall
    entlistall3 = list(dict.fromkeys(entlistall3))
    return entlistall3
# print(NERs(sent))