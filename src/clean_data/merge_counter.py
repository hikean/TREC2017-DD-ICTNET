#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
# from os.path import exists
from collections import Counter
import sys
# from lxml import etree
# import multiprocess as mp


def merge_counter(in_dir, out_file, file_count):
    ct = Counter()
    cnt = 0
    for i in range(file_count):
        js = json.load(codecs.open(in_dir.format(i), "r", "utf-8"))
        ct.update(Counter(js["counter"]))
        cnt += js["count"]
    wsum = sum(ct.values())
    json.dump(
        {
            "avg_len": wsum / float(cnt),
            "count": cnt,
            "counter": ct,
            "model": {
                key: (ct[key] + 1.0) / (float(wsum) + 1.0) for key in ct
            }
        },
        codecs.open(out_file, "w", "utf-8")
    )


def main():
    logging.root.setLevel(logging.INFO)
    import multi_merge as mm
    # python merge_counter.py 'ebola_words_{}.m.json' ebola_words.lm.json 16
    base_dir = "../../datas/LangModel/"
    if len(sys.argv) != 4:
        print((
            "Usage:\n" +
            "\tpython {0} <in_data_type> <out_file> <process_count>\n" +
            "\n\teg:\n\t  python ebola_words ebola_words2 16\n" +
            "\t  python {0} ebola_words ebola_words_2 16\n" +
            "\t  python {0} ebola_stem ebola_stem 16\n" +
            "\t  python {0} ny_words ny_words 16\n" +
            "\t  python {0} ny_stem ny_stem 16\n"
        ).format(sys.argv[0]))
    else:
        data_type = sys.argv[1]
        in_dir = base_dir + "tmp/" + data_type + "_{}.m.json"
        out_file = base_dir + sys.argv[2] + ".lm.json"
        file_count = int(sys.argv[3])
        argv = ["multi_merge.py", "process", str(file_count)]
        print argv
        mm.main(data_type=data_type, argv=argv)
        merge_counter(in_dir, out_file, file_count)


if __name__ == "__main__":
    main()
