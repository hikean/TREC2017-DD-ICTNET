#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
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

# Force matplotlib to not use any Xwindows backend.



def save_fig(out_file, x, y):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x, y)
    fig.savefig(out_file)
    plt.close()


def save_plot(out_file, xs, ys):
    colors, marks, labels = "krgby", "_.,ov", "a1234"
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for x, y, color, mark, label in zip(xs, ys, colors, marks, labels):
        ax.plot(x, y, (color), label=label, linewidth=1)
    fig.savefig(out_file)
    plt.close()


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


def interact_with_jig(jig, docs, interact_times=10):
    st_ptr = 0
    for i in range(interact_times):
        result = jig.run_itr(docs[st_ptr:st_ptr + 5])
        st_ptr += 5
        print "[#] iteration round:", i + 1
    return result


def print_jig_result(result):
    for item in result:
        print "\t {} {} {} {}".format(
            item["ranking_score"], item["on_topic"], item["doc_id"],
            item.get("subtopics", [{}])[0].get("rating", "none"))


def get_distances(doc_ids, in_dir, dtype="w2v", ngram=None, ngramc=None):
    def load_json(doc_ids, in_dir, dtype):
        def read_file(in_file):
            try:
                if dtype == "w2v":
                    return json.load(codecs.open(in_file, "r", "utf-8"))
                elif dtype == "words":
                    words = codecs.open(
                        in_file, "r", "utf-8"
                    ).read().strip().split(" ")[1].split(",")
                    # print len(words)
                    return words
                else:
                    return json.load(codecs.open(in_file, "r", "utf-8"))
                # print in_file, ">" * 10
            except Exception:
                logging.warning("[!] read_file %s failed", in_file)
                pass
            return None

        docs = [
            (doc_id, read_file(in_dir.format(doc_id))) for doc_id in doc_ids
        ]
        return {doc_id: vec for (doc_id, vec) in docs if vec is not None}

    def ngram_distance(docs, ngram, ngramc):
        def make_ngrams(doc, ngram):
            return [set([gram for gram in ngrams(doc, n)]) for n in ngram]

        def _distance(v1, v2):
            com = len((v1 & v2))
            return (len(v1) + len(v2) - 2 * com) ** 0.5

        def distance(da, db):
            return sum([
                _distance(v1, v2) * c for (v1, v2, c) in zip(da, db, ngramc)
            ])
        docs = {key: make_ngrams(docs[key], ngram) for key in docs}
        return {
            ka: {kb: distance(docs[ka], docs[kb]) for kb in docs}
            for ka in docs
        }
        # dmax = max([max(val) for val in dis.values()])
        # return {ka: {kb: dmax - dis[ka][kb] for kb in docs} for ka in docs}

    def w2v_distance(docs):
        def distance(v1, v2):
            return np.math.sqrt(sum((v1 - v2) ** 2))
        docs = {key: np.array(docs[key]) for key in docs}
        return {
            ka: {kb: distance(docs[ka], docs[kb]) for kb in docs}
            for ka in docs
        }
    docs = load_json(doc_ids, in_dir, dtype)
    if dtype == "w2v":
        return w2v_distance(docs)
    elif dtype == "words":
        if ngram is None:
            ngram, ngramc = (1, 2, 3), (0.15, 0.35, 0.5)
        return ngram_distance(docs, ngram, ngramc)
    else:
        return {}


def get_densities(distances, de_limit):
    def get_de(distances, de_limit):
        all_distance = np.array([
            distances[a][b] for a in distances for b in distances[a] if a != b
        ])
        return np.sort(all_distance)[int(len(all_distance) * de_limit)]

    def X(d, de):
        return 1 if d < de else 0
    de = get_de(distances, de_limit)
    return {
        i: sum([X(distances[i][j], de) for j in distances if i != j])
        for i in distances
    }


