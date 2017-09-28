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


def interact_with_jig(jig, docs, interact_times=10):
    st_ptr = 0

    for i in range(interact_times):
        result = jig.run_itr(docs[st_ptr:st_ptr + 5])
        st_ptr += 5
        print "[#] iteration round:", i + 1
        for item in result:
            print "\t {} {} {} {}".format(
                item["ranking_score"], item["on_topic"], item["doc_id"],
                item.get("subtopics", [{}])[0].get("rating", "none"))


def run_test(topics, iter_count):
    import logging
    logging.root.setLevel(logging.WARNING)
    solr = SolrClient(FULL_SOLR_URL)
    jig = JigClient(None, tot_itr_times=iter_count)
    for topic_id, topic in topics:
        print '\n', '-' * 80
        # if "ebola" not in topic.lower():
        #     topic = topic + ", ebola"
        print "[#] Topic: {}, TopicID: {}".format(topic, topic_id),
        jig.topic_id = topic_id
        docs = retrieval_top_k_doc_full(
            topic, solr, 1000, query_range=['title', 'content']
        )
        interact_with_jig(jig, docs, iter_count)
    jig.judge()


if __name__ == "__main__":
    # main()
    run_test(queries[9:18], iter_count=1)
