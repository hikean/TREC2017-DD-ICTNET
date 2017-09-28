#! /usr/bin/python

import codecs
import json
import logging
import xml.dom.minidom
from lxml import etree


from os.path import exists, isfile, isdir
from os import listdir
import sys
from elasticsearch import Elasticsearch

def get_json_file_name(file_name):
    return "../datas/ny_json/" + file_name.replace("xml", "json").split("/")[-1]

def parse_xml(file_name):
    dom = xml.dom.minidom.parse(file_name)
    root = dom.documentElement
    result = {}
    result["change_date_time"] = root.attributes["change.date"].value + " " + root.attributes["change.time"].value
    head = root.getElementsByTagName("head")[0]
    body = root.getElementsByTagName("body")[0]
    title = head.getElementsByTagName("title")
    result["title"] = title[0].firstChild.wholeText if len(title) > 0 else ""
    metas = { meta.attributes["name"].value:meta.attributes["content"].value for meta in head.getElementsByTagName("meta")}
    for key in ["dsk", "online_sections", "publication_day_of_week", "slug"]:
        if key in metas:
            result[key] = metas[key]
    try:
        result["publication_date"] = "{:04d}-{:02d}-{:02d}".format(int(metas["publication_year"]),
            int(metas["publication_month"]), int(metas["publication_day_of_month"]))
    except:
        result["publication_date"] = "-".join(file_name.split("/")[:3])
    try:
        result["print_location"] = "{}-{}-{}".format(metas["print_page_number"], 
            metas["print_section"], metas["print_column"])
    except:
        result["print_location"] = ""
    docdata = head.getElementsByTagName("docdata")[0]
    try:
        result["doc_id"] = docdata.getElementsByTagName("doc-id")[0].attributes["id-string"].value
    except:
        result["doc_id"] = file_name.split("/")[-1].split(".")[0]
    try:
        result["holder"] = docdata.getElementsByTagName("doc.copyright")[0].attributes["holder"].value
    except:
        result["holder"] = ""
    result["other_descriptor"], result["taxonomic_classifier"], result["types_of_material"] = [], [], []
    result["indexing_service"] = []
    # result["org"], result["person"], result["location"] = [], [], [], []
    id_content = docdata.getElementsByTagName("identified-content")[0]
    for name in ["org", "person", "location"]:
        result[name] = []
        for node in id_content.getElementsByTagName(name):
            try:
                result[name].append(node.firstChild.wholeText)
            except:
                pass
    for classifier in id_content.getElementsByTagName("classifier"):
        if not classifier.hasAttribute("class") or not classifier.hasChildNodes():
            continue
        node_class = classifier.attributes["class"].value
        text = classifier.firstChild.wholeText
        if node_class == "indexing_service":
            result["indexing_service"].append(text)
        elif node_class == "online_producer":
            node_type = classifier.attributes["type"].value
            if node_type in result:
                result[node_type].append(text)
            else:
                result["other_descriptor"].append(text)
    try:
        result["hedline"] = body.getElementsByTagName("body.head")[0].childNodes[1].childNodes[1].firstChild.wholeText
    except:
        result["hedline"] = ""
    result["lead_paragraph"] = result["full_text"] = ""
    for block in body.getElementsByTagName("body.content")[0].getElementsByTagName("block"):
        if block.hasAttribute("class"):
            result[block.attributes["class"].value] = "\n".join([p.firstChild.wholeText 
                for p in block.getElementsByTagName("p") if p.hasChildNodes()])
    return result


def parse_xml2(file_name):
    def get_tags_text(tags):
        return ["\n".join([txt.strip() for txt in tag.itertext()]) for tag in tags]

    def get_block_dict(blocks):
        return {block.attrib.get("class", "text"): "\n".join([txt.strip() for txt in block.itertext()])
            for block in blocks}

    def get_title():
        try:
            return root.xpath("//head/title")[0].text
        except: pass
        try:
            return get_tags_text(root.xpath("//hedline")[0].getchildren())[0]
        except: pass
        return ""

    def get_date():
        try:
            date = root.xpath("//pubdata")[0].attrib.get("date.publication", None)[:8]
            return "{}-{}-{}".format(date[:4], date[4:6], date[6:8])
        except:
            return "{0[0]:04d}-{0[1]:02d}-{0[2]:02d}".format([
                int(metas.get(key, 0)) for key in 
                ["publication_year", "publication_month", "publication_day_of_month"]])

    with open(file_name, "r") as fl:
        root = etree.XML(fl.read())
    metas = {meta.attrib.get("name"): meta.attrib.get("content", "") 
                for meta in root.xpath("//meta") if "name" in meta.attrib and "content" in meta.attrib}
    result = {"head": get_tags_text(root.xpath("//body.head"))[0]}
    result["content"] = get_block_dict(root.xpath("//body.content/block"))
    result["title"] = get_title()
    result["doc_id"] = file_name.split("/")[-1][:-4]
    result["date"] = get_date()
    result["metas"] = metas
    result["classifier"] = get_tags_text(root.xpath("//classifier"))
    return result

FILE_COUNTER = 0
def main(file_dir):
    global FILE_COUNTER
    if not isdir(file_dir):
        return
    for file in listdir(file_dir):
        file_path = file_dir + "/" + file
        if isfile(file_path) and ".xml" in file_path:
            try:
                json_file_name = get_json_file_name(file_path)
                if exists(json_file_name):
                    continue
                result = parse_xml2(file_path)
                with codecs.open(json_file_name, "w", "utf-8") as fl:
                    fl.write(json.dumps(result))
                logging.info("%s done")
                FILE_COUNTER += 1
                if FILE_COUNTER % 100 == 0:
                    print "File Counter:", FILE_COUNTER
            except Exception as e:
                logging.exception("Exception: %s %s", file_path, e)
        elif isdir(file_path):
            main(file_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: extract.py <file_dir>"
    else:
        main(sys.argv[1])