def get_heights(distances, densities):
    result = {}
    mdis = max([max(val.values()) for val in distances.values()])
    for i in densities:
        dis = [
            distances[i][j] for j in densities if i != j and
            densities[j] > densities[i]
        ]
        result[i] = mdis if len(dis) == 0 else min(dis)
    return result


def get_centers(heights, densities, hmin, dmin):
    return [i for i in heights if heights[i] > hmin and densities[i] > dmin]


def get_cluster(centers, densities, distances):
    sorted_densities = sorted(
        [(key, densities[key]) for key in densities],
        key=itemgetter(1),
        reverse=True
    )
    dict_densities = {
        key: i for i, (key, density) in enumerate(sorted_densities)
    }
    result = {key: [key] for key in centers}  # cluster with all docs
    cluster = {key: key for key in centers}  # doc => cluster_name
    for i, (key, density) in enumerate(sorted_densities):
        if key not in centers:
            j = min([j for (j, d) in sorted_densities[:i]],
                    key=lambda a: distances[key][a])
            cname = cluster[j]
            # for j, d in sorted_densities[:i]:
            #     if distances[key][j] < dis:
            #         dis = distances[key][j]
            #         cname = cluster[j]
            cluster[key] = cname
            result[cname].append(key)

    def get_pb(cname):
        try:
            item = min([
                min(
                    [(j, distances[i][j]) for j in distances if i != j and
                        cluster[j] != cname],
                    key=itemgetter(1)
                ) for i in result[cname]],
                key=itemgetter(1)
            )
        except:
            return 0
        return densities[item[0]]

    pbs = {c: get_pb(c) for c in result}
    ret = {
        c: [d for d in result[c] if densities[d] >= pbs[c]] for c in result
    }  # cluster deleted outsider
    return ret, cluster, result


def do_cluster(
        doc_ids, de_start, de_end, de_step, hmin, dmin, cluster_count,
        in_dir="../../datas/w2v/ebola_words/{}.json", dtype="w2v"):
    ngram, ngramc = (1, 2,), (1, 2)
    distances = get_distances(
        doc_ids, in_dir, dtype, ngram=ngram, ngramc=ngramc
    )
    logging.info(
        "[#] origin: %s docs, now: %s docs", len(doc_ids), len(distances))
    vals = [x for val in distances.values() for x in val.values()]
    vals = Counter(vals)
    keys = vals.keys()
    vals = [[vals[key] for key in keys], keys]
    json.dump(vals, codecs.open("dis.json", "w", "utf-8"))
    # return

    def run(de_limit):
        densities = get_densities(distances, de_limit=de_limit)
        heights = get_heights(distances, densities)
        keys = distances.keys()
        x = [densities[i] for i in keys]
        y = [heights[i] for i in keys]
        json.dump(
            [x, y],
            codecs.open("pts/{:.06f}.json".format(de_limit), "w", "utf-8")
        )
        save_fig("imgs/{:.06f}.png".format(de_limit), x, y)
        return
        dmin = sorted(
            densities.values(), reverse=True)[cluster_count * 10]
        hmin = sorted(
            [heights[h] for h in heights if densities[h] > dmin],
            reverse=True)[:cluster_count][-1]
        logging.info("[#] dmin: %s, hmin: %s", dmin, hmin)
        centers = get_centers(
            heights=heights, densities=densities, hmin=hmin, dmin=dmin)
        logging.info("[#]: centers %s, len: %s", centers, len(centers))

    while de_start < de_end:
        run(de_start)
        de_start += de_step


