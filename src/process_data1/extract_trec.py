#! /usr/bin/python

import codecs
import logging
from os.path import exists, isfile, isdir
from os import listdir
import sys


def trec_format(in_file, out_file):
    if exists(out_file):
        return
    with codecs.open(in_file, "r", "utf-8") as fl:
        origin = fl.read()
    with codecs.open(out_file, "w", "utf-8") as fl:
        doc_id = in_file.split("/")[-1].split(".")[0]
        fl.write("<DOC><DOCNO>")
        fl.write(doc_id)
        fl.write("</DOCNO><TEXT>")
        fl.write(origin)
        fl.write("</TEXT></DOC>")
        print doc_id


def main(file_dir, out_dir="/home/trec17dd/trec/datas/trec_xml/"):
    if not isdir(file_dir):
        return
    for file in listdir(file_dir):
        file_path = file_dir + "/" + file
        if isfile(file_path) and ".xml" in file_path:
            try:
                out_file = out_dir + file
                trec_format(file_path, out_file)
            except Exception as e:
                logging.exception("Exception: %s %s", file_path, e)
        elif isdir(file_path):
            main(file_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: extract_trec.py <file_dir>"
    else:
        main(sys.argv[1])
