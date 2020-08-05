import re
import spacy
from spacy.lang.en import English


# ***** pdf to text conversion using pdf box ***********************-o-o-o-o-o-o-o-o-o-o-o-*****************
nlp = spacy.load("en_core_web_sm")

path_text = r"C:\Users\arjun\dev\text_files\publishPre\100.txt"
text = open(path_text, "r", encoding="utf8")
text1 = text.read()

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = English()

# Create the pipeline 'sentencizer' component
sbd = nlp.create_pipe('sentencizer')

# Add the component to the pipeline
nlp.add_pipe(sbd)

#  "nlp" Object is used to create documents with linguistic annotations.
doc = nlp(text1)
filtered_sent = []
# create list of sentence tokens
for word in doc:
    if word.is_stop == False:
        filtered_sent.append(word)

sentences = []
for sent in doc.sents:
    sentences.append(sent.text)

p_val_list = []
sample_list = []

for i in range(0, len(sentences) - 1):

    # ********REGEX FOR PA FORMATTED DISTRIBUTIONS******************

    # expression for t distribution vs p value
    pattern_t_list = re.finditer(
        "t\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
        sentences[i])

    # expression for f distribution vs p value
    pattern_f_list = re.finditer(
        "F\\s?\\(\\s?\\d*\\.?(I|l|\\d+)\\s?,\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|([Pp]\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
        sentences[i])

    # expression for correlation r vs p value
    pattern_cor_list = re.finditer(
        "r\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
        sentences[i])

    # expression for z distribution
    pattern_z_list = re.finditer(
        "[^a-z]z\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
        sentences[i])

    # expression for chi square distribution vs p value
    pattern_chi_list = re.finditer(
        "((\\[CHI\\]|\\[DELTA\\]G)\\s?|(\\s[^trFzQWBn ]\\s?)|([^trFzQWBn ]2\\s?))2?\\(\\s?\\d*\\.?\\d+\\s?(,\\s?N\\s?\\=\\s?\\d*\\,?\\d*\\,?\\d+\\s?)?\\)\\s?[<>=]\\s?\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=]\\s?\\d?\\.\\d+e?-?\\d*))",
        sentences[i])

    # expression for q distribution vs p value
    pattern_q_list = re.finditer(
        "Q\\s?-?\\s?(w|within|b|between)?\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*,?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=]\\s?\\d?\\.\\d+e?-?\\d*))",
        sentences[i])

    # expression for beta distribution vs p value

    # expression for b value - p value distribution
    pattern_b_list = re.finditer(
        "b\\s?\\(\\s?\\d*\\.?\\d+\\s?\\)\\s?[<>=]\\s?[^a-z\\d]{0,3}\\s?\\d*\\.?\\d+\\s?,\\s?(([^a-z]ns)|(p\\s?[<>=-]\\s?\\d?\\.\\d+e?-?\\d*))",
        sentences[i])

    # *****************REGEX FOR P VALUE EXPRESSION FROM DISTRIBUTION**************
    # expression for p value expression
    pattern_p = re.search("p\\s?[<>=]\\s?\\d?\\.\\d+e?-?\\d*", sentences[i])

    # --------------------------------------T-DISTRIBUTION---------------------------------------------

    for pattern_t in pattern_t_list:
        if pattern_t:
            expression = pattern_t.group()
            reported_pval_exp = pattern_p.group()
            p_val_list.append(reported_pval_exp)
            sentence = pattern_t.string
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

    # --------------------------------------------------F-DISTRIBUTION--------------------------------

    for pattern_f in pattern_f_list:
        if pattern_f:
            expression = pattern_f.group()
            reported_pval_exp = pattern_p.group()
            p_val_list.append(reported_pval_exp)
            sentence = pattern_f.string
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
            reported_pval_exp = pattern_p.group()
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

    # ----------------------------------- b value in distribution ------------------------------------------------

    for pattern_b in pattern_b_list:
        if pattern_b:
            expression = pattern_b.group()
            reported_pval_exp = pattern_p.group()
            p_val_list.append(reported_pval_exp)
            s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
            if len(s) == 3:
                df2 = 'NULL'
                df1 = s[0]
            else:
                df2 = s[1]
                df1 = s[0]

    # ---------------------------------------------- Z-DISTRIBUTION ----------------------------------------------

    for pattern_z in pattern_z_list:
        if pattern_z:
            expression = pattern_z.group()
            reported_pval_exp = pattern_p.group()
            p_val_list.append(reported_pval_exp)
            sentence = pattern_z.string
            distribution = "z"
            s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
            if len(s) == 2:
                df2 = 'NULL'
                df1 = 'NULL'

    # ------------------------------------ CHI SQUARE DISTRIBUTION---------------------------------------------

    for pattern_chi in pattern_chi_list:
        if pattern_chi:
            expression = pattern_chi.group()
            reported_pval_exp = pattern_p.group()
            p_val_list.append(reported_pval_exp)
            s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
            if len(s) == 4:
                sample_chi = 'NULL'
                df1 = s[1]
            else:
                sample_chi = s[2]
                df1 = s[1]
                chi_value = s[3]
                sample_list.append(sample_chi)

    # --------------------------------------------------- Q-DISTRIBUTION ---------------------------------------------

    for pattern_q in pattern_q_list:
        if pattern_q:
            expression = pattern_q.group()
            reported_pval_exp = pattern_p.group()
            p_val_list.append(reported_pval_exp)
            claim = sentences[i]
            sentence = pattern_q.string
            distribution = "q"
            s = [float(s) for s in re.findall(r'-?\d+\.?\d*', expression)]
            if len(s) == 3:
                df2 = 'NULL'
                df1 = s[0]
            else:
                df2 = s[1]
                df1 = s[0]

p_val_num_list = [float(string.split()[2]) for string in p_val_list]
print("vector of p-value numbers:", p_val_num_list)

print("Number of hypothesis tested:", len(p_val_list))
print("Real p-value:", min(p_val_num_list))

number_significant = 0
for string in p_val_list:
    if string.split()[1] == '<' or string.split()[1] == '=':
        if float(string.split()[2]) <= 0.05:
            number_significant += 1
print("Number Significant:", number_significant)


print("vector of p-values", p_val_list)
print("vector of sample sizes", max(sample_list))
print("number of test cases", len(p_val_list))
print("Range of p-values", max(p_val_num_list)-min(p_val_num_list))
print("Real p-value sign", p_val_list[p_val_num_list.index(min(p_val_num_list))].split()[1])

# Set default val (0)