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

import multiprocess as mp

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
    es.index(
        index="trec", body=deal_json(file_name),
        doc_type="nytimes", id=file_id)


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


if __name__ == "__main__":
    mp.multi_main(
        target=index_thread,
        test_target=mp.partial(
            index_thread, thread_id=0, thread_count=1, file_count=281
        )
    )
