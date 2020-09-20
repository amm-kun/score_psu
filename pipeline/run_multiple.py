import os
import time

start = time.time()
os.system(r"python process_docs.py -in C:\Users\arjun\dev\text_files\retractedErrorData -out "
          r"C:\Users\arjun\dev\GROBID_processed\RetractedErrorData -m generate-train -csv C:\Users\arjun\dev -lr 0-0.3")
os.system(r"python process_docs.py -in C:\Users\arjun\dev\text_files\replicationProject\FALSE -out "
          r"C:\Users\arjun\dev\GROBID_processed\ReplicationProject\FALSE -m generate-train -csv C:\Users\arjun\dev "
          r"-l 0")
os.system(r"python process_docs.py -in C:\Users\arjun\dev\text_files\replicationProject\TRUE -out "
          r"C:\Users\arjun\dev\GROBID_processed\ReplicationProject\TRUE -m generate-train -csv C:\Users\arjun\dev -l 1")
os.system(r"python process_docs.py -in C:\Users\arjun\dev\text_files\publishPre -out "
          r"C:\Users\arjun\dev\GROBID_processed\PublishPre -m generate-train -csv C:\Users\arjun\dev -lr 0.7-1")
end = time.time()

print("Time taken: ", end-start)
