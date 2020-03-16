# Author: Arjun Menon <amm8987@psu.edu>

"""
This script contains the definition for a token based
similarity scores for a pair of text sentences
"""


from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from collections import Counter
import numpy as np


class TokenStringSimilarity:
    # Class object
    stemmer = SnowballStemmer("english", ignore_stopwords=True)

    def __init__(self, text1, text2):
        self.text1 = text1.strip()
        self.text2 = text2.strip()

    def cosine(self):
        # Tokenize both sentences
        tokens1 = word_tokenize(self.text1)
        tokens2 = word_tokenize(self.text2)
        # Stemming using Porter2 AKA Snowball Stemmer
        stemmed_token1 = [self.stemmer.stem(token) for token in tokens1]
        stemmed_token2 = [self.stemmer.stem(token) for token in tokens2]
        # Create dict with term frequency for each set of tokens
        count_tokens1 = Counter(stemmed_token1)
        count_tokens2 = Counter(stemmed_token2)

        if not count_tokens1 or count_tokens2:
            return 0

        # Inner Product
        inner_product = 0
        if len(count_tokens1) < len(count_tokens2):
            for token, norm_term_freq in count_tokens1.items():
                if token in count_tokens2:
                    inner_product += norm_term_freq*count_tokens2[token]
        else:
            for token, norm_term_freq in count_tokens2.items():
                if token in count_tokens1:
                    inner_product += norm_term_freq*count_tokens1[token]
        magnitude1 = np.sqrt(np.sum(np.array(list(count_tokens1.values()))**2))
        magnitude2 = np.sqrt(np.sum(np.array(list(count_tokens2.values()))**2))
        return round((inner_product/(magnitude1*magnitude2)), 4)

    def jaccard(self):
        tokens1 = word_tokenize(self.text1)
        tokens2 = word_tokenize(self.text2)
        # Stemming using Porter2 AKA Snowball Stemmer
        stemmed_token1 = [self.stemmer.stem(token) for token in tokens1]
        stemmed_token2 = [self.stemmer.stem(token) for token in tokens2]
        # Cast to set
        set1 = set(stemmed_token1)
        set2 = set(stemmed_token2)

        if not set1 or not set2:
            return 0

        return round(float(len(set1 & set2)) / float(len(set1 | set2)), 4)
