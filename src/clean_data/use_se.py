#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
from multiprocessing import Queue
from collections import Counter
from operator import itemgetter
from os.path import exists
import sys

import numpy as np
from nltk import ngrams
from dcluster import next_doc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import extract_utils as exu

sys.path.append("../")
from utils.basic_init import *

import src.utils.data_utils as du
import multiprocess as mp
from es_test import NY_TOPICS as ny_topics
from es_test import TOPICS as eb_topics
# from src.solution.ir_sys_blending import *

# from src.utils.Document import *
from src.utils.JigClient import *
from src.utils.SolrClient import SolrClient
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


def jig_iter(jig, docs, topic_id):
    result = jig.run_itr(docs, topic_id=topic_id)
    for item in result:
        print "\t {} {} {} {}".format(
            item["ranking_score"], item["on_topic"], item["doc_id"],
            item.get("subtopics", [{}])[0].get("rating", "none"))
    return [
        (key2id(item["doc_id"]),
            item.get("subtopics", [{}])[0].get("rating", 0)) for item in result
    ]


def load_json_data(doc_ids, in_dir):
    return {
        did: json.load(codecs.open(in_dir.format(did), "r", "utf-8"))
        for did in doc_ids
    }


def print_jig_result(result):
    if result is None:
        logging.info("[#]: jig result is None")
        return
    output = ""
    for item in result:
        output += "\n\t{} {} {} {}".format(
            item["ranking_score"], item["on_topic"], item["doc_id"],
            item.get("subtopics", [{}])[0].get("rating", "none"))
    logging.info("[#] jig result:%s\n", output)


def extract_bing_url(url):
    from urllib import unquote
    url = url.split("&u=")[-1]
    return unquote(url)


def unique_result(results, dtype):
    def find_insert(result):
        url = result["title"]
        # if dtype == "bing":
        #     url = extract_bing_url(url)
        #     result["url"] = url
        if url in st:
            return False
        st.add(url)
        return True
    st = set()
    logging.info("[#] results length before unique: %s", len(results))
    print "[#] results length before unique: {}".format(len(results))
    results = [result for result in results if find_insert(result)]
    logging.info("[#] results length after unique: %s", len(results))
    print "[#] results length after unique: {}".format(len(results))
    return results


def get_se_sim(docs, se_results, likehood, dtype):
    def deal_text(text, length_limit=1):
        return du.stemmer_by_porter(du.basic_preprocess(text, length_limit))

    def deal_doc(doc):
        if "nytimes" in dtype:
            text = res["title"] + " "
            try:
                text += " ".join(res["content"].values())
            except Exception:
                pass
        else:
            text = " ".join(doc["ps"]) + " " + doc["title"]
        doc["sim"] = set(deal_text(text))
        return doc

    def deal_result(res):
        text = " ".join([res["title"], res["abstract"]])
        res["sim"] = set(deal_text(text))
        return res

    def compute_sim(doc, result, ):
        if "url" in doc and doc["url"].strip() == result["url"].strip():
            return 1
        d, r = doc["sim"], result["sim"]
        dr = len(d & r)
        return dr / float(max(12, len(r)))

    print "in get_se_sim"
    if se_results is None or se_results["results"] is None:
        return []
    print "before unique_result"
    results = unique_result(se_results["results"], dtype)
    results = [deal_result(res) for res in results]
    docs = {did: deal_doc(docs[did]) for did in docs}

    sim_doc, sim_values = {}, []
    for did in docs:
        doc = docs[did]
        for result in results:
            sval = compute_sim(doc, result)
            if (sval > likehood and
               (did not in sim_doc or sval > sim_doc[did])):
                    sim_doc[did] = sval
            sim_values.append(sval)
    # logging.warning("[#] sim_doc %s\nsim_values: %s", sim_doc, sim_values)
    return sim_doc


def thread_main(
        process_id, process_count, in_dir, out_dir, dtype, se_name,
        iter_count, return_count, likehood, test=False):
    try:
        return _thread_main(
            process_id, process_count, in_dir, out_dir, dtype, se_name,
            iter_count, return_count, likehood, test)
    except Exception as e:
        logging.exception("[#] Exception: %s", e)


