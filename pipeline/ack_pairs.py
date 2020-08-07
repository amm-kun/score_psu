from xml.dom.minidom import parse
import re
# import en_core_web_sm
import stanza
import requests
from time import sleep
import XIN
import string

nlp = stanza.Pipeline(lang='en', processors='tokenize,ner')


# nlp2 = stanza.Pipeline('en')

def grobid(pdfname):  # input PDFfilename output XMLfilename
    url = 'http://localhost:8070/api/processFulltextDocument'
    params = dict(input=open(pdfname, 'rb'))
    tei = requests.post(url, files=params, timeout=300)
    teiname = r'%s.tei' % (pdfname)
    fh = open(teiname, 'w', encoding='utf-8')
    fh.write(tei.text)
    fh.close()
    return teiname


# def pdf2txt(pdfname):


def authorName_complete(pfname):  # generate all possible author name format
    def allChildren(node):
        content = ''
        nodelist = node.childNodes
        for node in nodelist:
            if node.nodeType != node.TEXT_NODE:
                content = content + allChildren(node)
            else:
                nodedata = node.data
                content = content + nodedata
        return content

    authorname = []

    doc = parse(pfname)
    header = doc.getElementsByTagName('teiHeader')
    for h in header:
        author = h.getElementsByTagName('author')
        for a in author:
            persrname = a.getElementsByTagName('persName')
            for n in persrname:
                name0 = allChildren(n)
                name1 = re.findall('[A-Z][^A-Z]*', name0)
                name2 = ''
                name3 = ''
                name4 = ''
                name5 = ''
                name6 = ''
                name7 = ''
                for m in name1:
                    name2 += m
                    name2 += ' '
                temp = name2.split()
                if len(temp) == 2:
                    name7 = temp[0][0] + '. ' + temp[1]
                if len(temp) == 3:
                    name3 = temp[0] + ' ' + temp[2]
                    name4 = temp[0] + ' ' + temp[1] + '. ' + temp[2]
                    name5 = temp[0][0] + '. ' + temp[1] + '. ' + temp[2]
                    name6 = temp[0][0] + '.' + temp[1] + '. ' + temp[2]

                authorname.append(name2.strip())
                authorname.append(name3.strip())
                authorname.append(name4.strip())
                authorname.append(name5.strip())
                authorname.append(name6.strip())
                authorname.append(name7.strip())

    authorname = list(dict.fromkeys(authorname))
    return (authorname)


def authorName(pfname):
    def allChildren(node):
        content = ''
        nodelist = node.childNodes
        for node in nodelist:
            if node.nodeType != node.TEXT_NODE:
                content = content + allChildren(node)
            else:
                nodedata = node.data
                content = content + nodedata
        return content

    authorname = []

    doc = parse(pfname)
    header = doc.getElementsByTagName('teiHeader')
    for h in header:
        author = h.getElementsByTagName('author')
        for a in author:
            persrname = a.getElementsByTagName('persName')
            for n in persrname:
                name0 = allChildren(n)
                name1 = re.findall('[A-Z][^A-Z]*', name0)
                name2 = ''
                for m in name1:
                    name2 += m
                    name2 += ' '

                authorname.append(name2.strip())

    authorname = list(dict.fromkeys(authorname))
    return (authorname)


