#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
from os.path import exists
from collections import Counter
import sys
import multiprocess as mp

sys.path.append("../utils")

import data_utils as du


def deal_nytimes(
        file_id, in_dir, out_dir, json_dir, stem_dir, stem_jsdir,
        overwrite=False):
    def get_content(blocks):
        try:
            max_len = max([len(b) for b in blocks])
            main = [b for b in blocks if len(b) == max_len][0].strip()
            blocks = [b for b in blocks if main.startswith(b.strip())]
            return blocks + [main]
        except Exception as e:
            logging.exception("[!][%s] Exception: %s", file_id, e)
            return []

    def write_line_data(file_name, key, words):
        with codecs.open(file_name, "w", "utf-8") as fl:
            fl.write("{} ".format(key))
            fl.write(",".join(words))
            fl.write("\n")

    in_file = in_dir.format(file_id)
    out_file = out_dir.format(file_id)
    json_file = json_dir.format(file_id)
    stem_file = stem_dir.format(file_id)
    stem_json = stem_jsdir.format(file_id)
    if exists(out_file) and exists(stem_file) and not overwrite:
        return False
    logging.info("[#] dealing file: %s", in_file)

    js = json.load(codecs.open(in_file, "r", "utf-8"))
    text = " ".join([js["title"]] + get_content(js["content"].values()))
    words = du.basic_preprocess(text)

    if not exists(out_file) or overwrite:
        write_line_data(out_file, js["doc_id"], words)

    stems = du.stemmer_by_porter(words)
    if not exists(stem_file) or overwrite:
        write_line_data(stem_file, js["doc_id"], stems)
    doc_dict = {
        "words": Counter(words),
        "id": file_id,
        "key": js["doc_id"]
    }
    if not exists(json_file) or overwrite:
        json.dump(
            doc_dict,
            codecs.open(json_file, "w", "utf-8")
        )

    if not exists(stem_json) or overwrite:
        doc_dict["words"] = Counter(stems)
        json.dump(
            doc_dict,
            codecs.open(stem_json, "w", "utf-8")
        )
    return True


def deal_thread(
        thread_id, thread_count, in_dir, out_dir,
        json_dir, stem_dir, stem_jsdir, file_count=1855688):
    file_id = thread_id
    while file_id < file_count:
        try:
            deal_nytimes(
                file_id, in_dir, out_dir, json_dir, stem_dir, stem_jsdir
            )
        except Exception as e:
            logging.exception("[!][%s] Exception: %s", file_id, e)
        file_id += thread_count


def main():
    in_dir = "../../datas/ny_json/{:07d}.json"
    out_dir = "../../datas/ny_words/{:07d}.txt"
    json_dir = "../../datas/ny_words_json/{:07d}.json"
    stem_dir = "../../datas/ny_stem/{:07d}.json"
    stem_jsdir = "../../datas/ny_stem_json/{:07d}.json"
    test = mp.partial(
        deal_thread, 0, 1,
        in_dir=in_dir, out_dir=out_dir, json_dir=json_dir,
        stem_dir=stem_dir, stem_jsdir=stem_jsdir, file_count=200
    )
    mp.multi_main(
        target=deal_thread,
        test_target=test,
        in_dir=in_dir,
        out_dir=out_dir,
        json_dir=json_dir,
        stem_dir=stem_dir,
        stem_jsdir=stem_jsdir
    )


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    main()
