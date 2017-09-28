#! /usr/bin/python

import json
import codecs


def load_news(file_name):
    xml = json.load(codecs.open(file_name, "r", "utf-8"))
    