def _thread_main(
        process_id, process_count, in_dir, out_dir, dtype, se_name,
        iter_count, return_count, likehood, test=False):
    if "nytimes" in dtype:
        solr = SolrClient(SOLR_SEG_nyt_LMD_URL)
    else:
        solr = SolrClient(FULL_SOLR_URL)
    key2id = du.load_ebola_map("key2id")
    se_results = du.load_se_results(se_name=se_name, dtype=dtype)
    # id2key = du.load_ebola_map("id2key")
    # jig = JigClient(tot_itr_times=iter_count, topic_id=None)
    jig = JigClient(
            tot_itr_times=iter_count, topic_id=None,
            base_jig_dir=EBOLA_NYT_JIG_DIR)
    if "ebola" in dtype:
        topics = eb_topics
    if "nytimes" in dtype:
        topics = ny_topics
    if test:
        topics = [eb_topics[2], eb_topics[3], eb_topics[5], eb_topics[24]]
        logging.root.setLevel(logging.WARNING)
    frame_list = []
    topics = topics[process_id::process_count]
    print topics
    for tid, topic in topics:
        logging.info("[#] id: %s, topic: %s\n", tid, topic)
        if "ebola" in dtype:
            solr_docs = retrieval_top_k_doc_full(
                [topic], solr, 600, query_range=['content'], key2id=key2id
            )
        else:
            solr_docs = solr.query_fields(
                keywords=[topic], fl="title,key,date", rows=return_count)
            solr_docs = [(d["key"], d["key"], d["score"]) for d in solr_docs]
        ddocs = {d[0]: d for d in solr_docs}
        doc_ids = ddocs.keys()
        if "ebola" in dtype:
            jdocs = {
                did: exu.extract_ebola(
                    in_file=in_dir.format(did)
                )
                for did in doc_ids[:return_count]
            }
        else:
            jdocs = {}
            for did in doc_ids[:return_count]:
                try:
                    jdocs[did] = json.load(
                        codecs.open(in_dir.format(did), "r", "utf-8"))
                except:
                    pass
        sim_docs = get_se_sim(jdocs, se_results[tid], likehood, dtype=dtype)
        sim_ratings = [
            (did, (sim_docs[did]), ddocs[did][2])
            for did in sim_docs
        ]
        limit_score = likehood  # (likehood + 0.1) * solr_docs[return_count][2]
        sim_ratings = sorted(sim_ratings, key=itemgetter(1, 2), reverse=True)
        logging.info("[#] sim_ratings: %s", sim_ratings)
        frame = {
            "solr_docs": solr_docs, "return_count": return_count,
            "sim_docs": sim_docs, "ddocs": ddocs,  # "jdocs": jdocs
            "sim_ratings": sim_ratings, "iter_count": iter_count,
            "topic_id": tid, "topic": topic
        }
        sim_ids = [item[0] for item in sim_ratings if item[1] > limit_score]
        sub_list, sub_set = [], set()
        solr_p = 0
        for i in range(iter_count):
            sub_ids = set(doc_ids[:solr_p])
            doc_ids = doc_ids[solr_p:]
            while len(sub_ids) < 5:
                if len(sim_ids) > 0:
                    sub_ids.add(sim_ids[0])
                    sim_ids = sim_ids[1:]
                elif len(doc_ids) > 0:
                    sub_ids.add(doc_ids[0])
                    doc_ids = doc_ids[1:]
                else:
                    break
                sub_ids = set([did for did in sub_ids if did not in sub_set])
            sub_set.update(sub_ids)
            sub_list.extend(list(sub_ids))
            # result = jig.run_itr(
            #     [ddocs[did] for did in sub_ids], topic_id=tid)
            # print_jig_result(result)
        frame["sub_list"] = sub_list
        frame_list.append(frame)
        # jig.judge()
    ps = "{}-{}".format(process_count, process_id)
    json.dump(
        frame_list, codecs.open(out_dir.format(ps), "w", "utf-8"))
    if test:
        jig.judge()
        rejudege(
            process_count, iter_counts=[1, 2, 3, 5],
            max_iter_count=iter_count, out_dir=out_dir)


def rejudege(
        process_count, iter_counts,
        max_iter_count, out_dir, dtype="ebola"):
    import time
    frames = []
    for i in range(process_count):
        ps = "{}-{}".format(process_count, i)
        try:
            frames.extend(
                json.load(codecs.open(out_dir.format(ps), "r", "utf-8")))
        except:
            pass
    print "queue len:", len(frames)
    json.dump(
        frames, codecs.open(out_dir.format(int(time.time())), "w", "utf-8"))

    rank = {frame["topic_id"]: frame["sub_list"] for frame in frames}
    json.dump(
        rank, codecs.open("frames/{}_rank.json".format(dtype), "w", "utf-8"))

    for iter_count in iter_counts:
        jig = JigClient(
            tot_itr_times=iter_count, topic_id=None,
            base_jig_dir=EBOLA_NYT_JIG_DIR)
        if iter_count > max_iter_count:
            logging.error(
                "iter_count: %s is larger than max_iter_count: %s",
                max_iter_count)
        for frame in frames:
            topic_id = frame["topic_id"]
            sub_list = frame["sub_list"]
            ddocs = frame["ddocs"]
            for i in range(iter_count):
                jig.run_itr(
                    [ddocs[str(did)] for did in sub_list[:5]],
                    topic_id=topic_id)
                sub_list = sub_list[5:]
        jig.judge()


def main(iter_count, return_count, likehood, in_dir, out_dir, dtype, se_name):
    mp.multi_main(
        target=thread_main,
        test_target=mp.partial(
            thread_main, process_id=0, process_count=1,
            in_dir=in_dir, out_dir=out_dir, dtype=dtype,
            se_name=se_name, iter_count=iter_count, return_count=return_count,
            likehood=likehood, test=True
        ),
        use_pool=True,
        in_dir=in_dir, out_dir=out_dir, dtype=dtype,
        se_name=se_name, iter_count=iter_count, return_count=return_count,
        likehood=likehood, test=False
    )
    if "process" in sys.argv:
        process_count = int(sys.argv[-1])
        rejudege(
            process_count, iter_counts=[1, 2, 3, 5, 10],
            max_iter_count=iter_count, out_dir=out_dir, dtype=dtype)

    print "\nDone!"


if __name__ == "__main__":
    logging.root.setLevel(logging.WARNING)
    iter_count, return_count, likehood = 10, 250, 0.5
    in_dir, dtype, se_name = "../../datas/ebola/{}.json", "ebola", "google"

    iter_count, return_count, likehood = 10, 300, 0.6
    in_dir, dtype, se_name = (
        "../../datas/ny_json/{:07d}.json", "nytimes", "google")

    out_dir = "frames/" + dtype + "_{}.json"
    main(
        iter_count=iter_count,
        return_count=return_count,
        likehood=likehood,
        in_dir=in_dir,
        out_dir=out_dir,
        dtype=dtype,
        se_name=se_name
    )
