# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/27 下午10:25
# @version: 1.0

'''
根据共现次数来确定阈值 过滤subquery
'''

import json
import codecs
from src.utils.constants import *

def filter_subquery(in_file, out_file, filter_cnt= 5):
    data = json.load(codecs.open(in_file, 'r', 'utf-8'))
    ret = {}
    for tid, vs in data.items():
        ret[tid] = []
        for v in vs:
            if v[1] >= filter_cnt:
                ret[tid].append(v[0])

    with codecs.open(out_file, 'w', 'utf-8') as fobj:
        print "writing...", out_file
        fobj.write( json.dumps(ret) )
    return ret


def cal_ebola_filter_subquery():
    ebola_v1 = GOOGLE_SUGGESTED_EBOLA_WITH_CNT
    for fc in range(2, 20):
        out_file =  "/home/zhangwm/trec/datas/filter_suggestion/ebola-merge_filter_%d.json" % fc
        filter_subquery(ebola_v1, out_file, fc)

def cal_nyt_filter_subquery():
    nyt_v1 = GOOGLE_SUGGESTED_NYT_WITH_CNT
    for fc in range(2, 20):
        out_file =  "/home/zhangwm/trec/datas/filter_suggestion/nytimes-merge_filter_%d.json" % fc
        filter_subquery(nyt_v1, out_file, fc)

if __name__ == '__main__':
    cal_ebola_filter_subquery()
    cal_nyt_filter_subquery()

__END__ = True