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



'''

import copy
import math
from constants import *
from collections import Counter
import math

def cos_dis(a,b):
    ca = Counter(a)
    cb = Counter(b)
    key_set = set(ca.keys()) & set(cb.keys())

    zi = 0
    for k in key_set:
        zi += ca[k] * cb[k]


    mo_a = 0
    # for k in ca.keys():
    #     mo_a += ca[k] * k * k

    for v in ca.values():
        mo_a += v * v

    mo_b = 0
    # for k in cb.keys():
    #     mo_b += cb[k] * k * k

    for v in cb.values():
        mo_b += v * v

    if mo_b == 0 or mo_a == 0:
        print "ERROR zero, a:",  a

        print "ERROR zero, b:", b

    return float( zi ) / float(  math.sqrt(mo_a) * math.sqrt(mo_b) )
    # for k,v in ca.


def cos_sim_tf_idf(a,b, idf_dict):
    ca = Counter(a)
    cb = Counter(b)


    for k in ca.keys():
        if not idf_dict.has_key(k):
            # print "===> cos_sim_tf_idf, IDF dict not have:", k
            del ca[k]
        else:
            ca[k] *= idf_dict[k]

    for k in cb.keys():
        if not idf_dict.has_key(k):
            # print "===> cos_sim_tf_idf, IDF dict not have:", k
            del cb[k]
        else:
            cb[k] *= idf_dict[k]


    key_set = set(ca.keys()) & set(cb.keys())

    a_len = sum(ca.values())
    b_len = sum(cb.values())

    for k in ca.keys():
        ca[k] /= float(a_len)
    for k in cb.keys():
        cb[k] /= float(b_len)


    zi = 0
    for k in key_set:
        zi += ca[k] * cb[k]

    mo_a = 0
    # for k in ca.keys():
    #     mo_a += ca[k] * k * k

    for v in ca.values():
        mo_a += v * v

    mo_b = 0
    # for k in cb.keys():
    #     mo_b += cb[k] * k * k

    for v in cb.values():
        mo_b += v * v

    return float(zi) / float(math.sqrt(mo_a) * math.sqrt(mo_b))


def get_qi_q_u(Tq):
    return 1.0 / len(Tq)

class xQuAD(object):
    def __init__(self, LM, lmd=0.5, alpha=0.5):
        self.LM = LM
        self.lmd = lmd
        self.alpha = alpha

    # def basic_params_clean(self, query, R_left, D, Tq):

    def get_q_d(self, q_words, d, all_dc_dics):
        '''
        :param q_words: words_list
        :param d: doc的dict格式的...
        :param all_doc_dics: 是所有文档的dc list， 通过key可以访问到dc
        :return:
        '''
        if all_dc_dics is None:
            return self.LM.cal_q_d_log(q_words, d=d)
        else:
            key = d[KEY]
            dc = all_dc_dics[key]
            return self.LM.cal_q_d(q_words, d = d, dc=dc)

    def get_q_d_cos(self, q_words, d, all_dc_dics):
            '''
            :param q_words: words_list
            :param d: doc的dict格式的...
            :param all_doc_dics: 是所有文档的dc list， 通过key可以访问到dc
            :return:
            '''
            # if all_dc_dics is None:
            #     return self.LM.cal_q_d_log(q_words, d=d)
            # else:
            #     key = d[KEY]
            #     dc = all_dc_dics[key]
            #     return self.LM.cal_q_d(q_words, d=d, dc=dc)

            # print "!!!!!!!!!?????????===>all_dc_dics[d[KEY]]", all_dc_dics[d[KEY]]

            return cos_dis(q_words, all_dc_dics[d[KEY]])


    def get_q_d_cos_tf_idf(self, q_words, d, all_dc_dics, idf_dict):
            '''
            :param q_words: words_list
            :param d: doc的dict格式的...
            :param all_doc_dics: 是所有文档的dc list， 通过key可以访问到dc
            :return:
            '''
            # if all_dc_dics is None:
            #     return self.LM.cal_q_d_log(q_words, d=d)
            # else:
            #     key = d[KEY]
            #     dc = all_dc_dics[key]
            #     return self.LM.cal_q_d(q_words, d=d, dc=dc)


            return cos_sim_tf_idf(q_words, all_dc_dics[d[KEY]], idf_dict)

    #R_left表示R-D
    def select_doc_u(self, query, R_left, D, Tq, query_field='content', dc_dicts=None, cal_qi_q = get_qi_q_u, if_log=False, ret_rel_div_score=False, boost_div_params=1.0):
        '''
        :param query: 这里的query必须是word_list
        :param R_left:
        :param D:
        :param Tq: 里面包含了各个subquery，每个subquery也必须是word_list
        :param query_field:
        :param cal_qi_q:
        :param if_log:
        :return:
        '''
        score_list = [] # [d, score]
        for d in R_left:
            # print "===select_doc_u CHECK=>", d[query_field]
            # tmp = self.LM.cal_q_d(query, d=d)
            rel_score = self.get_q_d(query, d, dc_dicts)
            # rel_score = (1 - self.lmd) * tmp
            div_score = 0
            for qi in Tq:
                p_qi_q = cal_qi_q(Tq)
                if if_log:
                    p_d_qi = self.LM.cal_q_d_log(qi, d=d)
                else:
                    # p_d_qi = self.LM.cal_q_d(qi, d = d)
                    p_d_qi = self.get_q_d(qi, d, dc_dicts)
                pi = 1.0
                for dj in D:
                    if if_log:
                        #TODO:应该是有问题的 还是得处理boost这样... 另外p(q|d)和p(d|q)这样的计算看看有没有可以优化的地方... 或者用decimal类，或者boost
                        pi += math.log(1.0 - boost_div_params * self.LM.cal_q_d(qi, d=dj))
                    else:
                        # pi *= 1.0 - self.LM.cal_q_d(qi, d = dj)
                        pi *= 1.0 - self.get_q_d(qi, dj, dc_dicts)

                div_score += p_qi_q * p_d_qi * pi
            # div_score *= self.lmd * div_score
            # div_score = self.lmd * div_score
            if ret_rel_div_score:
                score_list.append([d, (1 - self.lmd) * rel_score + self.lmd * div_score, rel_score, div_score])
            else:
                score_list.append([d, (1 - self.lmd) * rel_score + self.lmd * div_score])
        return sorted(score_list, reverse=True, key=lambda d: d[1])


    def select_doc_u_cos(self, query, R_left, D, Tq, query_field='content', dc_dicts=None, cal_qi_q = get_qi_q_u, if_log=False, ret_rel_div_score=False, boost_div_params=1.0):
        '''
        :param query: 这里的query必须是word_list
        :param R_left:
        :param D:
        :param Tq: 里面包含了各个subquery，每个subquery也必须是word_list
        :param query_field:
        :param cal_qi_q:
        :param if_log:
        :return:
        '''
        score_list = [] # [d, score]
        for d in R_left:
            # print "===select_doc_u CHECK=>", d[query_field]
            # tmp = self.LM.cal_q_d(query, d=d)
            rel_score = self.get_q_d_cos(query, d, dc_dicts)
            # rel_score = (1 - self.lmd) * tmp
            div_score = 0
            for qi in Tq:
                p_qi_q = cal_qi_q(Tq)
                if if_log:
                    p_d_qi = self.LM.cal_q_d_log(qi, d=d)
                else:
                    # p_d_qi = self.LM.cal_q_d(qi, d = d)
                    p_d_qi = self.get_q_d_cos(qi, d, dc_dicts)
                pi = 1.0
                for dj in D:
                    if if_log:
                        #TODO:应该是有问题的 还是得处理boost这样... 另外p(q|d)和p(d|q)这样的计算看看有没有可以优化的地方... 或者用decimal类，或者boost
                        pi += math.log(1.0 - boost_div_params * self.LM.cal_q_d(qi, d=dj))
                    else:
                        # pi *= 1.0 - self.LM.cal_q_d(qi, d = dj)
                        pi *= 1.0 - self.get_q_d_cos(qi, dj, dc_dicts)
                        # print "!!!!!!!!!?????????===>pi:", pi

                div_score += p_qi_q * p_d_qi * pi
                # print "XXXXXXXXXXXXXXX==============>p_qi_q, p_d_qi, div:", p_qi_q, p_d_qi, div_score, qi
            # div_score *= self.lmd * div_score
            # div_score = self.lmd * div_score
            if ret_rel_div_score:
                score_list.append([d, (1 - self.lmd) * rel_score + self.lmd * div_score, rel_score, div_score])
            else:
                score_list.append([d, (1 - self.lmd) * rel_score + self.lmd * div_score])
        return sorted(score_list, reverse=True, key=lambda d: d[1])

    def select_doc_u_cos_tf_idf(self, query, R_left, D, Tq, query_field='content', dc_dicts=None, cal_qi_q = get_qi_q_u, if_log=False, ret_rel_div_score=False, boost_div_params=1.0, idf_dict={}):
        '''
        :param query: 这里的query必须是word_list
        :param R_left:
        :param D:
        :param Tq: 里面包含了各个subquery，每个subquery也必须是word_list
        :param query_field:
        :param cal_qi_q:
        :param if_log:
        :return:
        '''
        score_list = [] # [d, score]
        for d in R_left:
            # print "===select_doc_u CHECK=>", d[query_field]
            # tmp = self.LM.cal_q_d(query, d=d)
            rel_score = self.get_q_d_cos_tf_idf(query, d, dc_dicts, idf_dict)
            # rel_score = (1 - self.lmd) * tmp
            div_score = 0
            for qi in Tq:
                p_qi_q = cal_qi_q(Tq)
                if if_log:
                    p_d_qi = self.LM.cal_q_d_log(qi, d=d)
                else:
                    # p_d_qi = self.LM.cal_q_d(qi, d = d)
                    p_d_qi = self.get_q_d_cos_tf_idf(qi, d, dc_dicts, idf_dict)
                pi = 1.0
                for dj in D:
                    if if_log:
                        #TODO:应该是有问题的 还是得处理boost这样... 另外p(q|d)和p(d|q)这样的计算看看有没有可以优化的地方... 或者用decimal类，或者boost
                        pi += math.log(1.0 - boost_div_params * self.LM.cal_q_d(qi, d=dj))
                    else:
                        # pi *= 1.0 - self.LM.cal_q_d(qi, d = dj)
                        pi *= 1.0 - self.get_q_d_cos_tf_idf(qi, dj, dc_dicts, idf_dict)
                div_score += p_qi_q * p_d_qi * pi
            # div_score *= self.lmd * div_score
            # div_score = self.lmd * div_score
            if ret_rel_div_score:
                score_list.append([d, (1 - self.lmd) * rel_score + self.lmd * div_score, rel_score, div_score])
            else:
                score_list.append([d, (1 - self.lmd) * rel_score + self.lmd * div_score])
        return sorted(score_list, reverse=True, key=lambda d: d[1])


    def diversity_score(self, query, R, Tq, ret_cnt=5):
        R_left = copy.deepcopy(R)
        D = []
        for i in range(ret_cnt):
            d = self.select_doc_u(query, R_left, D, Tq)
            D.append(d)
            R_left.remove(d)


    def select_doc_u_div(self, query, R_left, D, Tq, query_field='content', dc_dicts=None, cal_qi_q = get_qi_q_u, if_log=False, ret_rel_div_score=False, boost_div_params=1.0):
        '''
        重做一下概率那部分
        :param query: 这里的query必须是word_list
        :param R_left:
        :param D:
        :param Tq: 里面包含了各个subquery，每个subquery也必须是word_list
        :param query_field:
        :param cal_qi_q:
        :param if_log:
        :return:
        '''
        score_list = [] # [d, score]
        for d in R_left:
            # print "===select_doc_u CHECK=>", d[query_field]
            # tmp = self.LM.cal_q_d(query, d=d)
            rel_score = self.get_q_d(query, d, dc_dicts)
            # rel_score = (1 - self.lmd) * tmp
            div_score = 0
            for qi in Tq:
                p_qi_q = cal_qi_q(Tq)
                if if_log:
                    p_d_qi = self.LM.cal_q_d_log(qi, d=d)
                else:
                    # p_d_qi = self.LM.cal_q_d(qi, d = d)
                    p_d_qi = self.get_q_d(qi, d, dc_dicts)
                pi = 1.0
                for dj in D:
                    if if_log:
                        #TODO:应该是有问题的 还是得处理boost这样... 另外p(q|d)和p(d|q)这样的计算看看有没有可以优化的地方... 或者用decimal类，或者boost
                        pi += math.log(1.0 - boost_div_params * self.LM.cal_q_d(qi, d=dj))
                    else:
                        # pi *= 1.0 - self.LM.cal_q_d(qi, d = dj)
                        pi *= 1.0 - self.get_q_d(qi, dj, dc_dicts)
                div_score += p_qi_q * p_d_qi * pi
            # div_score *= self.lmd * div_score
            # div_score = self.lmd * div_score
            if ret_rel_div_score:
                score_list.append([d, (1 - self.lmd) * rel_score + self.lmd * div_score, rel_score, div_score])
            else:
                score_list.append([d, (1 - self.lmd) * rel_score + self.lmd * div_score])
        return sorted(score_list, reverse=True, key=lambda d: d[1])

class HxQuAD(object):
    def __init__(self):
        pass


if __name__ == '__main__':
    pass

__END__ = True