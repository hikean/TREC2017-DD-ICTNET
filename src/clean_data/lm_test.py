# -*- encoding: utf-8 -*-

import json
import sys
# import os
import codecs
import re
from collections import Counter
from nltk import ngrams
import math
import logging
sys.path.append('../utils')

from JigClient import JigClient
from SolrClient import SolrClient
from constants import *
from Document import *

from es_test import TOPICS as queries
from es_test import interact_with_jig as interact
from langmodel import LangModel

DATA_DIR = "/home/zhangwm/trec/datas/"

def retrieval_top_k_doc_full(query, solr=SolrClient(), k=RET_DOC_CNT, query_range=[ "content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"]):
    fl = 'key,doc_id'

    irdocs = []

    for v in query_range:
        logging.info("ir: " + v)
        docs = solr.query_fields(query, v, fl, rows=k)
        irdocs += docs
    print "tot ir doc cnt:", len(irdocs)

    # print docs

    return irdocs2tuple_full(irdocs)[0:k]


def load_documents(doc_ids,
                   dir_template="/home/zhangwm/trec/datas/wordsjson/{}.json",
                   ignorecase=False):
    if ignorecase:
        return {doc_id: json.loads(
            codecs.open(dir_template.format(doc_id),
                "r", "utf-8").read().lower()) for doc_id in doc_ids}
    return {doc_id: json.load(
            codecs.open(dir_template.format(doc_id), "r", "utf-8")
            ) for doc_id in doc_ids}


def run_test(topic_id, query, iter_times, ignorecase=False):
    solr = SolrClient(FULL_SOLR_URL)
    jig = JigClient(topic_id,tot_itr_times=iter_times)
    docs = retrieval_top_k_doc_full(
        query, solr, 1000, query_range=['title', 'content']
    )
    # (id, "key", float(score))
    doc_ids = [str(item[0]) for item in docs]
    print doc_ids[:10], docs[:10]
    documents = load_documents(doc_ids, ignorecase=ignorecase)
    model = (json.load(codecs.open(DATA_DIR + "ebola_lm_i.json")) if ignorecase
             else json.load(codecs.open(DATA_DIR + "ebola_lm.json")))
    query = query.lower() if ignorecase else query
    lm = LangModel(model, ngram=(2,3))
    result = lm.get_candidate_words(documents, query)
    print docs[0]
    for key, value in result.most_common(20):
        print key,


if __name__ == "__main__":
    # main()
    run_test(queries[0][0], queries[0][1], 1, ignorecase=True)
