#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
import sys
# from os.path import exists
from collections import Counter

import multiprocess as mp
from clean_ebola import du


def deal_file(in_file):
    js = json.load(codecs.open(in_file, "r", "utf-8"))
    return Counter(js["words"])


def deal_thread(process_id, process_count, in_dir, out_dir, file_count):
    logging.info("[#] enter process<%s> in [%s]", process_id, process_count)
    file_id = process_id
    ct = Counter()
    real_cnt = 0
    while file_id < file_count:
        try:
            ct.update(deal_file(in_dir.format(file_id)))
            real_cnt += 1
        except Exception as e:
            logging.exception("[#][%s] Exception: %s", file_id, e)
        file_id += process_count
    fsum = float(sum(ct.values()))
    dc = {
        "counter": ct,
        "words_count": sum(ct.values()),
        "avg_len": fsum / real_cnt,
        "count": real_cnt
    }
    json.dump(dc, codecs.open(out_dir.format(process_id), "w", "utf-8"))


def main(data_type="ebola_stem", argv=sys.argv):
    base_dir = "../../datas/"
    file_count = du.ebola_file_count
    out_dir = base_dir + "LangModel/tmp/" + data_type + "_{}.m.json"
    in_dir = base_dir + data_type + "_json/{}.json"
    if data_type.startswith("ny"):
        in_dir = base_dir + data_type + "_json/{:07d}.json"
        file_count = du.ny_file_count

    # out_dir = "../../datas/LangModel/ebola_stem_{}.m.json"
    # in_dir = "../../datas/ebola_stem_json/{}.json"
    test = mp.partial(
        deal_thread, 0, 1,
        in_dir=in_dir, out_dir=out_dir, file_count=200
    )
    mp.multi_main(
        target=deal_thread,
        test_target=test,
        use_pool=True,
        argv=argv,
        in_dir=in_dir,
        out_dir=out_dir,
        file_count=file_count
    )
    logging.info("[#] multi_merge all done")


if __name__ == "__main__":
    logging.error("Use merge_counter.py instead.")
