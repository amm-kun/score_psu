# Author: Arjun Menon <amm8987@psu.edu>

"""
This script contains the definition for a string based
similarity scores for a pair of strings
"""


from six.moves import xrange
import re


class StringSimilarity:
    def __init__(self, text1, text2):
        self.text1 = text1.strip()
        self.text2 = text2.strip()
        self.prefix_weight = 0.1

    def get_raw_jaro(self):
        len_s1 = len(self.text1)
        len_s2 = len(self.text2)

        max_len = max(len_s1, len_s2)
        search_range = (max_len // 2) - 1
        if search_range < 0:
            search_range = 0

        flags_s1 = [False] * len_s1
        flags_s2 = [False] * len_s2

        common_chars = 0
        for i, ch_s1 in enumerate(self.text1):
            low = i - search_range if i > search_range else 0
            high = i + search_range if i + search_range < len_s2 else len_s2 - 1
            for j in xrange(low, high + 1):
                if not flags_s2[j] and self.text2[j] == ch_s1:
                    flags_s1[i] = flags_s2[j] = True
                    common_chars += 1
                    break

        if not common_chars:
            return 0

        k = trans_count = 0
        for i, f_s1 in enumerate(flags_s1):
            if f_s1:
                for j in xrange(k, len_s2):
                    if flags_s2[j]:
                        k = j + 1
                        break
                if self.text1[i] != self.text2[j]:
                    trans_count += 1

        trans_count /= 2
        common_chars = float(common_chars)
        weight = ((common_chars / len_s1 + common_chars / len_s2 +
                   (common_chars - trans_count) / common_chars)) / 3
        return weight

    def jaro_winkler(self):
        # if one of the strings is empty return 0
        if not self.text1 or not self.text2:
            return 0

        jw_score = self.get_raw_jaro()
        min_len = min(len(self.text1), len(self.text2))

        # prefix length can be at max 4
        j = min(min_len, 4)
        i = 0
        while i < j and self.text1[i] == self.text2[i] and self.text1[i]:
            i += 1

        if i:
            jw_score += i * self.prefix_weight * (1 - jw_score)

        return jw_score

    def soundex(self):
        if not self.text1 or not self.text2:
            return 0

        if self.text1 == self.text2:
            return 1

        string1, string2 = self.text1.upper(), self.text2.upper()
        first_letter1, first_letter2 = string1[0], string2[0]
        string1, string2 = string1[1:], string2[1:]

        # remove occurrences of vowels, 'y', 'w' and 'h'
        string1 = re.sub('[AEIOUYWH]', '', string1)
        string2 = re.sub('[AEIOUYWH]', '', string2)

        # replace (B,F,P,V)->1 (C,G,J,K,Q,S,X,Z)->2 (D,T)->3 (L)->4
        # (M,N)->5 (R)->6
        string1 = re.sub('[BFPV]', '1', string1)
        string1 = re.sub('[CGJKQSXZ]', '2', string1)
        string1 = re.sub('[DT]', '3', string1)
        string1 = re.sub('[L]', '4', string1)
        string1 = re.sub('[MN]', '5', string1)
        string1 = re.sub('[R]', '6', string1)

        string2 = re.sub('[BFPV]', '1', string2)
        string2 = re.sub('[CGJKQSXZ]', '2', string2)
        string2 = re.sub('[DT]', '3', string2)
        string2 = re.sub('[L]', '4', string2)
        string2 = re.sub('[MN]', '5', string2)
        string2 = re.sub('[R]', '6', string2)

        string1 = first_letter1 + string1[:3]
        string2 = first_letter2 + string2[:3]

        return 1 if string1 == string2 else 0