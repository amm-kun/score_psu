## Feature extraction Pipeline

The pipeline is designed to extract features from scholarly work. Given a scholarly work, it extracts various features of the scholarly work and output features as a CSV file.

However, it cannot process the PDFs directly, instead, we input preprocessed PDF files using GROBID and pdf2text. This preprocessing can be done both by pipeline or individually before extracting the features. 


### Preprocessing PDFs

Preprocessing can be done by either using pipeline or separately running GROBID and pdf2text. In both cases, it is required to have a working GROBID and pdf2text installation.

PDF files have to be preprocessed using 

1) [GROBID](https://grobid.readthedocs.io/en/latest/)
2) [PDF2Text](https://linux.die.net/man/1/pdftotext)

While preprocessing with GROBID, it is required to convert using full text mode i.e., **/api/processFulltextDocument**, please refer to GROBID documentation for more details.

Once GROBID is installed and running, and pdf2text is installed, we can use the pipeline to preprocess the PDF files using the below command:

`python process_docs.py --mode  process-pdfs  --pdf_input DIR_TO_PDFs -out OUTPUT_DIR`

Alternatively, one can process them separately without using the pipeline.


### Running the pipeline feature extraction

Once the PDFs are processed using GROBID and pdf2text, we can run a pipeline for feature extraction:
You can run the pipeline using the below command:

`python process_docs.py -out PROCESSED_GROBID_FILES -in TEXT_FILES -m generate-train"  -csv OUTPUT_DIR`

-out: path to preprocessed PDF files in tei.xml format(grobid output)

-in: path to preprocessed PDF files in txt format(output of pdf2text)

-m: generate-train mode 

-csv: csv output directory

For more details, refer to process_docs.py file.

## For claimevidence code

Clone the scifact repository in /pipeline from https://github.com/allenai/scifact

### Project Structure
Important files for reference:

| File        | Description     |   
| ------------- |:------------- |
| process_docs.py     | code execution starts here, there are 2 main modes (1) Preprocess (2) generate feature set | 
| extractor.py      | grobid output gets torn down into various features and extracted information is used to call elsevier/crossref/semantic scholar api     | 
| elsevier.py | Output from elsevier api/crossref/semantic scholar gets parsed and returned |
| XIN.py | acknowlegement section is processed to identify funding information |

**NOTE:** Elsevier api key may expire after certain number of hits. In case of batch processing, it is better to update api key details from elsevier developer [portal](https://dev.elsevier.com). Check the same for semantic scholar api.


**NOTE** Place the citation sentiment model under pipeline/tamu_features/rec_model/pytorch_model.bin from the [link](https://drive.google.com/file/d/1Yd_x-65bCqu8kJlo6QaIltoNv2CCEU0w/view?usp=sharing)