def XML2ack(pfname):  # extract acknowledgement section from XML(.tei) file
    pattern1 = re.compile('acknowledg|funding|beneﬁt|grant', re.IGNORECASE)
    pattern2 = re.compile('thank[s]? |grateful|gratitude|funded|acknowledg|funding',
                          re.IGNORECASE)  # not recommend 'fund','acknowledgement'and'benifit'

    temp_list = []
    text = ''
    textout = ''

    def allChildren(node):
        content = ''
        nodelist = node.childNodes
        for node in nodelist:
            if node.nodeType != node.TEXT_NODE:
                content = content + allChildren(node)
            else:
                nodedata = node.data
                content = content + nodedata
        return content

    try:
        doc = parse(pfname)

        divs = doc.getElementsByTagName('div')

        # for div2 in divs:

        for div in divs:
            heads = div.getElementsByTagName('head')

            if len(heads) != 0:

                for head in heads:
                    title = allChildren(head)

                    if pattern1.search(title):

                        ps = div.getElementsByTagName('p')
                        for p in ps:
                            pdata = allChildren(p)

                            textout = textout + pdata + '\n'


                    else:
                        ps2 = div.getElementsByTagName('p')
                        for p2 in ps2:
                            pdata2 = allChildren(p2)
                            if pattern2.search(pdata2):
                                textout = textout + pdata2 + '\n'

            else:

                whole = allChildren(div)
                if pattern2.search(whole):
                    textout = textout + whole + '\n'

            div22 = div.getElementsByTagName('div')
            if len(div22) != 0:
                for div2 in div22:
                    heads = div2.getElementsByTagName('head')

                    if len(heads) != 0:

                        for head in heads:
                            title = allChildren(head)

                            if pattern1.search(title):

                                ps = div2.getElementsByTagName('p')
                                for p in ps:
                                    pdata = allChildren(p)

                                    textout = textout + pdata + '\n'

                            else:
                                ps2 = div2.getElementsByTagName('p')
                                for p2 in ps2:
                                    pdata2 = allChildren(p2)
                                    if pattern2.search(pdata2):
                                        textout = textout + pdata2 + '\n'

        notes = doc.getElementsByTagName('note')
        for note in notes:
            notedata = allChildren(note)
            if pattern2.search(notedata):
                # print(notedata)
                textout = textout + notedata + '\n'

        figures = doc.getElementsByTagName('figure')
        for figure in figures:
            figuredata = allChildren(figure)
            if pattern2.search(figuredata):
                # print(notedata)
                textout = textout + figuredata + '\n'

    except Exception as e:
        print('')

    # print(text,textout)
    text = filter1(tokenize(text))
    textout = filter1(tokenize(textout))
    # print(text,textout)
    textsum = text + textout

    textsum = list(dict.fromkeys(textsum))
    return textsum


def tokenize(text):  # tokenizer
    textnlp = nlp(text)
    return [sentence.text for sentence in textnlp.sentences]


def NER(sentencelist):  # extract all entities
    return XIN.NERs(sentencelist)


def perNER(sentencelist):  # extract person entities

    PER = []
    Pres = []
    for t in NER(sentencelist):
        if t[1] == 'PERSON':
            PER.append(t)

    PER = list(dict.fromkeys(PER))
    for p in PER:  # names to be acknowledged must be full name
        if p[0].find(' ') != -1 or p[0].find('.') != -1:
            Pres.append(p)

    return Pres


def orgNER(sentencelist):  # extract org entities

    ORG = []

    for t in NER(sentencelist):
        if t[1] == 'ORG':
            ORG.append(t)
    ORG = list(dict.fromkeys(ORG))

    for x, i in enumerate(ORG):
        if 'Grant' == i[-1]:
            ORG[x] = i.split('Grant')[0].strip()
        ORG[x] = (ORG[x], 'ORG')
    return ORG


def perCounter(list1, list2):
    m = 0
    for a in list1:
        a = a.rstrip()
        for b in list2:
            b = b.rstrip()
            if a == b:
                print(a, '&&&', b)
                m += 1
    try:
        recall = m / len(list1)
        print('recall = ', recall * 100, '%')
    except:
        recall = None

    try:
        precision = m / len(list2)
        print('precision = ', precision * 100, '%')
    except:
        precision = None

    try:
        F1 = (2 * recall * precision) / (recall + precision)
        print("F1 =", F1)
    except:
        F1 = None

    return recall, precision, F1, m, len(list1), len(list2)


