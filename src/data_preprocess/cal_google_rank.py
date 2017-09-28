# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/28 上午7:10
# @version: 1.0

'''
合并两个rank file
并且第一个的id转化成key
'''

from basic_init import *
from src.utils.constants import *

import json
import codecs




def cal(ebola_file, nyt_file, out_file):
    key2id = json.load( codecs.open(ID2KEY_FILE, 'r', 'utf-8') )
    ebola_data = json.load(codecs.open(ebola_file, 'r', 'utf-8'))
    nyt_data = json.load( codecs.open(nyt_file, 'r', 'utf-8') )

    for tid, docids in ebola_data.items():
        new_vs = []
        for did in docids:
            try:
                new_vs.append(key2id[str(did)])
            except Exception ,e:
                print "error key:", did
        ebola_data[tid] = new_vs

    ret = dict( ebola_data.items() + nyt_data.items() )

    with codecs.open(out_file, 'w',  'utf-8' ) as fobj:
        fobj.write( json.dumps( ret ) )



def cal2(ebola_file, nyt_file, out_file):
    key2id = json.load( codecs.open(ID2KEY_FILE, 'r', 'utf-8') )
    ebola_data = json.load(codecs.open(ebola_file, 'r', 'utf-8'))
    nyt_data = json.load( codecs.open(nyt_file, 'r', 'utf-8') )

    for tid, docids in ebola_data.items():
        new_vs = []
        for did in docids:
            try:
                new_vs.append(key2id[str(did)])
            except Exception ,e:
                print "error key:", did
        ebola_data[tid] = new_vs

    for tid, docids in nyt_data.items():
        new_vs = []
        for did in docids:
            try:
                new_vs.append( did[1] )
            except Exception ,e:
                print "error key:", did
        nyt_data[tid] = new_vs

    ret = dict( ebola_data.items() + nyt_data.items() )

    with codecs.open(out_file, 'w',  'utf-8' ) as fobj:
        fobj.write( json.dumps( ret ) )

def combine1():
    ebola_file = EBOLA_GOOGLE_RANK_FILE
    nyt_file = NYT_GOOGLE_RANK_FILE
    out_file = EBOLA_NYT_GOOGLE_KEY_RANK_FILE

    cal(ebola_file, nyt_file, out_file)



def combine2():
    ebola_file = EBOLA_GOOGLE_RANK_FILE
    nyt_file = NYT_GOOGLE_RANK_FILE2
    out_file = EBOLA_NYT_GOOGLE_KEY_RANK_FILE

    cal(ebola_file, nyt_file, out_file)

if __name__ == '__main__':

    pass


__END__ = True