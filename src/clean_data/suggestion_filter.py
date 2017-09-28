# -*- encoding: utf-8 -*-

import codecs
import json
import logging
import random
import re
import sys
import time
from collections import Counter
from operator import itemgetter

import requests
from lxml import etree
from nltk import ngrams

import multiprocess as mp
import extract_utils as exu
sys.path.append("..")
from utils.basic_init import *
import src.utils.data_utils as du
from src.utils.SolrClient import SolrClient
from src.utils.JigClient import *


def retrieval_top_k_doc_full(
        query, solr=SolrClient(), k=500,
        query_range=["content"], key2id=None):
    st = set()

    def find_and_insert(key):
        if key in st:
            return True
        st.add(key)
        return False
    fl = 'key,doc_id'
    if key2id is None:
        key2id = du.load_ebola_map("key2id")
    docs = []
    for v in query_range:
        logging.info("[#] solr query: %s", v)
        docs.extend(solr.query_fields(query, v, fl, rows=k))
    logging.info("[#] solr result %s", docs[1])
    docs = [
        (key2id[key], key, score) for (key, score) in
        [(dct["key"][0], dct["score"]) for dct in docs]
    ]
    docs = sorted(docs, key=itemgetter(2, 0), reverse=True)
    return [
        (nid, key, score) for (nid, key, score) in docs
        if not find_and_insert(key)][:k]


def load_json_data(doc_ids, in_dir):
    result = {}
    for did in doc_ids:
        try:
            result[did] = json.load(
                codecs.open(in_dir.format(did), "r", "utf-8"))
        except Exception as e:
            logging.info("%s load failed", e)
    return result


def doc2words(doc):
    if isinstance(doc, dict):
        keys = ["content", "a", "content_full_text", "ps", "h2", "title"]
        doc = exu.undict(doc)
        text = [exu.unlist(doc[key]) for key in keys if key in doc]
    else:
        text = [exu.unlist(doc)]
    try:
        text = " ".join(text)
    except:
        print doc, "holy shit"*20
    return set(du.basic_preprocess(text, length_limit=1))


def deal(words, topic, solr, in_dir, topk=350):
    solr_docs = retrieval_top_k_doc_full(
        [topic], solr, 600, query_range=['content'], key2id=None)

    doc_ids = [item[0] for item in solr_docs]
    docs = load_json_data(doc_ids, in_dir)
    cts = [Counter(doc2words(docs[did])) for did in docs]
    result = []
    for su in set(words):
        sus = set(du.basic_preprocess(su))
        if len(sus) == 0:
            continue
        cnt = 0
        for ct in cts:
            cnt += min([ct.get(s, 0) for s in sus])
        if cnt > 0:
            result.append([su, cnt])
    return result


def parse_args(args, se_name="google"):
    out_dir = "/home/zhangwm/trec/datas/filter_suggestion/tmp/{}-{}.json"
    if "bing" in args:
        se_name = "bing"
    if "ebola" in args:
        in_dir = "/home/zhangwm/trec/datas/ebola_full/{}.json"
        in_file = "../../datas/{}_ebola.sg.json".format(se_name)
        dtype = "ebola"
        if "ngram" in args:
            in_file = "../../datas/{}_ngram_ebola.sg.json".format(se_name)
    else:
        dtype = "nytimes"
        in_dir = "/home/zhangwm/trec/datas/ny_json/{:07d}.json"
        in_file = "../../datas/{}_nytimes.sg.json".format(se_name)
        if "ngram" in args:
            in_file = "../../datas/{}_ngram_nytimes.sg.json".format(se_name)
    if "ngram" in args:
        dtype = dtype + "_ngram"
    return in_file, in_dir, out_dir, dtype


def filter_thread(process_id, process_count, options):
    from es_test import TOPICS as eb_topics
    from es_test import NY_TOPICS as ny_topics
    from es_test import PL_TOPICS as pl_topics
    args = options
    topics = []
    if "all" in args:
        topics = eb_topics + ny_topics
    if "ALL" in args:
        topics = eb_topics + pl_topics + ny_topics
    if "ebola" in args:
        topics.extend(eb_topics)
    if "nytimes" in args:
        topics.extend(ny_topics)
    if "polar" in args:
        topics.extend(pl_topics)
    if "test" in args:
        topics = topics[:2]
    in_file, in_dir, out_dir, dtype = parse_args(args)

    suggestions = json.load(codecs.open(in_file, "r", "utf-8"))
    results = {}
    solr = SolrClient(FULL_SOLR_URL)
    topics = topics[process_id::process_count]
    for topic_id, topic in topics:
        words = set(suggestions[topic_id])
        if len(words) == 0:
            results[topic_id] = []
        else:
            try:
                results[topic_id] = deal(words, topic, solr, in_dir)
            except Exception as e:
                logging.exception("deal Exception: %s", e)
    out_file = out_dir.format(dtype, process_id)
    print "\n" * 2, results
    json.dump(results, codecs.open(out_file, "w", "utf-8"))



def merge_results(options, process_count):
    in_file, in_dir, out_dir, dtype = parse_args(options)
    results = {}
    for i in range(process_count):
        in_file = out_dir.format(dtype, i)
        try:
            results.update(json.load(codecs.open(in_file, "r", "utf-8")))
        except Exception as e:
            print in_file, e
    json.dump(
        results, codecs.open(out_dir.format(dtype, "merge"), "w", "utf-8"),
        indent=4)


def main():
    logging.root.setLevel(logging.WARNING)
    argsv = sys.argv
    if "merge" in argsv[1]:
        options = argsv[1]
        process_count = int(argsv.pop())
        merge_results(options, process_count)
    else:
        options = argsv.pop()
        mp.multi_main(
            target=filter_thread,
            test_target=mp.partial(
                filter_thread, 0, 1, options + "test"
            ),
            argv=argsv,
            options=options,
            use_pool=True
        )
    # try:
    #     process_count = int(argsv[-1])
    # except Exception:
    #     process_count = 1
    # merge_results(options, process_count)


if __name__ == "__main__":
    main()

# python suggestion_filter.py process 16 google_ebola
# plr suggestion_filter process 16 google_ebola

