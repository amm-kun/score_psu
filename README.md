# SCORE_PSU
## Repository for Python scripts pertaining to the DARPA SCORE project effort by PSU ##

### ingest_WoS ###
#### Dependencies (tested) ####
| Package | Version |
| :-------: | :-------: |
| pymongo | 3.10.1  |


####Running the script: ####
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

####Running the script: ####
```
python xml_to_json.py -p <path-to-XML-dir> / --path <path-to-XML-dir>
```

If the path argument is not supplied, default behavior is to use the local directory

### Miscellaneous functions ###

connect_db
:Usage: connect_db(Database, Host-IP, DB-Port)

insert_record
:Database_client_object, collection, JSON-to-be-inserted



