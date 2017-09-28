import codecs
import json
import logging
from os.path import exists, getsize
from urllib import unquote

import requests
from lxml import etree


def remove_tag(root, tagignore):
    for tag in root.iterchildren():
        if tag.tag in tagignore or len(str(tag.tag)) > 10:
            root.remove(tag)
        else:
            remove_tag(tag, tagignore)


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
        # logging.info("[#] exception get title, %s", e)
        pass
    try:
        title = html.get("title", "-").strip()
    except Exception as e:
        # logging.info("[#] exception get title, %s", e)
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

    def html_empty(html, root, word_limit=3):
        # if html.startswith("<?xml"):
        #     root = etree.XML(html.encode('utf-8'))
        #     return get_tag_text(root, word_limit)
        return get_tag_text(root, word_limit)

    tagignore = set([
        "link", "script", "style", "aside", "footer", "nav", "link", "br",
        "hr", "form", "input", "button", "select", "label", "option", "frame",
        "iframe", "frameset", "noframes", "img", "map", "convas", "source",
        "noscript", "param", ""
    ])
    root = etree.HTML(html.encode('utf-8'))
    remove_tag(root, tagignore)
    content = parse_head(root.xpath("//head"))
    for tag in ["h1", "h2", "h3", "h4", "h5", "a"]:
        t = [get_tag_text(node, 3) for node in root.xpath("//{}".format(tag))]
        content[tag] = [x for x in t if len(x) > 0]
    title = get_title(content)
    if title is None:
        title = ""
    content["title"] = title
    content["ps"] = [get_tag_text(tag, 6) for tag in root.xpath("//p")]
    if len(content["ps"]) < 10:
        content["ps"] = html_empty(html, root)
    return content
    # ps.append(title)
    # results = ",".join(re.findall(
    #     r"\w+", " ".join(ps).strip(), flags=re.UNICODE))
    # if len(results) < 10:
    #     results = ",".join(re.findall(
    #         r"\w+", get_tag_text(root), flags=re.UNICODE))
    # return results


def undict(js, affix=None):
    if not isinstance(js, dict):
        return js
    ret = {}
    for key in js:
        aff = unicode(key) if affix is None else affix + u"_" + unicode(key)
        if isinstance(js[key], dict):
            ret.update(undict(js[key], aff))
        else:
            ret[aff] = js[key]
    return ret


def unlist(js):
    if isinstance(js, list):
        return " ".join([i for i in js])
    elif isinstance(js, dict):
        return {key: unlist(js[key]) for key in js}
    else:
        return js


def ebola(in_file_name, out_file_name):
    if exists(out_file_name) and getsize(out_file_name) > 100:
        return
    js = json.load(codecs.open(in_file_name, "r"))
    with codecs.open(out_file_name, "w", "utf-8") as fl:
        file_id = in_file_name.split("/")[-1][:-5] + " "
        fl.write(file_id)
        fl.write(parse_html(js["content"]))


def extract_ebola(url=None, in_file=None):
    if url is None and in_file is None:
        raise ValueError("url and in_file can't both be None")
    html = None
    if in_file is not None:
        js = json.load(codecs.open(in_file, "r"))
        html = js["content"]
        result = {"key": js["key"], "url": unquote(js["url"])}
    else:
        res = requests.get(url=url)
        result = {"url": res.url}
        html = res.text
    result.update(parse_html(html))
    return result
