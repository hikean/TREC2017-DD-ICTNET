#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
from os.path import exists

import src.kean.multiprocess as mp
import src.utils.data_utils as du
import src.utils.w2v_utils as wu

# from gensim.models import Word2Vec


w2v_content_model = "/home/zhangwm/zhangweimin/Data/trec/build_data/ebola/textmodel/content_w2v.model"


def deal(in_file, out_file, w2v, overwrite):
    if not overwrite and exists(out_file):
        return
    with codecs.open(in_file, "r", "utf-8") as fl:
        line = fl.read().strip().split(" ")
    if len(line) <= 1:
        logging.exception("[!]file: %s words is empty", in_file)
    else:
        json.dump(
            w2v.doc2vec(doc=line[-1], sp=","),
            codecs.open(out_file, "w", "utf-8")
        )


def process_deal(
        process_id, process_count, in_dir, out_dir, file_count,
        overwrite=False):
    vu = wu.VecUtils()
    file_id = process_id
    while file_id < file_count:
        try:
            deal(
                in_dir.format(file_id), out_dir.format(file_id), vu, overwrite
            )
        except Exception as e:
            logging.exception(
                "[!] [%s] process_deal Exception: %s", file_id, e)
        file_id += process_count


def main(data_type="ebola_words", base_dir="../../datas/"):
    in_dir = base_dir + data_type + "/{}.txt"
    out_dir = base_dir + "w2v/" + data_type + "/{}.json"
    file_count = du.ebola_file_count
    if "ny" in data_type:
        in_dir = base_dir + data_type + "/{:07d}.txt"
        out_dir = base_dir + "w2v/" + data_type + "/{:07d}.json"
        file_count = du.ny_file_count

    mp.multi_main(
        target=process_deal,
        test_target=mp.partial(
            process_deal, 0, 1, in_dir, out_dir, 200
        ),
        in_dir=in_dir,
        out_dir=out_dir,
        file_count=file_count
    )


if __name__ == "__main__":
    main()