def enum_thread(process_id, process_count, in_dir, dtype, iter_count):
    logging.root.setLevel(logging.INFO)
    # solrs = get_all_ebola_solrs()
    solr = SolrClient(FULL_SOLR_URL)
    return_count = 800
    # key2id = du.load_ebola_map("key2id")
    # id2key = du.load_ebola_map("id2key")
    for tid, topic in eb_topics:
        # jig = JigClient(tot_itr_times=iter_count, topic_id=tid)
        docs = retrieval_top_k_doc_full(
            [topic], solr, return_count, query_range=['content']
        )
        # interact_with_jig(jig, docs, iter_count)
        # jig.judge()

        docids = [item[0] for item in docs]
        base_de = 0.001
        de_start = 0.1 * process_id / float(process_count) + base_de
        de_end = (0.1 * (process_id + 1)) / float(process_count) + base_de
        de_step = (0.1 / process_count) / 5

        do_cluster(
            docids, de_start=de_start,
            de_end=de_end, de_step=de_step,
            hmin=0, dmin=0, cluster_count=10,
            in_dir=in_dir,
            dtype=dtype
        )
        break


def docluster(
        doc_ids, de_limit, hmin, dmin, cluster_count,
        in_dir="../../datas/w2v/ebola_words/{}.json", dtype="w2v",
        ngram=None, ngramc=None):
    distances = get_distances(
        doc_ids, in_dir, dtype, ngram=ngram, ngramc=ngramc
    )
    logging.info(
        "[#] origin: %s docs, now: %s docs", len(doc_ids), len(distances))
    vals = [x for val in distances.values() for x in val.values()]
    vals = Counter(vals)
    keys = vals.keys()
    vals = [[vals[key] for key in keys], keys]
    json.dump(vals, codecs.open("dis.json", "w", "utf-8"))
    # return

    def run(de_limit):
        densities = get_densities(distances, de_limit=de_limit)
        heights = get_heights(distances, densities)
        keys = distances.keys()
        x = [densities[i] for i in keys]
        y = [heights[i] for i in keys]
        json.dump(
            [x, y],
            codecs.open("pts/{:.06f}.json".format(de_limit), "w", "utf-8")
        )
        save_fig("imgs/{:.06f}.png".format(de_limit), x, y)
        # return
        dmin = sorted(
            densities.values(), reverse=True)[cluster_count * 20]
        hmin = sorted(
            [heights[h] for h in heights if densities[h] > dmin],
            reverse=True)[:cluster_count][-1]
        logging.info("[#] dmin: %s, hmin: %s", dmin, hmin)
        centers = get_centers(
            heights=heights, densities=densities, hmin=hmin, dmin=dmin)
        logging.info("[#]: centers %s, len: %s", centers, len(centers))
        ret, cluster, result = get_cluster(centers, densities, distances)
        logging.info(
            "\n\tret: %s\n\tcluster: %s\n\tresult: %s\n\tcenters: %s\n",
            ret.keys(), cluster.keys(), result.keys(), centers
        )
        clst = sorted(
            [(key, len(result[key])) for key in result],
            key=itemgetter(1), reverse=True)  # clusterRank
        #  Rank(c, d)
        rcd = {
            c: {d: result[c].index(d) + 1 for d in result[c]} for c in result
        }
        return (ret, cluster, result,
                {d[0]: i + 1 for i, d in enumerate(clst)}, rcd)

    return run(de_limit)


