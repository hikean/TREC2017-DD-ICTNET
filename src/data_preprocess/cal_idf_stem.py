# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/20 下午3:39
# @version: 1.0


'''
输入是胡耀康的每个文件都是dict的
'''

import json
import os
import codecs
import math

def cal_idf_dic(dir_path, out_file):
    #记录出现次数
    ret = {}
    files = os.listdir(dir_path)
    doc_cnt = 0
    for f in files:
        suffix = f[-5:]
        if not suffix == '.json':
            print "FILE ERROR:", f
            continue
        fn = os.path.join(dir_path, f)
        try:
            js = json.load(codecs.open(fn, 'r', 'utf-8'))
            js = js['words']
            for w in js.keys():
                if ret.has_key(w):
                    ret[w] += 1
                else:
                    ret[w] = 1
            doc_cnt += 1
        except:
            print "ERROR processing file:", fn

    print "doc cnt:", doc_cnt
    for k in ret.keys():
        ret[k] = math.log(1.0 * doc_cnt/ float(ret[k] + 1))

    with codecs.open(out_file, 'w', 'utf-8') as fobj:
        print "writing...."
        fobj.write( json.dumps(ret) )

def cal():
    in_dir = "/home/zhangwm/Data/subquerys/ebola_stem_json/"
    out_dir = "/home/zhangwm/Data/processed/ebola_stem_idf.json"

    cal_idf_dic(in_dir, out_dir)


def cal_polar():
    in_dir = "/home/zhangwm/trec/datas/polar_stem_json/"
    out_dir = "/home/zhangwm/Data/processed/polar_stem_idf.json"
    cal_idf_dic(in_dir, out_dir)


def test():
    out_dir = "/home/zhangwm/Data/processed/ebola_stem_idf.json"
    c = json.load( codecs.open(out_dir, 'r', 'utf-8') )
    cnt = 0
    for k, v in c.items():
        print k,v,type(k)
        cnt += 1
        if cnt >= 10: break


def cal_ebola_idf_without_stem():
    in_dir = "/home/zhangwm/trec/datas/ebola_words_json/"
    out_dir = "/home/zhangwm/Data/processed/ebola_withoutstem_idf.json"

    cal_idf_dic(in_dir, out_dir)


def cal_nyt_idf_without_stem():
    in_dir = "/home/zhangwm/trec/datas/ny_words_json/"
    out_dir = "/home/zhangwm/Data/processed/nyt_withoutstem_idf.json"

    cal_idf_dic(in_dir, out_dir)


def cal_nyt_idf_stem():
    #/home/zhangwm/trec/datas/ny_stem_json
    in_dir = "/home/zhangwm/trec/datas/ny_stem_json/"
    out_dir = "/home/zhangwm/Data/processed/nyt_stem_idf.json"

    cal_idf_dic(in_dir, out_dir)


if __name__ == '__main__':
    # test()
    # cal_polar()
    # cal_ebola_idf_without_stem()
    # cal_nyt_idf_without_stem()
    cal_nyt_idf_stem()

__END__ = True