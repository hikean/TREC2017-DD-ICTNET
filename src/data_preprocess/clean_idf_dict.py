# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/26 下午1:12
# @version: 1.0


'''
去除掉ebola和nyt idf dict不能utf-8的
'''

from basic_init import *

import json
import codecs
from src.utils.constants import *


def clean_idf_dict(dict_path, out_file):
    idf_dict = json.load(codecs.open(dict_path, 'r', 'utf-8'))
    print "tot word BEFORE to str cnt:", len(idf_dict.items())
    err_cnt = 0
    for k in idf_dict.keys():
        v = idf_dict[k]
        idf_dict.pop(k)
        try:
            k = str(k)
            idf_dict[k] = v
        except:
            err_cnt += 1
        # print "UNICODE TO STR ERR:", k
    print "UNICODE TO STR ERR CNT:", err_cnt
    print "tot word after to str cnt:", len(idf_dict.items())


    with codecs.open(out_file, 'w', 'utf-8') as fobj:
        fobj.write( json.dumps( idf_dict ) )


def cal_nyt_stem():
    in_file = nyt_idf_idf_dic_nostem
    out_file = nyt_idf_idf_dic_nostem_clean
    clean_idf_dict(in_file, out_file)

def cal_nyt_none_steam():
    in_file = nyt_idf_idf_dic_stem
    out_file = nyt_idf_idf_dic_stem_clean
    clean_idf_dict(in_file, out_file)


def cal_ebola_stem():
    in_path = STEM_IDF_DICT_EBOLA
    out_path =STEM_IDF_DICT_EBOLA_CLEAN
    clean_idf_dict(in_path, out_path)


def cal_ebola_nostem():
    in_path = idf_dic_path
    out_path =ebola_nostem_idf_dic_path_clean
    clean_idf_dict(in_path, out_path)

if __name__ == '__main__':

    # cal_nyt_none_steam()
    # cal_nyt_stem()

    # cal_ebola_stem()
    cal_ebola_nostem()


__END__ = True