def thread_main(in_dir, dtype, iter_count, return_count):
    logging.root.setLevel(logging.ERROR)
    solr = SolrClient(FULL_SOLR_URL)
    key2id = du.load_ebola_map("key2id")
    # id2key = du.load_ebola_map("id2key")
    jig = JigClient(tot_itr_times=iter_count, topic_id=None)
    for tid, topic in eb_topics:
        jig.topic_id = tid
        docs = retrieval_top_k_doc_full(
            [topic], solr, return_count, query_range=['content']
        )
        sub_docs = [item[0] for item in docs[:5]]
        result = jig.run_itr(docs[:5], topic_id=tid)
        # result = interact_with_jig(jig, docs[:5], iter_count)
        if result is None:
            logging.warning("[!] jig result is None")
            continue
        else:
            print_jig_result(result)

        doc_score = {
            key2id[item["doc_id"]]: item.get(
                "subtopics", [{}])[0].get("rating", -1000)
            for item in result
        }
        rqd = {d[0]: i for i, d in enumerate(docs)}
        doc_ids = [item[0] for item in docs]
        cret, cluster, cres, clsRank, Rcd = docluster(
            doc_ids=doc_ids, de_limit=0.02,
            hmin=0, dmin=8, cluster_count=10,
            in_dir=in_dir, dtype="w2v",
            ngram=None, ngramc=None
        )
        logging.info(
            "[#]\n\tcR: %s\n\tbDR: %s\n\tRcd: %s\n", clsRank,
            {}, Rcd
        )
        doc_dict = {item[0]: item for item in docs}
        docs = set([item[0] for item in docs[5:]])
        sn = set()
        p = 0.8
        for i in range(iter_count - 1):
            bestDocRank = {
                c: max([5 - doc_score.get(d, -1000) for d in cres[c]])
                for c in cres
            }
            sn.update(sub_docs)
            sub_docs = []
            # next_doc(RestDocs, Sn, rqd, p, clstRank, bestDockRank, rankcd):
            for i in range(5):
                ndoc = next_doc(
                    docs, sn, rqd, p, clsRank, bestDocRank, Rcd
                )
                sub_docs.append(ndoc)
                sn.add(ndoc)
                docs.discard(ndoc)
            result = jig.run_itr([doc_dict[key] for key in sub_docs], topic_id=tid)
            if result is None:
                logging.warning("[!] jig result is None")
                break
            else:
                print_jig_result(result)
            doc_score.update({
                key2id[item["doc_id"]]: item.get(
                    "subtopics", [{}])[0].get("rating", -1000)
                for item in result
            })
        jig.judge()
    jig.judge()


def topic_thread(process_id, process_count, return_count, count=None):
    if count is None:
        count = return_count + 5
    logging.root.setLevel(logging.INFO)
    solr = SolrClient(FULL_SOLR_URL)
    out_dir = "imgs/{}.jpg"
    topics = eb_topics[:count][process_id::process_count]
    for tid, topic in topics:
        out_file = out_dir.format(tid)
        if exists(out_file):
            logging.info("[#] file: %s already existed.", out_file)
            continue
        jig = JigClient(tot_itr_times=(return_count / 5), topic_id=tid)
        docs = retrieval_top_k_doc_full(
            [topic], solr, return_count, query_range=['content']
        )
        xs, ys, index = [[0] for i in range(5)], [[0] for i in range(5)], 0
        while len(docs) > 0:
            result = jig.run_itr(docs[:5])
            docs = docs[5:]
            if result is None:
                index += 5
                continue
            for i, item in enumerate(result):
                score = item.get("subtopics", [{}])[0].get("rating", None)
                if score is not None:
                    xs[0].append(index + i + 1)
                    ys[0].append(ys[0][-1] + 1)
                    xs[score].append(index + i + 1)
                    ys[score].append(ys[score][-1] + 1)
            index += 5
        save_plot(out_file, xs, ys)


def main(choice=0):
    dtype, in_dir = "w2v", "../../datas/w2v/ebola_words/{}.json"
    # dtype, in_dir = "words", "../../datas/ebola_stem/{}.txt"
    if choice == 0:
        mp.multi_main(
            target=enum_thread,
            test_target=mp.partial(
                enum_thread, 0, 1, in_dir, dtype, iter_count=1
            ),
            in_dir=in_dir,
            dtype=dtype,
            iter_count=1
        )
    elif choice == 1:
        mp.multi_main(
            target=topic_thread,
            test_target=mp.partial(
                topic_thread, 0, 1, 100, 1
            ),
            return_count=500
        )
    else:
        thread_main(in_dir, dtype, iter_count=2, return_count=350)
    # for i in `ls *.png`; do imgcat $i; echo $i; done;
    # for i in `ls *.jpg`; do imgcat $i; echo $i; done;


if __name__ == "__main__":
    main(2)
