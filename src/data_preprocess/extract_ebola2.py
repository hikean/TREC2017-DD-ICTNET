#! /usr/bin/python

import codecs
import json
from lxml import etree
import re
from os.path import exists, getsize
import multiprocess as mp

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


def get_title(html):
    try:
        title = html["metas"]["title"].strip()
        if len(title) > 3:
            return title
    except Exception as e:
        print e
    try:
        title = html.get("title", "-").strip()
    except Exception as e:
        print e
        title = "-"
    for tag in ["h2", "h3", "h1"]:
        if len(html.get(tag, [])) == 1 and title == "":
            return html.get(tag)[0]
        for value in html[tag]:
            value = value.strip()
            if value in title:
                return value
    return title.split("-")[0].strip()


def parse_html(html):
    def get_tag_text(tag, word_limit=3):
        texts = [txt.strip() for txt in tag.itertext() if len(
            txt.strip().split(" ")) >= word_limit]
        return " ".join(texts)
    root = etree.HTML(html.encode('utf-8'))
    remove_tag(root)
    content = parse_head(root.xpath("//head"))
    for tag in ["h1", "h2", "h3", "h4", "h5"]:
        content[tag] = [get_tag_text(node, 3)
                        for node in root.xpath("//{}".format(tag))]
    title = get_title(content)
    if title is None:
        title = ""
    ps = [get_tag_text(tag, 6) for tag in root.xpath("//p")]
    ps.append(title)
    results = ",".join(re.findall(
        r"\w+", " ".join(ps).strip(), flags=re.UNICODE))
    if len(results) < 10:
        results = ",".join(re.findall(
            r"\w+", get_tag_text(root), flags=re.UNICODE))
    return results


def ebola(in_file_name, out_file_name):
    if exists(out_file_name) and getsize(out_file_name) > 100:
        return
    js = json.load(codecs.open(in_file_name, "r"))
    with codecs.open(out_file_name, "w", "utf-8") as fl:
        file_id = in_file_name.split("/")[-1][:-5] + " "
        fl.write(file_id)
        fl.write(parse_html(js["content"]))


def ebola_thread(thread_id, thread_count, in_dir, out_dir, file_count=194481):
    file_id = thread_id
    while file_id < file_count:
        ebola(in_dir.format(file_id), out_dir.format(file_id))
        file_id += thread_count


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
