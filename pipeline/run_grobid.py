import os

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Pipeline - Process PDFS - Market Pre-processing")
#     parser.add_argument("--path", default=os.getcwd(), help="set grobid-client execution path")
#     parser.add_argument("--input", help="parent folder that contains all pdfs")
#     parser.add_argument("--grobid_out", help="grobid output path")
#     parser.add_argument("--mode", default="processFulltextDocument", help="grobid mode")
#
#     args = parser.parse_args()

    # python pipeline/pipeline.py --path C:\Users\arjun\repos\grobid-client-python\ --input C:\Users\arjun\dev\pdfs --grobid_out C:\Users\arjun\dev\xmls
    # os.chdir(args.path)
os.chdir(r"C:\Users\arjun\repos\grobid-client-python")
# command = "grobid-client.py --input {0} --output {1} {2}".format(args.input, args.grobid_out, args.mode)
command = r"grobid-client.py --input C:\Users\arjun\dev\GroundTruth-KnownReplicationStudies\PublishedPreprints\pre_pubPDF --output C:\Users\arjun\dev\GROBID_processed\PublishPre --n 4 processFulltextDocument"
os.system(command)
    # print("Coverting PDF to TXT")
    # os.system(r"C:\Users\arjun\dev\xpdf-tools-win-4.02\bin64\pdftotext C:\Users\arjun\dev\pdfs\*")
    # xml = parse_dir_xml(args.grobid_out)
    # xml = parse_dir_xml(r"C:\Users\arjun\dev\xmls")
    # for file in xml:
    #     parse_xml(file)
    # print(perNER(XML2ack(r'C:\Users\arjun\dev\xmls\4.tei.xml')))
    # print(NER(XML2ack(r'C:\Users\arjun\dev\xmls\4.tei.xml')))