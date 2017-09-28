#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
import sys

import extract_utils as exu
import multiprocess as mp
from os.path import exists


def deal_thread(
        process_id, process_count, in_dir, out_dir, file_count=200,
        overwirte=False):
    file_id = process_id
    while file_id < file_count:
        in_file, out_file = in_dir.format(file_id), out_dir.format(file_id)
        file_id += process_count
        if exists(out_file) and not overwirte:
            continue
        try:
            json.dump(
                exu.extract_ebola(in_file=in_file),
                codecs.open(out_file, "w", "utf-8")
            )
        except Exception as e:
            logging.info("[#] Deal File: %s Error, %s", file_id, e)


def main(argv=sys.argv):
    logging.root.setLevel(logging.INFO)
    in_dir = "../../datas/ebola/{}.json"
    out_dir = "../../datas/ebola_full/{}.json"
    mp.multi_main(
        target=deal_thread,
        test_target=mp.partial(
            deal_thread, 0, 1, in_dir, out_dir
        ),
        use_pool=True,
        argv=argv,
        in_dir=in_dir,
        out_dir=out_dir,
        file_count=194481
    )


if __name__ == "__main__":
    main()
