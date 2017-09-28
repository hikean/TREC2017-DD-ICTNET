#! /usr/bin/python

import codecs
import logging
from os.path import exists, isfile, isdir
from os import listdir
import sys
import json
import threading

import multiprocess as mp

ALL_KEYS = [
    'content_lead_paragraph',
    'metas_correction_date',
    'metas_publication_day_of_month',
    'metas_feature_page',
    'metas_column_name',
    'metas_online_sections',
    'title',
    'metas_publication_month',
    'metas_alternate_url',
    'head',
    'content_full_text',
    'metas_series_name',
    'metas_publication_year',
    'metas_slug',
    'metas_publication_day_of_week',
    'key',
    'date',
    'metas_print_page_number',
    'metas_print_column',
    'metas_print_section',
    'metas_banner',
    'content_correction_text',
    'content_online_lead_paragraph',
    'metas_dsk',
    'classifier'
]


def unpack_dict(dct, result, name):
    for key in dct:
        result[name + key] = dct[key]
    return result


def deal_nonested_file(nyjson, nonested_file):
    if exists(nonested_file):
        return
    global ALL_KEYS
    njson = {key: "" for key in ALL_KEYS}
    njson.update({key: nyjson[key] for key in ["head", "title", "date"]})
    njson["key"] = nyjson["doc_id"]
    njson = unpack_dict(nyjson["metas"], njson, "metas_")
    njson = unpack_dict(nyjson["content"], njson, "content_")
    njson["classifier"] = ",".join(nyjson["classifier"])
    for key in ALL_KEYS:
        if key not in njson:
            njson[key]
    with codecs.open(nonested_file, "w", "utf-8") as fl:
        fl.write(json.dumps(njson))


def deal_merged_file(nyjson, merged_file):
    if exists(merged_file):
        return
    global ALL_KEYS
    njson = {key: "" for key in ALL_KEYS if not key.startswith("content")}
    njson.update({key: nyjson[key] for key in ["head", "title", "date"]})
    njson["key"] = nyjson["doc_id"]
    njson = unpack_dict(nyjson["metas"], njson, "metas_")
    njson["content"] = "\n\n\n\n".join(nyjson["content"].values())
    njson["classifier"] = u",".join(nyjson["classifier"])
    with codecs.open(merged_file, "w", "utf-8") as fl:
        fl.write(json.dumps(njson))


def deal_files(in_file, nonested_file, merged_file):
    nyjson = json.loads(codecs.open(in_file, "r", "utf-8").read())
    if nonested_file is not None:
        deal_nonested_file(nyjson, nonested_file)
    if merged_file is not None:
        deal_merged_file(nyjson, merged_file)


def statics_key(in_file):
    nyjson = json.loads(codecs.open(in_file, "r", "utf-8").read())
    return set([key for key in nyjson])


def deal_thread(thread_id, thread_count,
                file_tmplt="../datas/ny_json/{:07d}.json",
                nonested_file_tmplt="../datas/nonested/{:07d}.json",
                merged_file_tmplt="../datas/merged/{:07d}.json",
                file_count=1855658):
    # key_set = set()
    # key_file_name = "{}.json".format(thread_id)
    while thread_id < file_count:
        in_file = file_tmplt.format(thread_id)
        nonested_file = (None if nonested_file_tmplt is None else
                         nonested_file_tmplt.format(thread_id))
        merged_file = (None if merged_file_tmplt is None else
                       merged_file_tmplt.format(thread_id))
        try:
            deal_files(in_file, nonested_file, merged_file)
        except Exception as e:
            logging.exception("deal thread %s", e)
        thread_id += thread_count
        # key_set.update(statics_key(nonested_file))
    # json.dump(list(key_set), codecs.open(key_file_name, "w", "utf-8"))


if __name__ == "__main__":
    mp.multi_main(
        target=deal_thread,
        test_target=mp.partial(
            deal_thread,
            thread_id=0,
            thread_count=1,
            file_count=200
        )
    )
