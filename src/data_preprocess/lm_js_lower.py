# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/18 下午5:47
# @version: 1.0

# from basic_init import *
from src.utils.constants import *
import json
import codecs

def toLMModel():
    js = json.load(codecs.open(LMDirichlet_without_stem_raw, 'r', 'utf-8'))
    js = js['model']
    with codecs.open(LMDirichlet_without_stem, 'w', 'utf-8') as fl:
        fl.write(json.dumps(js))
def toLower():
    js = json.load(codecs.open(LMDirichlet_without_stem_raw, 'r', 'utf-8'))
    js = js['model']

    ret = {}

    for w,p in js.items():
        if ret.has_key(w.lower()):
            ret[w.lower()] += p
        else:
            ret[w.lower()] = p

    #before cnt: 456183 after cnt: 388737
    print "before cnt:", len(js.items()), "after cnt:", len(ret.items())

    with codecs.open(LMDirichlet_without_stem_lower, 'w', 'utf-8') as fl:
        fl.write(json.dumps(ret))

if __name__ == '__main__':
    # toLower()
    js = json.load(codecs.open(LMDirichlet_without_stem_raw, 'r', 'utf-8'))
    print js['avg_len']

__END__ = True