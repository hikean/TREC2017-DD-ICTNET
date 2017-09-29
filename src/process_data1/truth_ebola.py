# -*- encoding: utf-8 -*-

from lxml import etree


FILE_NAME = "../datas/dynamic-domain-2016-truth-data.xml"


def extract_passage_id():
    root = etree.HTML(open(FILE_NAME, "r").read())
    return set([psg.attrib.get("id", None) for psg in root.xpath("//passage")])


def main():
    result = extract_passage_id()
    print result, len(result)

if __name__ == "__main__":
    main()
