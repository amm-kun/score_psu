import re
import spacy
import os
from spacy.lang.en import English
from utilities import p_val_sign

nlp = spacy.load("en_core_web_sm")
# Load English tokenizer, tagger, parser, NER and word vectors
nlp = English()

# Create the pipeline 'sentencizer' component
sbd = nlp.create_pipe('sentencizer')

# Add the component to the pipeline
nlp.add_pipe(sbd)

# Max length for input (Memory bottleneck)
nlp.max_length = 6000000


def get_p_val_darpa_tsv(claim):
    
    # [p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?[-|–]?\\d*
    
    pattern_p = re.search("[p|P]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))", claim)
    if pattern_p:
        return pattern_p.group()
    else:
        return None


def extract_p_values(file, tsv_claim=None):
    p_val_list = []
    sample_list = []
    real_sample_list = []
    filtered_sent = []
    sentences = []
    just_pvalues_list = []
    just_pvalues_range = []
    max_sample_size = 0
    range_p_values = 0
    real_p_sign = 0
    num_hypo_test = 0
    real_p_value = 1
    number_significant = 0
    extended_p_val = 0

    try:
        # text = open(file, "r", encoding="utf8")
        text = open(file, "r")
        text1 = text.read()
    except FileNotFoundError:
        print("******---------- File not found: ", file, "----------******")
        return {"num_hypo_tested": num_hypo_test, "real_p": real_p_value, "real_p_sign": real_p_sign,
                "p_val_range": range_p_values, "num_significant": number_significant, "sample_size": max_sample_size,
                "extend_p": extended_p_val}
    except UnicodeDecodeError:
        try:
            text = open(file, "r", encoding="utf-8")
            text1 = text.read()
        except UnicodeDecodeError:
            print("*********---------- Encoding error: ", file, "*********----------")
            return {"num_hypo_tested": num_hypo_test, "real_p": real_p_value, "real_p_sign": real_p_sign,
                    "p_val_range": range_p_values, "num_significant": number_significant,
                    "sample_size": max_sample_size, "extend_p": extended_p_val}

    #  "nlp" Object is used to create documents with linguistic annotations.
    doc = nlp(text1)
    # create list of sentence tokens
    for word in doc:
        if not word.is_stop:
            filtered_sent.append(word)

    for sent in doc.sents:
        sentences.append(sent.text)

    for i in range(0, len(sentences) - 1):

        #********REGEX FOR PA FORMATTED DISTRIBUTIONS******************

        #expression for t distribution vs p value
        pattern_t_list = re.finditer("t\\s?(\[|\()\\s?\\d*\\.?\\d+\\s?(\]|\))\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*[,;]?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])
        pattern_t_nodf_list = re.finditer("t\\s?([<>=]|\\s?)\\s?[^a-z\\d]{0,3}\\s?\\d*[,;]?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))", sentences[i])

        #expression for f distribution vs p value
        pattern_f_list = re.finditer("(F|F-change)\\s?(\[|\()\\s?\\d*\\.?(I|l|\\d+)\\s?,\\s?\\d*\\.?\\d+\\s?(\]|\))\\s?[<>=]\\s?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])
        # pattern_f_list = re.finditer("F\s*(\[|\()\s*\d*\.*(I|l|\d+)\s*,\s*\d*\.*\d+\s*(\]|\))\s*[<>=]\s*\d*\.?\d+\s*[,;]\s*(([^a-z]ns)|([p|P]\s*[<>=-]\s*\d*\.\d+e*-*\d*))", sentences[i])
        
        #expression for correlation r vs p value
        pattern_cor_list = re.finditer("r\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,5}\\s?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])
        pattern_cor_no_df_list = re.finditer("(r|rpb|R)\s*\s*[<>=]\s*[^a-z\d*]{0,5}\s*\d*\.?\d+\s*[,;]\s*(([^a-z]ns)|([p|P]\s*[<>=-]\s*\d*\.\d+e?(-|–)?\d*))", sentences[i])

        # expression for z distribution
        pattern_z_list = re.finditer("[^a-z]z\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])

        #expression for chi square distribution vs p value
        pattern_chi_list = re.finditer("((\\[CHI\\]|\\[DELTA\\]G)\\s?|(\\s[^trFzQWBn ]\\s?)|([^trFzQWBn ]2\\s?))2?\\(\\s?\\d*\\.?\\d+\\s?(,\\s?N\\s?\\=\\s?\\d*\\,?\\d*\\,?\\d+\\s?)?\\)\\s?[<>=]\\s?\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|([p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])

        #expression for q distribution vs p value
        pattern_q_list = re.finditer("Q\\s?-?\\s?(w|within|b|between)?\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|([p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?(-|–)?\\d*))", sentences[i])

        #expression for logistic regression distribution vs p value
        pattern_logreg_list = re.finditer("[OR|or|oR|Or]\\s?\\s?[<>=]\\s?[^a-z\\d]{0,5}\\s?\\d*\\.?\\d+\\s?[,;]\\s?(([^a-z]ns)|([p|P]\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))", sentences[i])


        pattern_HR_list = re.finditer("HR[\s*|=]\d*\.*\d*,\s*(.*,(.*[p|P]\s*[<>=]\s*\d*\.\d+e?[-|–]*\d*))", sentences[i])

        # expression for b distribution (unstandardalized beta)
        pattern_b_list = re.finditer("b\s*[=><]\s*\d*\.*\d*\s*,\s*[p|P]\s*[<>=]\s*\d*\.\d+e*[-|–]*\d*", sentences[i])


        #*****************REGEX FOR P VALUE EXPRESSION FROM DISTRIBUTION*****************************
    
        pattern_p = re.search( "[p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?[-|–]?\\d*", sentences[i])

        # #*****************Expression for sample size in 'n' form**********************
        # pattern_sample = re.finditer("(N|n)\s*=\s*\d*", sentences[i])

        # #**********append sample sizes to list********************
        # for sample in pattern_sample:
        #     if sample:
        #         samplesize = sample.group()
        #         real_sample_list.append(samplesize)


        # --------------------------------------T-DISTRIBUTION---------------------------------------------

        for pattern_t in pattern_t_list:
            if pattern_t:
                expression = pattern_t.group()
                # print(expression)
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = 'NULL'
                    df1 = s[0]
                    sample_t = df1 + 1
                    sample_list.append(sample_t)

                else:
                    df2 = s[1]
                    df1 = s[0]
                    sample_t = df1 + 1
                    sample_list.append(sample_t)

        for pattern_t_nodf in pattern_t_nodf_list:
            if pattern_t_nodf:
                expression = pattern_t_nodf.group()
                print(expression)
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                # print(pattern_pval)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                   

        # --------------------------------------------------F-DISTRIBUTION--------------------------------

        for pattern_f in pattern_f_list:
            if pattern_f:
                expression = pattern_f.group()
                # print(expression)
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = s[1]
                    df1 = s[0]
                    constant = df1 + 1
                    sample_f = constant + df2
                    sample_list.append(sample_f)

                else:
                    df2 = s[1]
                    df1 = s[0]
                    constant = df1 + 1
                    sample_f = constant + df2
                    sample_list.append(sample_f)

        # ------------------------------------------- CORRELATION ----------------------------------------------------

        for pattern_cor in pattern_cor_list:
            if pattern_cor:
                expression = pattern_cor.group()
                # print(expression)
                # print(sentences[i])
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 3:
                    df2 = 'NULL'
                    df1 = s[0]
                    sample_cor = df1 + 2
                    sample_list.append(sample_cor)

                
                else:
                    df2 = s[1]
                    df1 = s[0]
                    sample_cor = df1 + 2
                    sample_list.append(sample_cor)

        for pattern_cor_ndf in pattern_cor_no_df_list:
            if pattern_cor_ndf:
                expression = pattern_cor_ndf.group()
                # print(expression)
                # print(sentences[i])
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                

    #***********************************************logistic (OR MEANS ODDS RATIO) regression*************************
        for pattern_logreg in pattern_logreg_list:
            if pattern_logreg:
                expression = pattern_logreg.group()
                # print(expression)
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                if pattern_pval:
                    reported_pval_exp = pattern_pval.group()
                    p_val_list.append(reported_pval_exp)
                
        #********************* HR (hazard ratio) statistics *******************************************
        for pattern_hr in pattern_HR_list:
            if pattern_hr:
                expression = pattern_hr.group()
                # print(expression)
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)

        # ----------------------------------- b value in distribution ------------------------------------------------

        for pattern_b in pattern_b_list:
            if pattern_b:
                expression = pattern_b.group()
                # print(expression)
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
               

        # ---------------------------------------------- Z-DISTRIBUTION ----------------------------------------------

        for pattern_z in pattern_z_list:
            if pattern_z:
                expression = pattern_z.group()
                # print(expression)
                # [p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?[-|–]?\\d*
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
               

        # ------------------------------------ CHI SQUARE DISTRIBUTION---------------------------------------------

        for pattern_chi in pattern_chi_list:
            if pattern_chi:
                expression = pattern_chi.group()
                # print(expression)
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
                s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
                if len(s) == 4:
                    sample_chi = 'NULL'
                    # df1 = s[1]
                else:
                    sample_chi = s[2]
                    # df1 = s[1]
                    # chi_value = s[3]
                    sample_list.append(sample_chi)

        # --------------------------------------------------- Q-DISTRIBUTION ---------------------------------------------

        for pattern_q in pattern_q_list:
            if pattern_q:
                expression = pattern_q.group()
                # print(expression)
                pattern_pval = re.search( "[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", expression)
                reported_pval_exp = pattern_pval.group()
                p_val_list.append(reported_pval_exp)
               
        
    

        #_______________________________________________________________________________________________________________________

    # print("P-vals list is:", p_val_list)
    if len(p_val_list) == 0:
        extended_p_val = 1
        for i in range(0, len(sentences) - 1):

            # ---------------------------REGEX FOR P VALUE EXP from sentences ----------------------------
           
           #old p val exp : [p|P]\\s?[<>=]\\s?\\d?\\.\\d+e?[-–]?\\d*
            pattern_p_list = re.finditer("[p|P|Ps|ps]\s*[<>=]\s*\d*\.\d+(e[-–]\d*)?(?!.*(-|–))(?!.*e)", sentences[i])
            pattern_p_range_list = re.finditer("(p|P)\s*[=<>]\s*\d*.\d*(-|–)\s*\d*.\d*", sentences[i])


            
            # append just pvalues to a list names 'just_pvalues_list'
            for pattern_p in pattern_p_list:
                if pattern_p:
                    reported_pval = pattern_p.group()
                    just_pvalues_list.append(reported_pval)
                    

            # append just pvalues in the form of range to a list names 'just_pvalues_range'
            for pattern_p_range in pattern_p_range_list:
                if pattern_p_range:
                    reported_pval_range = pattern_p_range.group()
                    just_pvalues_range.append(reported_pval_range)

        # print("statistical p-values not found, all p-values of pdf", just_pvalues_list)
        p_val_list = just_pvalues_list
        # print(p_val_list)
        # print(just_pvalues_range)
        # print(just_pvalues_list)
    
    if len(p_val_list) == 0 and tsv_claim:
        from_claim = get_p_val_darpa_tsv(tsv_claim)
        
        if from_claim:
            p_val_list.append(get_p_val_darpa_tsv(tsv_claim))
    # print(p_val_list)
    # try:
        # p_val_num_list = [float(string.split()[2]) for string in p_val_list]
    p_val_num_list = []
    for string in p_val_list:
        
        try:
            # print(string)
            p_val_num_list.append(float(string.split()[2]))
        except ValueError:
            string = string.replace('–', '-')
            try:
                p_val_num_list.append(float(string.split()[2]))
            except ValueError:
                p_val_num_list.append(float((re.split('[<>=]', string))[-1]))
        except AttributeError:
            pass
        except IndexError:
            p_val_num_list.append(float((re.split('[<>=]', string))[-1]))
            # print("Index error in P-Val script")
            # p_val_num_list = []
    # print("vector of p-value numbers:", p_val_num_list)
    if len(p_val_list) > 0 and len(p_val_num_list) > 0:
        num_hypo_test = len(p_val_list)
        real_p_value = min(p_val_num_list)
        # print("Number of hypothesis tested:", num_hypo_test)
        # print("Real p-value:", real_p_value)

        number_significant = 0
        for string in p_val_list:
            try:
                if string.split()[1] == '<' or string.split()[1] == '=':
                    if float(string.split()[2]) <= 0.05:
                        number_significant += 1
            except ValueError:
                string = string.replace('–', '-')
                if float(string.split()[2]) <= 0.05 and (string.split()[1] == '<' or string.split()[1] == '='):
                    number_significant += 1
            except IndexError:
                if any(character in string for character in ['<', '=']):
                    if float((re.split('[<>=]', string))[-1]) <= 0.05:
                        number_significant += 1

        # print("Number Significant:", number_significant)

        # print("vector of p-values", p_val_list)
        if sample_list:
            # print("vector of sample sizes", max(sample_list))
            max_sample_size = max(sample_list)
            range_p_values = max(p_val_num_list) - min(p_val_num_list)
            try:
                real_p_sign = p_val_list[p_val_num_list.index(min(p_val_num_list))].split()[1]
                real_p_sign = p_val_sign[real_p_sign]
            except KeyError:
                real_p_sign = 0
            except IndexError:
                real_p_sign = p_val_sign[re.search('[<>=]', p_val_list[p_val_num_list.index(min(p_val_num_list))]).group()]

        # print("Max Sample size: ", max_sample_size)
        # print("Range of p-values: ", range_p_values)
        # print("Real p-value sign: ", real_p_sign)
    return {"num_hypo_tested": num_hypo_test, "real_p": real_p_value, "real_p_sign": real_p_sign,
            "p_val_range": range_p_values, "num_significant": number_significant, "sample_size": max_sample_size,
            "extend_p": extended_p_val}


# extract_p_values(r"C:\Users\arjun\dev\test\pdfs\Hongbo_covid_gy96y.txt")
# path_text = "C:\\Users\\lanka\\Downloads\\6713.txt"
d = "C:\\Users\\lanka\\Desktop\\Lab\\DARPA\\new_pval_code_for_pipeline_edited_statcheck\\train\\retractedErrorData"
filepaths_list = []
for path in os.listdir(d):
    full_path = os.path.join(d, path)
    if os.path.isfile(full_path):
        filepaths_list.append(full_path)

# print(len(filepaths_list))

for path_text in filepaths_list:
    print(path_text)
    print(extract_p_values(path_text))