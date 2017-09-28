#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
import re
import sys
import time
import random
from os.path import exists

sys.path.append("..")

import requests
from lxml import etree
from nltk import ngrams

import multiprocess as mp
import extract_utils as exu

import utils.data_utils as du
# from urllib import urlencode, quote
# import HTMLParser


def merge_field(js, dtype="ebola"):
    def merge_ebola(js):
        js = exu.undict(js)
        ps, h2 = js["ps"], js["h2"]
        if not isinstance(ps, list):
            ps = [ps]
        if not isinstance(h2, list):
            h2 = [h2]
        js["content"] = h2 + ps
        del js["ps"], js["h2"]
        return exu.unlist(js)

    def merge_nytimes(js):
        return exu.undict(js)

    if "ebola" in dtype:
        return merge_ebola(js)
    if "nytimes" in dtype:
        return merge_nytimes(js)
    return exu.undict(js)


def merge_thread(p_id, p_count, in_dir, out_dir, dtype, file_count, overwrite):

    def deal_file(in_file, out_file):
        try:
            if exists(out_file) and not overwrite:
                return False
            js = json.load(codecs.open(in_file, "r", "utf-8"))
            js = merge_field(js, dtype=dtype)
            json.dump(js, codecs.open(out_file, "w", "utf-8"))
        except Exception as e:
            logging.exception("[!] Deal file %s Failed %s", in_file, e)
            return False
        return True

    file_id = p_id
    while file_id < file_count:
        deal_file(in_dir.format(file_id), out_dir.format(file_id))
        file_id += p_count


def main():
    in_dir = '/home/zhangwm/trec/datas/ebola_full/{}.json'
    out_dir = '/home/zhangwm/trec/datas/merged_fields_ebola/{}.json'
    dtype, file_count = "ebola", du.ebola_file_count

    mp.multi_main(
        target=merge_thread,
        test_target=mp.partial(
            merge_thread, 0, 1, in_dir, out_dir, dtype, 200, True
        ),
        use_pool=True,
        in_dir=in_dir,
        out_dir=out_dir,
        dtype=dtype,
        file_count=file_count,
        overwrite=True
    )


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    main()
