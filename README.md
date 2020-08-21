# SCORE_PSU
## Repository for Python scripts pertaining to the DARPA SCORE project effort by PSU ##

### Disambiguation ###
#### Dependencies (tested) ####
| Package | Version |
| :-------: | :-------: |
| mysql-connector-python | 8.0.19  |
| nltk | 3.4.5 |
| numpy | 1.18.1 |

#### Feature Extraction script ####
This script queries the USPTO PatentsView database instance to retrieve inventor features for the disambiguation task 
writes to a CSV formatted file.

**Usage**:
```commandline
python inventor_feature_extraction.py -f <file> / --file <file>
```

#### Feature Generator ####
Generates postive and negative pairs (random) and computes their corresponding feature vectors by building inventor 
clusters (records of the same inventor belong to a single cluster)

**Usage**:
```commandline
python pair_feature_extraction.py -f <file> \ --file <file>
```

#### Pairwise Inventor Records Feature Extractor ####
This script creates a class object for a pair of inventors (namedtuples), and computes various similarity features
for the various fields relevant to an inventor record.  

Current feature function definitions that are available include:
1. Token based
    1. Cosine Similarity
    2. Jaccard Similarity
2. String based
    1. Soundex
    2. Jaro-Winkler Distance
3. Long|Lat distance
    1. Haversine distance
    
### ingest_WoS ###
#### Dependencies (tested) ####
| Package | Version |
| :-------: | :-------: |
| pymongo | 3.10.1  |


#### Running the script: ####
```
python xml_to_json.py -p <path-to-XML-dir> / --path <path-to-XML-dir>
```

If the path argument is not supplied, default behavior is to use the local directory


### ingest_dblp ###
#### Dependencies (tested) ####
| Package | Version |
| :-------: | :-------: |
| pymongo | 3.10.1  |
| lxml | 4.5.0 |

#### Running the script: ####
```
python xml_to_json.py -p <path-to-XML-dir> / --path <path-to-XML-dir>
```

If the path argument is not supplied, default behavior is to use the local directory