def orgCounter_strict(list1, list2):  # list1:ground truth, list2:extraction

    # strict evaluation
    count_correct_ext = 0  # correct of extraction(list2)
    count_correct_GT = 0  # correct of ground truth(list1)
    for a in list1:  # recall
        t = False
        a = a.strip()
        for b in list2:
            b = b.strip()
            if a == b:
                # print(a,'&&&',b)

                t = True
        if t == True:
            count_correct_GT += 1

    for b in list2:  # precision
        t = False
        b = b.strip()
        for a in list1:
            a = a.strip()
            if a == b:
                # print(b,'&&&',a)

                t = True
        if t == True:
            count_correct_ext += 1
    try:
        recall0 = count_correct_GT / len(list1)
        print('recall = ', recall0 * 100, '%')
    except:
        recall0 = None

    try:
        precision0 = count_correct_ext / len(list2)  # strict
        print('precision = ', precision0 * 100, '%')
    except:
        precision0 = None

    try:
        F10 = (2 * recall0 * precision0) / (recall0 + precision0)
        print("F1 =", F10)
    except:
        F10 = None
    return recall0, precision0, F10, count_correct_GT, len(list1), count_correct_ext, len(list2)


# return can be optimised
def orgCounter_loose(list1, list2):
    # loose evaluation
    count_correct_GT = 0
    count_correct_ext = 0
    for a in list1:
        t = False
        a = a.strip()
        for b in list2:
            b = b.strip()
            if a.find(b) != -1 or b.find(a) != -1:
                # print(a,'&&&',b)
                t = True

        if t == True:
            count_correct_GT += 1

    for b in list2:
        t = False
        b = b.strip()

        for a in list1:
            a = a.strip()
            if a.find(b) != -1 or b.find(a) != -1:
                # print(a,'&&&',b)
                t = True

        if t == True:
            count_correct_ext += 1

    try:
        recall0 = count_correct_GT / len(list1)
        print('recall = ', recall0 * 100, '%')
    except:
        recall0 = None

    try:
        precision0 = count_correct_ext / len(list2)  # loose
        print('precision = ', precision0 * 100, '%')
    except:
        precision0 = None

    try:
        F10 = (2 * recall0 * precision0) / (recall0 + precision0)
        print("F1 =", F10)
    except:
        F10 = None
    return recall0, precision0, F10, count_correct_GT, len(list1), count_correct_ext, len(list2)


def filter1(sentencelist):  # sentence filter inside acknowledgement
    pattern3 = re.compile(
        '(funding|grant)(.{0,20}) (:|support|came|assistance|was provided by)|(support(.{0,20})with|supported (in part )?by|support (from|of)|financed by|support(.{0,30})provided by|provided support|acknowledg)(.{0,120})(grant|scholarship|office|university|Council|assistance|constructive|fellowship|center|Foundation|Institut|fund|financial)|(work|paper|study) was supported in part by|(helpful|useful) (comments|feedback|suggest)|provide(d|s)?(.{0,25}) (fund|feedback|comment)|benefit(ed|s)?(.{0,15})from (.{0,60})(contribution|comment|insight)',
        re.IGNORECASE)
    pattern4 = re.compile(
        'thank(?! you!)|appreciate|grateful (to|for)|gratitude to|like[s]? to acknowledge|indebted to|funded (by|in|through)|funds were provided by|(center|Foundation|Institut|university)(.{0,20})(provided(.{0,20})support|funded this)|financial(ly)? support',
        re.IGNORECASE)

    text2 = []

    # for x,r in enumerate(sentencelist):

    # if pattern3.search(r):
    # text2.append(r)
    # if ':' in r[-2:]:   # in case tokenize at ':'
    # try:
    # text2.append(sentencelist[x+1])
    # except:
    # pass

    for i in range(len(sentencelist)):
        if pattern3.search(sentencelist[i]) or pattern4.search(sentencelist[i]):
            text2.append(sentencelist[i])
        elif i != 0:  # we thank: A, B, and C, stanza will segment at ':'
            if ':' in sentencelist[i - 1][-2:]:
                text2.append(sentencelist[i])

    return text2

# print(perNER(XML2ack(r'C:\Users\arjun\dev\GROBID_processed\PublishPre\45.tei.xml')))
# print(NER(XML2ack(r'C:\Users\arjun\dev\GROBID_processed\PublishPre\45.tei.xml')))