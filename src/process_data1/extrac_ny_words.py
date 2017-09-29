#!/usr/bin/python
# -*- encoding: utf-8 -*-


import logging
import codecs
import re
import json

import multiprocess as mp


def deal_news(json_news):
    if "full_text" in json_news["content"]:
        text = ([json_news.get("title", ""),
                json_news["content"]["full_text"]] +
                json_news["classifier"])
    else:
        text = ([json_news.get("title", ""),
                " ".join(json_news["content"].values())] +
                json_news["classifier"])
    text = " ".join(text)
    return re.findall(r"\w+", text)


def deal_thread(thread_id, thread_count, in_dir, out_dir, file_count):
    out_file = codecs.open(out_dir.format(thread_id), "w", "utf-8")
    file_id = thread_id
    while file_id < file_count:
        try:
            js = json.load(codecs.open(in_dir.format(file_id), "r", "utf-8"))
        except Exception as e:
            logging.exception(
                "[!] <{}> <{}>: {}".format(thread_id, file_id, e)
            )

        words = deal_news(js)
        out_file.write(str(file_id))
        out_file.write(" ")
        out_file.write(",".join(words))
        out_file.write("\n")
        file_id += thread_count
    out_file.close()


if __name__ == "__main__":
    in_dir = "../datas/ny_json/{:07d}.json"
    out_dir = "../datas/ny_words/ny_words_{}.txt"
    mp.multi_main(
        target=deal_thread,
        test_target=mp.partial(
            deal_thread, 0, 1, in_dir=in_dir, out_dir=out_dir, file_count=200
        ),
        in_dir=in_dir,
        out_dir=out_dir,
        file_count=1855658
    )
