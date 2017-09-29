#! /usr/bin/python

import codecs
import json
from urllib import unquote
from lxml import etree
# from io import BytesIO, StringIO
import threading
import sys
# from os import listdir
from os.path import exists


import multiprocess as mp

def ebola(in_file_name, out_file_name):
    tagignore = set([
        "link", "script", "style", "aside", "footer", "nav", "link", "br",
        "hr", "form", "input", "button", "select", "label", "option", "frame",
        "iframe", "frameset", "noframes", "img", "map", "convas", "source",
        "noscript", "param", ""])

    def remove_tag(root):
        for tag in root.iterchildren():
            if tag.tag in tagignore or len(str(tag.tag)) > 8:
                root.remove(tag)
            else:
                remove_tag(tag)
        return root

    def parse_head(tag):
        if len(tag) == 0:
            return {"metas": {}}
        head, metas = {"title": ""}, {}
        for child in tag[0].iterchildren():
            if child.tag == "title":
                head["title"] = child.text
            elif child.tag == "meta":
                if "name" in child.attrib:
                    metas[child.attrib["name"]] = (
                        child.attrib.get("content", ""))
                elif "property" in child.attrib:
                    prop = child.attrib["property"]
                    if "og:" in prop:
                        metas[prop[3:]] = child.attrib.get("content", "")
        if "title" in metas:
            head["title"] = metas["title"]
        if "|" in head["title"]:
            head["title"] = head["title"].split("|")[0]
        head["metas"] = metas
        return head

    def get_tag_text(tag, word_limit=2):
        texts = [
            txt.strip() for txt in tag.itertext()
            if txt.strip().count(" ") > word_limit]
        return " \n ".join(texts)

    def parse_html(html):
        root = remove_tag(etree.HTML(html.encode('utf-8')))
        content = parse_head(root.xpath("//head"))
        for tag in ["p", "h1", "h2", "h3", "h4", "h5", "a"]:
            word_limit = 5 if tag == "p" else 1
            texts = [
                get_tag_text(node, word_limit)
                for node in root.xpath("//{}".format(tag))]
            content[tag] = [txt for txt in texts if len(txt) > 0]
        return content

    if exists(out_file_name):
        return
    js = json.load(codecs.open(in_file_name, "r"))
    js["content"] = parse_html(js["content"])
    js["url"] = unquote(js["url"])
    with codecs.open(out_file_name, "w", "utf-8") as fl:
            fl.write(json.dumps(js))


def ebola_thread(thread_id, thread_count, in_dir, out_dir, file_count=194481):
    for i in range(file_count / thread_count + 2):
        file_id = i + thread_id * file_count / thread_count
        try:
            ebola(in_dir.format(file_id), out_dir.format(file_id))
        except Exception as e:
            print e, file_id


if __name__ == "__main__":
    in_dir = "../datas/ebola/{}.json"
    out_dir = "../datas/ebola_clean/{}.json"
    mp.multi_main(
        target=ebola_thread,
        test_target=mp.partial(
            ebola_thread, 0, 1, in_dir, out_dir, file_count=1000
        ),
        in_dir=in_dir,
        out_dir=out_dir
    )
