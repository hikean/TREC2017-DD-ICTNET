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
FILE_TEMPLATE = "../../dk/data/clean_ebola_json/{}.json"


def get_title(html):
    try:
        title = html["content_metas_title"].strip()
        if len(title) > 3:
            return title
    except Exception:
        pass
    try:
        title = html.get("content_title", "-").strip()
    except Exception:
        title = "-"
    for tag in ["content_h2", "content_h3", "content_h1"]:
        if len(html.get(tag, [])) == 1 and title == "":
            return html.get(tag)[0]
        for value in html[tag]:
            value = value.strip()
            if value in title:
                return value
    return title.split("-")[0].strip()


def get_spacetime(html):
    for tag in ["content_h2", "content_h3", "content_h4", "content_h5"]:
        for value in html[tag]:
            if len(re.findall("[0-9]+", value)) >= 2:
                return value
    return ""


def deal_json(file_name):
    body = json.load(codecs.open(file_name, "r", "utf-8"))
    html = body
    try:
        body["description"] = html["content_metas_description"]
    except Exception:
        body["description"] = ""
    body["title"] = get_title(html)
    body["spacetime"] = get_spacetime(html)
    body["content"] = html["content_p"]
    return body

    """
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
    """


def index_ebola(es, file_id):
    global FILE_TEMPLATE
    file_name = FILE_TEMPLATE.format(file_id)
    es.index(
        index="trec3", body=deal_json(file_name), doc_type="ebola", id=file_id)


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


if __name__ == "__main__":
    mp.multi_main(
        target=index_thread,
        test_target=mp.partial(
            index_thread, thread_id=0, thread_count=1, file_count=281
        )
    )

