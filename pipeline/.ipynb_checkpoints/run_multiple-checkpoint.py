import os
import time

start = time.time()
os.system(r"python process_docs.py -in ~/data/train_texts/retractedErrorData -out "
          r"~/data/GROBID_processed/RetractedErrorData -m generate-train -csv ~/data/output -lr 0-0.3")
os.system(r"python process_docs.py -in ~/data/train_texts/replicationProject/FALSE -out "
          r"~/data/GROBID_processed/ReplicationProject/FALSE -m generate-train -csv ~/data/output "
          r"-l 0")
os.system(r"python process_docs.py -in ~/data/train_texts/replicationProject/TRUE -out "
          r"~/data/GROBID_processed/ReplicationProject/TRUE -m generate-train -csv ~/data/output -l 1")
os.system(r"python process_docs.py -in ~/data/train_texts/publishPre -out "
          r"~/data/GROBID_processed/PublishPre -m generate-train -csv ~/data/output -lr 0.7-1")
os.system(r"python process_docs.py -out ~/data/GROBID_processed/test -in ~/data/test_texts -m extract-test -f ~/data/test_texts/covid_ta3.tsv -csv ~/data/output")

"""python process_docs.py -out ~/GROBID_processed/test -in ~/test_texts -m extract-test -f ~/test_texts/covid_ta3.tsv -csv ~/output"""
""" python process_docs.py -in ~/data/2400set/txts/ -out ~/data/2400set/processed/ -m 2400set -f ~/data/2400set/filtered.csv -csv ~/data/output/ -l 1"""
end = time.time()

print("Time taken: ", end-start)



"""
 for file in *.pdf; do pdftotext "$file"; done
"""
