#! /usr/bin/python

import codecs
import json
import re
import logging
from urllib import unquote
from lxml import etree
from io import BytesIO, StringIO
import threading
import sys
import threading
from os import listdir
from os.path import exists, isfile, isdir
from elasticsearch import Elasticsearch


ELASTICS_HOSTS = ['http://localhost:9200/']
FILE_TEMPLATE = "../datas/ny_json/{:07d}.json"


def deal_json(file_name):
    body = json.load(codecs.open(file_name, "r", "utf-8"))
    metas = body["metas"]
    for key in ["dsk", "online_sections"]:
        if key in metas:
            body["classifier"].append(metas[key])
    content = body["content"]
    lead = [content[key] for key in content if key != "full_text"]
    body["blocks"] = {"lead": lead, "full_text": content.get("full_text", "")}
    body["metas"] = json.dumps(body["metas"])
    del body["content"]
    return body


def index_ebola(es, file_id):
    global FILE_TEMPLATE
    file_name = FILE_TEMPLATE.format(file_id)
    es.index(index="trec", body=deal_json(file_name), doc_type="nytimes", id=file_id)


def index_thread(thread_id, thread_count, file_count=1855658):
    es = Elasticsearch(ELASTICS_HOSTS)
    file_id = thread_id
    while file_id <= file_count:
        try:
            index_ebola(es, file_id)
            if file_id % 101 == thread_id:
                logging.warning("[#] processing file %s.json", file_id)
        except Exception as e:
            logging.exception("[!] index nytimes exception: %s", e)
        file_id += thread_count

def usage():
    print """Usage:
        python import_nytimes.py test [file_count]
        python import_nytimes.py process <process_id> <process_count>
        python import_nytimes.py thread <thread_count>"""

def main():
    logging.root.setLevel(logging.WARNING)
    if len(sys.argv) == 1:
        return usage()
    option = sys.argv[1]
    if option == "process":
        process_id = int(sys.argv[2])
        process_count = int(sys.argv[3])
        index_thread(process_id, process_count)
    elif option == "test":
        if len(sys.argv) == 3:
            index_thread(0, 1, int(sys.argv[2]))
        else:
            index_thread(0, 1, 300)
    elif option == "thread":
        thread_count = int(sys.argv[2])
        for thread in [threading.Thread(target=index_thread, args=(i, thread_count)) for i in range(thread_count)]:
            thread.start()
    else:
        usage()

if __name__ == "__main__":
    main()
    





