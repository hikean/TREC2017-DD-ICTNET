#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
from collections import Counter
from operator import itemgetter
from os.path import exists
import sys
import re

import multiprocess as mp
sys.path.append("../")
from utils.basic_init import *
from src.utils.SolrClient import SolrClient
from src.utils.Document import *
from src.utils.JigClient import *
from src.rmit.rmit_psg_max import retrieval_top_k_doc_full, interact_with_jig
from src.utils.IR_utils import *
from src.solution.ir_sys_blending import *


import src.utils.data_utils as du
from es_test import NY_TOPICS as ny_topics
from es_test import TOPICS as eb_topics
# from src.solution.ir_sys_blending import *

# from src.utils.Document import *
from src.utils.JigClient import *
from src.utils.SolrClient import SolrClient


def retrieval_top_k_doc_full(
        query, solr=SolrClient(), k=RET_DOC_CNT,
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


def del_no_ascii(text):
    return "".join(map(lambda a: a if ord(a) < 128 else " ", text))


def clean_ascii(text):
    chars = set((
        "1234567890" + "abcdefghijklmnopqrstuvwxyz" +
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "_'"))
    return "".join(map(lambda a: a if a in chars else " ", text))


def text_sim(ta, tb, length_limit=1):
    ta, tb = del_no_ascii(ta), del_no_ascii(tb)
    sa = set(du.stemmer_by_porter(du.basic_preprocess(ta, length_limit)))
    sb = set(du.stemmer_by_porter(du.basic_preprocess(tb, length_limit)))
    sab = sa & sb
    return len(sab) * 2.0 / float(len(sa) + len(sb))


def ny_query(solr, result, return_cnt=100, sim_limit=0.5):
    def get_date(url):
        date = re.findall(r"(\d+)/(\d+)/(\d+)", url)
        if len(date) > 0:
            return date[0]
        return None

    def url_title():
        title = result["url"].split("/")[-1].split(".")[0].split("-")
        return " ".join(title) + " " + result["title"]

    date = get_date(result["url"])
    if date is not None:
        if int(date[0]) > 2007 or int(date[0]) < 1987:
            return None
        date = "{0[0]}-{0[1]}-{0[2]}T00:00:00Z".format(date)
    keywords = clean_ascii(result["abstract"].strip())
    keywords = keywords + " " + clean_ascii(result["title"])
    keywords = keywords.replace("  ", " ").replace("  ", " ")
    # print keywords
    ret = solr.query_fields(
        keywords=[keywords], fl="title,key,date", rows=return_cnt) 
        # content_full_text

    if len(ret) == 0:
        print "\n\n", "None Result", "\n" * 2
        return None
    res = [item for item in ret if date is None or date == item["date"]]
    if len(res) == 1:
        return res[0]
    utitle = url_title()
    tres = []
    for item in res:
        try:
            if text_sim(item["title"], utitle) > sim_limit:
                tres.append(item)
        except:
            print item
    res = tres
    if len(res) >= 1:
        return res[0]
    else:
        return ret[0]


def print_jig_result(result, useprint=False):
    if result is None:
        logging.info("[#]: jig result is None")
        return
    output = ""
    for item in result:
        output += "\n\t{} {} {} {}".format(
            item["ranking_score"], item["on_topic"], item["doc_id"],
            item.get("subtopics", [{}])[0].get("rating", "none"))
    if not useprint:
        logging.info("[#] jig result:%s\n", output)
    else:
        print "\n", output

EBOLA_NYT_JIG_DIR = "/home/zhangwm/Software/jig/trec-dd-jig/"


def rejudege(all_subs, iter_counts, max_iter_count):
    for iter_count in iter_counts:
        jig = JigClient(
            tot_itr_times=iter_count, topic_id=None,
            base_jig_dir=EBOLA_NYT_JIG_DIR)
        should_judge = False
        if iter_count > max_iter_count:
            logging.error(
                "iter_count: %s is larger than max_iter_count: %s",
                max_iter_count)
        for topic_id in all_subs:
            sub_list = all_subs[topic_id]
            # print topic_id, len(sub_list)
            if len(sub_list) <= iter_count * 5:
                continue
            for i in range(iter_count):
                should_judge = True
                jig_result = jig.run_itr(sub_list[:5], topic_id=topic_id)

                print_jig_result(jig_result)
                sub_list = sub_list[5:]
        try:
            if should_judge:
                jig.judge()
        except:
            print "shit judge error"


def unique_sub_list(sub_list):
    def find_st(sub):
        if sub[1] in st:
            return False
        st.add(sub[1])
        return True
    st = set()
    return [item for item in sub_list if find_st(item)]


def ny_test(process_id, process_count, iter_count=10, t_count=100):
        # SolrClient(SOLR_SEG_nyt_LMD_URL),
        # SolrClient(SOLR_SEG_nyt_BM25_URL),
        # # SolrClient(SOLR_SEG_nyt_DFR_URL),
        # SolrClient(SOLR_SEG_nyt_IBS_URL),
        # SolrClient(SOLR_SEG_nyt_Classic_URL),
        # SolrClient(SOLR_SEG_nyt_LMJK_URL)
    solr = SolrClient(SOLR_SEG_nyt_LMD_URL)
    # jig = JigClient(
    #     tot_itr_times=iter_count, topic_id=None,
    #     base_jig_dir=EBOLA_NYT_JIG_DIR)
    js = json.load(
        codecs.open("../../datas/google_nytimes_all.json", "r", "utf-8"))
    all_subs = {}
    js = {tid: js[tid] for tid in js if js[tid] is not None}
    topics = [(tid, js[tid]) for tid in js]
    topics = topics[process_id::process_count][:t_count]
    for topic_id, results in topics:
        sub_list = []
        for result in results["results"][:50]:
            res = ny_query(solr, result, return_cnt=100)
            if res is None:
                continue
            sub_list.append((int(res["key"]), res["key"], res["score"]))
        if len(sub_list) > 0:
            print len(sub_list), "sub_list"
            sub_list = unique_sub_list(sub_list)
            sub_list = sub_list + ((5 - (len(sub_list) % 5)) * [sub_list[-1]])
        # print topic_id, "\n" * 2
        # for i in range(iter_count):
        #     if len(sub_list) < i * 5 + 5:
        #         break
        #     jig_result = jig.run_itr(
        #         sub_list[i * 5:i * 5 + 5], topic_id=topic_id)
        #     print_jig_result(jig_result)
        all_subs[topic_id] = sub_list
        dump_file = "dump/subs_{}_{}.json".format(process_count, process_id)
        json.dump(all_subs, codecs.open(dump_file, "w", "utf-8"))


if __name__ == "__main__":
    logging.root.setLevel(logging.WARNING)
    # all_subs = json.load(codecs.open("all_subs.json", "r", "utf-8"))
    # rejudege(all_subs, [1, 2, 3, 5, 10], 10)
    # if len(sys.argv) == 2:
    #     all_subs = json.load(codecs.open("all_subs.json", "r", "utf-8"))
    #     rejudege(all_subs, [1, 2, 3, 5, 10], 10)
    # else:
    # mp.multi_main(
    #     target=ny_test,
    #     test_target=mp.partial(
    #         ny_test, 0, 1, 10, 1
    #     ),
    #     use_pool=True
    # )
    try:
        process_count = int(sys.argv[-1])
        all_subs = {}
        for i in range(process_count):
            dump_file = "dump/subs_{}_{}.json".format(process_count, i)
            all_subs.update(json.load(codecs.open(dump_file, "r", "utf-8")))
        json.dump(all_subs, codecs.open("dump/all_subs.json", "w", "utf-8"))
        rejudege(all_subs, iter_counts=[1, 2, 3, 5, 10], max_iter_count=10)
    except Exception as e:
        logging.exception("[#] exception %s", e)

