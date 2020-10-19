python process_docs.py -m generate-train -l 1 -out ~/data/retractionWork/data/posTextRank1/ -in ~/data/retractionWork/data/posTextRanktxt/ -csv ~/data/retractionWork/data/output/
python process_docs.py -m generate-train -l 0 -out ~/data/retractionWork/data/retractedSet/ -in ~/data/retractionWork/data/retractedSettxt/ -csv ~/data/retractionWork/data/output/
python process_docs.py -m generate-train -l 1 -out ~/data/retractionWork/data/posPUB/ -in ~/data/retractionWork/data/posPUBtxt/ -csv ~/data/retractionWork/data/output/
