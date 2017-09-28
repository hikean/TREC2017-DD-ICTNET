#! -*- encoding: utf-8 -*-

import codecs
# from lxml import etree
import json
import re
from collections import Counter


GRAND_TRUTH_FILE = "../../datas/ebola_truth.xml"
DATA_DIR = "../../datas/"

rtext = r'\<text\>\<!\[CDATA\[(.*)\]\]\>\</text\>'
rid = r'\<passage id="(\d+)"\>'
rno = r'\<docno\>([a-zA-Z0-9\-_]+)\</docno\>'
rrating = r'<rating\>(\d+)\</rating\>'
rtype = r'\<type\>(.*)\</type\>'

ignore = set(u"–→—’‘”“£•§…©­°´·»更◀�™‐‑多少显示详细♦‹")
uni_chars = u"ÃÂÅïÎâéèñôōöŽÉيœµط"
all_uchars = Counter()


def is_ascii(char):
    global ignore
    return ord(char) > 128 and char not in ignore


def is_all_ascii(text):
    global all_uchars
    flag = True
    for word in text.split():
        for ch in word:
            if is_ascii(ch):
                all_uchars[ch] += 1
                flag = False
    return flag

def analytics_ascii():
    ebola_words = "../../datas/ebola_words.txt"


def check_ascii(file_name):
    xml_data = codecs.open(file_name, "r", "utf-8").read()
    ids = re.findall(rid, xml_data, re.U)
    nos = re.findall(rno, xml_data, re.U)
    texts = re.findall(rtext, xml_data, re.U)
    types = re.findall(rtype, xml_data, re.U)
    ratings = re.findall(rrating, xml_data, re.U)
    passages = zip(ids, nos, types, ratings, texts)
    out_file = DATA_DIR + "ebola_truth_passages.json"
    json.dump(passages, codecs.open(out_file, "w", "utf-8"))
    ascii_count = [1 for passage in passages if not is_all_ascii(passage[-1])]
    print sum(ascii_count)
    print u"".join(all_uchars.keys())


if __name__ == "__main__":
    check_ascii(GRAND_TRUTH_FILE)
