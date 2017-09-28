#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
# import multiprocess as mp


def deal(in_dir, out_dir, file_count=194481):
    key2id, id2key = {}, {}
    for i in range(file_count):
        try:
            text = codecs.open(in_dir.format(i), "r", "utf-8").read()
            js = json.loads(text)[0]
            key2id[js["key"]] = i
            id2key[i] = js["key"]
        except Exception as e:
            logging.info("[#] %s, %s", i, e)
            id2key[i] = ""

    json.dump(key2id, codecs.open(out_dir.format("key2id"), "w", "utf-8"))
    json.dump(id2key, codecs.open(out_dir.format("id2key"), "w", "utf-8"))


def main():
    in_dir = "/home/zhangwm/Data/ebola_full/ebola_htmls/{}.json"
    out_dir = "/home/zhangwm/Data/ebola_full/{}.json"
    deal(in_dir=in_dir, out_dir=out_dir)


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    main()
