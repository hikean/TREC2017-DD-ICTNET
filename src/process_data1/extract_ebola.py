#! /usr/bin/python

import codecs
import json
import sys
from os import listdir
from os.path import exists, isdir, isfile
from urllib import unquote

import multiprocess as mp
from io import BytesIO, StringIO
from lxml import etree

tagignore = set(["link", "script", "style"])


def parse_head(tag):
    if len(tag) == 0:
        return {"metas": {}}
    head, metas = {}, {}
    for child in tag[0].iterchildren():
        if child.tag == "title":
            head["title"] = child.text
        elif child.tag == "meta":
            if "name" in child.attrib:
                metas[child.attrib["name"]] = child.attrib.get("content", "")
            elif "property" in child.attrib:
                prop = child.attrib["property"]
                if "og:" in prop:
                    metas[prop[3:]] = child.attrib.get("content", "")
    if "title" not in head and "title" in metas:
        head["title"] = metas["title"]
    head["metas"] = metas
    return head


def parse_html(html):
    def get_tag_text(tags):
        return ["\n".join([txt for txt in tag.itertext()]) for tag in tags]
    root = etree.HTML(html.encode('utf-8'))
    content = parse_head(root.xpath("//head"))
    for tag in ["p", "h1", "h2", "h3", "h4", "h5"]:
        content[tag] = get_tag_text(root.xpath("//{}".format(tag)))
    return content


def ebola(in_file_name, out_file_name):
    if exists(out_file_name):
        return
    js = json.load(codecs.open(in_file_name, "r"))
    js["content"] = parse_html(js["content"])
    js["url"] = unquote(js["url"])
    with codecs.open(out_file_name, "w", "utf-8") as fl:
            fl.write(json.dumps(js))


def ebola_thread(thread_id, thread_count, in_dir, out_dir, file_count=194481):
    file_id = thread_id
    while file_id < file_count:
        ebola(in_dir.format(file_id), out_dir.format(file_id))
        file_id += thread_count


if __name__ == "__main__":
    in_dir = "../datas/ebola/{}.json"
    out_dir = "../datas/ebola_json/{}.json"
    mp.multi_main(
        target=ebola_thread,
        test_target=mp.partial(
            ebola_thread, thread_id=0, thread_count=1, in_dir=in_dir,
            out_dir=out_dir, file_count=200
        ),
        in_dir=in_dir,
        out_dir=out_dir
    )
