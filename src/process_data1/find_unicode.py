#! /usr/bin/python

import codecs
import json


def get_chars(file_id):
    file_name = "./ebola_json/{}.json".format(file_id)
    body = json.load(codecs.open(file_name, "r", "utf-8"))["content"]
    metas = body["metas"]
    title = body.get("title", "")
    title = title if title is not None else ""
    st = set(title)
    for key in metas:
        st.update(metas[key])
    for tag in ["h1", "h2", "h3", "h4", "h5", "p"]:
        for item in body[tag]:
            st.update(item)
    return st


def main(file_count=194481):
    st = set()
    for i in range(file_count):
        st.update(get_chars(i))
        # print st
    codecs.open("./chars.json", "w", "utf-8").write(json.dumps(list(st)))


if __name__ == "__main__":
    main(10000)
