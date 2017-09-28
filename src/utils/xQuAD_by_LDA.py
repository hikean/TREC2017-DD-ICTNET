# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/4 下午9:31
# @version: 1.0


'''
符号统一:
t和qi认为是同一个东西
D和S认为是一个东西，都是已经检索到的相关文档
Tq和Q认为是一个东西，都是qi的集合

P(t|q)的几种算法参考xQuAD的论文：
(1)P(t|q)c 这种简单先用着

===

几种


算法改成 rel_score + diverstiy score

diverstiy score用LDA去计算，于是lmd这个参数调整就有点麻烦了...

为了防止后面div那一项太大，可以



'''

import copy
import math
from constants import *

class xQuAD_LDA(object):
    def __init__(self, key_Lda_feat_dic, topic_cnt, rel_topic_cnt=1, lmd=0.5):
        '''
        :param key_Lda_feat_dic:
        :param topic_cnt:
        :param rel_topic_cnt: 根据选举席位算法选出topX的 先按照1来写
        '''
        self.topic_cnt = topic_cnt
        self.key_feat_dic = key_Lda_feat_dic
        self.rel_topic_cnt = rel_topic_cnt
        self.lmd = lmd

    def select_doc_u(self, R_left, already_selected_keys=set(), key_lda_feat_dict={}, query_key='query'):
        score_list = []  # [d, tot_score, solr_score, xQuAD_LDA_score,]
        for d in R_left:
            rel_score = d[1][0]
            div_score = 0.0
            doc_key = d[1][2][KEY]

            for i_topic in range(self.topic_cnt):
                #TODO: 这里需要考虑一下修改，比如P(qi|q)这一项直接去掉...或者变成常数
                if not key_lda_feat_dict[query_key].has_key(i_topic) or not key_lda_feat_dict[doc_key].has_key(i_topic):
                    continue
                div_with_s = 1.0
                for s_key in already_selected_keys:
                    # print key_lda_feat_dict[s_key]
                    if key_lda_feat_dict[s_key].has_key(i_topic):
                        div_with_s *= 1.0 - key_lda_feat_dict[s_key][i_topic]

                # 这部分需要考虑下加不加或者修改
                div_score += key_lda_feat_dict[query_key][i_topic] * key_lda_feat_dict[doc_key][i_topic] * div_with_s
                import math
                #TODO:CHECK
                div_score = math.log(1.0 + div_score)
            score_list.append( [d[1][2], rel_score + self.lmd * div_score, rel_score, div_score] )
        score_list = sorted( score_list, reverse=True, key= lambda d:d[1])
        return score_list

    def select_doc_u_log(self, R_left, already_selected_keys=set(), key_lda_feat_dict={}, query_key='query'):
        score_list = []  # [d, tot_score, solr_score, xQuAD_LDA_score,]
        for d in R_left:
            rel_score = d[1][0]
            div_score = 0.0
            doc_key = d[1][2][KEY]

            for i_topic in range(self.topic_cnt):
                #TODO: 这里需要考虑一下修改，比如P(qi|q)这一项直接去掉...或者变成常数
                if not key_lda_feat_dict[query_key].has_key(i_topic) or not key_lda_feat_dict[doc_key].has_key(i_topic):
                    continue
                div_with_s = 1.0
                for s_key in already_selected_keys:
                    # print key_lda_feat_dict[s_key]
                    if key_lda_feat_dict[s_key].has_key(i_topic):
                        div_with_s *= 1.0 - key_lda_feat_dict[s_key][i_topic]

                # 这部分需要考虑下加不加或者修改
                div_score += key_lda_feat_dict[query_key][i_topic] * key_lda_feat_dict[doc_key][i_topic] * div_with_s
                import math
                #TODO:CHECK
                div_score = math.log(1.0 + div_score)
            score_list.append( [d[1][2], rel_score + self.lmd * div_score, rel_score, div_score] )
        score_list = sorted( score_list, reverse=True, key= lambda d:d[1])
        return score_list

    def select_doc_u_log_weak_rel_score(self, R_left, already_selected_keys=set(), key_lda_feat_dict={}, query_key='query', top = 30):
        R_left = R_left[0:top]
        score_list = []  # [d, tot_score, solr_score, xQuAD_LDA_score,]
        for d in R_left:
            rel_score = d[1][0]
            div_score = 0.0
            doc_key = d[1][2][KEY]

            for i_topic in range(self.topic_cnt):
                #TODO: 这里需要考虑一下修改，比如P(qi|q)这一项直接去掉...或者变成常数
                if not key_lda_feat_dict[query_key].has_key(i_topic) or not key_lda_feat_dict[doc_key].has_key(i_topic):
                    continue
                div_with_s = 1.0
                for s_key in already_selected_keys:
                    # print key_lda_feat_dict[s_key]
                    if key_lda_feat_dict[s_key].has_key(i_topic):
                        div_with_s *= 1.0 - key_lda_feat_dict[s_key][i_topic]

                # 这部分需要考虑下加不加或者修改
                div_score += key_lda_feat_dict[query_key][i_topic] * key_lda_feat_dict[doc_key][i_topic] * div_with_s
                import math
                #TODO:CHECK
                div_score = math.log(1.0 + div_score)
            score_list.append( [d[1][2], rel_score + self.lmd * div_score, rel_score, div_score] )
        score_list = sorted( score_list, reverse=True, key= lambda d:d[1])
        return score_list



class HxQuAD(object):
    def __init__(self):
        pass


if __name__ == '__main__':
    pass

__END__ = True