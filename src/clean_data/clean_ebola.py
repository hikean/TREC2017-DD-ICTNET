#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import logging
from os.path import exists
from collections import Counter
import sys
from lxml import etree
import multiprocess as mp

sys.path.append("../utils")

import data_utils as du


tagignore = set(
    ["link", "script", "style", "aside", "footer", "nav", "link", "br", "hr",
     "form", "input", "button", "select", "label", "option", "frame",
     "iframe", "frameset", "noframes", "img", "map", "convas", "source",
     "noscript", "param", ""]
)


def remove_tag(root):
    global tagignore
    for tag in root.iterchildren():
        if tag.tag in tagignore or len(str(tag.tag)) > 10:
            root.remove(tag)
        else:
            remove_tag(tag)


def get_tags(root, st):
    st.add(root.tag)
    for child in root.iterchildren():
        st.add(child.tag)
        get_tags(child, st)


def parse_html(html):
    def html_empty(html, root, word_limit=3):
        if html.startswith("<?xml"):
            root = etree.XML(html)
            return get_tag_text(root, word_limit)
        return get_tag_text(root, word_limit)

    def get_tag_text(tag, word_limit=3):
        texts = [txt.strip() for txt in tag.itertext() if len(
            txt.strip().split(" ")) >= word_limit]
        return " ".join(texts)
    root = etree.HTML(html.encode('utf-8'))
    remove_tag(root)
    ps = [get_tag_text(tag, 6) for tag in root.xpath("//p")]
    ret = " ".join(ps)
    if len(ret) < 10:
        ret = ret + " " + html_empty(html=html, root=root)
    return ret


def deal_ebola(
        file_id, in_dir, out_dir, json_dir, stem_dir, stem_jsdir,
        overwrite=True):

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
    logging.info("[#] deal file_id: %s", file_id)
    if (exists(out_file) and not overwrite and exists(stem_file) and
            exists(json_file) and exists(stem_json)):
        return False
    logging.info("[#] dealing file_id: %s", file_id)
    js = json.load(codecs.open(in_file, "r", "utf-8"))
    text = parse_html(js["content"])
    words = du.basic_preprocess(text, length_limit=1)
    doc_dict = {
        "words": Counter(words),
        "id": file_id,
        "key": js["key"]
    }
    stem_words = du.stemmer_by_porter(words)
    if not exists(json_file) or overwrite:
        json.dump(doc_dict, codecs.open(json_file, "w", "utf-8"))
    if not exists(out_file) or overwrite:
        write_line_data(out_file, js["key"], words)
    if not exists(stem_file) or overwrite:
        write_line_data(stem_file, js["key"], stem_words)
    if not exists(stem_json) or overwrite:
        doc_dict["words"] = Counter(stem_words)
        json.dump(doc_dict, codecs.open(stem_json, "w", "utf-8"))
    return True


def deal_thread(
        thread_id, thread_count, in_dir, out_dir, json_dir, stem_dir,
        stem_jsdir, file_count=194481):
    file_id = thread_id
    while file_id < file_count:
        try:
            deal_ebola(
                file_id, in_dir, out_dir, json_dir, stem_dir, stem_jsdir)
        except Exception as e:
            logging.exception("[!][%s] Exception: %s", file_id, e)
        file_id += thread_count


def main():
    out_base_dir = "../../datas/"
    in_dir = "../../datas/ebola/{}.json"
    out_dir = out_base_dir + "ebola_words/{}.txt"
    json_dir = out_base_dir + "ebola_words_json/{}.json"
    stem_dir = out_base_dir + "ebola_stem/{}.txt"
    stem_jsdir = out_base_dir + "ebola_stem_json/{}.json"
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
