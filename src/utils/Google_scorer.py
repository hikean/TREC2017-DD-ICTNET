# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/27 下午4:21
# @version: 1.0

from basic_init import *

import json
import codecs
from src.utils.constants import *
import copy

class Google_scorer(object):
    def __init__(self, js_file, a = 0.5):
        self.data = json.load(codecs.open(js_file, 'r', 'utf-8'))
        self.a = a
        self.doc_info = {}
        for tid, keys in self.data.items():
            self.doc_info[tid] = {}
            for i,r in enumerate(keys):
                self.doc_info[tid][r] = i

    def get_rank_by_tid_key(self, tid, key):
        if self.doc_info.has_key(tid) and self.doc_info[tid].has_key(key):
            return self.doc_info[tid][key]
        else:
            return None
    def cal_score(self,  rank, a = 0.5, b = 10):
        return float(b) / float(1 + a * rank)

    def get_score_by_tid_key(self, tid, key, b=1.0):

        rank = self.get_rank_by_tid_key(tid, key)
        if rank is None:
            return None
        else:
            return self.cal_score( rank, self.a, b)


# class Google_scorer_v1(object):


#
# def add_google_score_and_rerank(doc_list, google_scorer, tid, a = 0.5):
#     '''
#
#     :param doc_list: [ d, xquad score, rel_score, div_score格式]
#     :param google_scorer:
#     :return: [ d, xquad score + google_score, rel_score, div_score格式, google score]
#     '''
#     ret = []
#     for d in doc_list:
#         rank = google_scorer.get_rank_by_tid_key(tid, d[0][KEY])
#         if rank is not None:
#             gscore = google_scorer.cal_score(rank, a)
#         else:
#             gscore = 0
#         d[1] += gscore
#         ret.append( d + [gscore] )
#
#     return ret


def irsys_doclist_add_google_score_and_rerank(doc_list, google_scorer, tid, b = 1.0):
    '''
    针对irsys返回形式的doc_list修改分数，注意是deepcopy的，方式出问题
    :param doc_list: [ d, xquad score, rel_score, div_score格式]
    :param google_scorer:
    :return: [ d, xquad score + google_score, rel_score, div_score格式, google score]
    '''
    doc_list = copy.deepcopy(doc_list)
    for i,d in enumerate(doc_list):
        gscore = google_scorer.get_score_by_tid_key(tid, d[0], b)
        if gscore is None:
            gscore = 0

        doc_list[i][1][0] += gscore
        doc_list[i][1][1].append(gscore)

    return sorted(doc_list, reverse=True, key = lambda d:d[1][0])


def xquad_doclist_add_google_score_and_rerank(doc_list, google_scorer, tid, b=1.0):
    doc_list = copy.deepcopy(doc_list)
    for i,d in enumerate(doc_list):
        gscore = google_scorer.get_score_by_tid_key(tid, d[0][KEY], b)
        if gscore is None:
            gscore = 0
        # print "CHECK BEFORE ADD:", doc_list[i][1:]
        doc_list[i][1] += gscore

        doc_list[i].append( gscore )
        # print "CHECK AFTER ADD:", doc_list[i][1:]

    return sorted(doc_list, reverse=True, key = lambda d:d[1])

if __name__ == '__main__':


    pass

__END__ = True