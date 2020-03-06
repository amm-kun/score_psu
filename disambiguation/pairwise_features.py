from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from collections import Counter
import numpy as np
# import nltk

# nltk.download('punkt')
# nltk.download('stopwords')


class PairwiseFeatures:
    # Class variable
    stemmer = SnowballStemmer("english", ignore_stopwords=True)

    def __init__(self, text1, text2):
        self.text1 = text1
        self.text2 = text2
        self.cos_sim_score = 0

    def sentence_similarity(self):
        # Tokenize both sentences
        tokens1 = word_tokenize(self.text1)
        tokens2 = word_tokenize(self.text2)
        # Stemming using Porter2 AKA Snowball Stemmer
        stemmed_token1 = [self.stemmer.stem(token) for token in tokens1]
        stemmed_token2 = [self.stemmer.stem(token) for token in tokens2]
        # Create dict with term frequency for each set of tokens
        count_tokens1 = Counter(stemmed_token1)
        count_tokens2 = Counter(stemmed_token2)
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
        self.cos_sim_score = inner_product/(magnitude1*magnitude2)
