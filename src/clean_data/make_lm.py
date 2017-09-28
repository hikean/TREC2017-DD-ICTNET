# -*- encoding: utf-8 -*-

import json
import codecs
from collections import Counter


DATA_DIR = "/home/zhangwm/trec/data/"


def make_model(in_file, out_name, ignorecase=False):
    counter = Counter()
    with codecs.open(in_file, "r", "utf-8") as fl:
        for line in fl.readlines():
            words = line.strip().split(" ")
            if len(words) < 2:
                continue
            else:
                for word in words[1].strip().split(","):
                    if ignorecase:
                        word = word.lower()
                    counter[word] += 1
            print words[0]
    with codecs.open(out_name, "w", "utf-8") as fl:
        fl.write(json.dumps(counter))


def split_words_file(in_file, out_dir):
    with codecs.open(in_file, "r", "utf-8") as fl:
        for line in fl.readlines():
            words = line.strip().split(" ")
            if len(words[0]) < 1:
                continue
            out_file = out_dir + words[0] + ".json"
            print words[0]
            with codecs.open(out_file, "w", "utf-8") as fl:
                words = [] if len(words) == 1 else words[1].strip().split(",")
                fl.write(json.dumps(words))

def smain():
    in_file = DATA_DIR + "ebola_words.txt"
    out_dir = DATA_DIR + "wordsjson/"
    split_words_file(in_file, out_dir)


def main():
    in_file = DATA_DIR + "ebola_words.txt"
    out_file = DATA_DIR + "ebola_lm_i.json"
    make_model(in_file, out_file, True)


if __name__ == "__main__":
    main()
