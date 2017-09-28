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
FILE_TEMPLATE = "../datas/ebola_json/{}.json"


def get_title(html):
    try:
        title = html["metas"]["title"].strip()
        if len(title) > 3:
            return title
    except: pass
    try:
        title = html.get("title", "-").strip()
    except:
        title = "-"
    for tag in ["h2", "h3", "h1"]:
        if len(html.get(tag, [])) == 1 and title == "":
            return html.get(tag)[0]
        for value in html[tag]:
            value = value.strip()
            if value in title:
                return value
    return title.split("-")[0].strip()


def get_spacetime(html):
    for tag in ["h2", "h3", "h4", "h5"]:
        for value in html[tag]:
            if len(re.findall("[0-9]+", value)) >= 2:
                return value
    return ""


def deal_json(file_name):
    body = json.load(codecs.open(file_name, "r", "utf-8"))
    html = body["content"]
    try:
        body["description"] = html["metas"]["description"]
    except:
        body["description"] = ""
    body["title"] = get_title(html)
    body["spacetime"] = get_spacetime(html)
    body["content"] = html["p"]
    return body


def index_ebola(es, file_id):
    global FILE_TEMPLATE
    file_name = FILE_TEMPLATE.format(file_id)
    es.index(index="trec", body=deal_json(file_name), doc_type="ebola", id=file_id)


def index_thread(thread_id, thread_count, file_count=194481):
    es = Elasticsearch(ELASTICS_HOSTS)
    file_id = thread_id
    while file_id < file_count:
        try:
            index_ebola(es, file_id)
            if file_id % 101 == thread_id:
                logging.warning("[#] processing file %s.json", file_id)
        except Exception as e:
            logging.exception("[!] index ebola exception: %s", e)
        file_id += thread_count

def usage():
    print """Usage:
        python import_ebola.py test [file_count]
        python import_ebola.py process <process_id> <process_count>
        python import_ebola.py thread <thread_count>"""

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
    





