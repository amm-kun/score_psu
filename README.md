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

#### Similarity ####
This script creates a class object for a pair of strings for (pairwise classification task for disambiguation) and 
contains functions that compute relevant feature values

Current feature function definitions that are available include:
1. Cosine Similarity

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

