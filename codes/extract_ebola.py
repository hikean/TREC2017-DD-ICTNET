#! /usr/bin/python

import codecs
import json
from urllib import unquote
from lxml import etree
from io import BytesIO, StringIO
import threading
import sys
from os import listdir
from os.path import exists, isfile, isdir


tagignore = set(["link", "script", "style"])

def parse_head(tag):
    if len(tag) == 0:
        return {"metas":{}}
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

def ebola_thread(in_dir, out_dir, thread_id, thread_count, file_count=194481):
    for i in range(file_count/thread_count + 2):
        file_id = i + thread_id * file_count / thread_count;
        ebola(in_dir.format(file_id), out_dir.format(file_id))

def main(in_dir, out_dir, thread_count):
    threads = [threading.Thread(target=ebola_thread, args=(in_dir, out_dir, i, thread_count)) for i in range(thread_count)]
    for thread in threads:
        thread.start()

if __name__ == "__main__":
    in_dir = "../datas/ebola/{}.json"
    out_dir = "../datas/ebola_json/{}.json"
    print "\t".join(sys.argv)
    if len(sys.argv) == 1:
        main(in_dir, out_dir, 4)
    elif len(sys.argv) == 3:
        ebola_thread(in_dir, out_dir, int(sys.argv[1]), int(sys.argv[2]))
    else:
        print "usage:\n\tpython ebola_extract.py <process_id> <process_count>"

