# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/27 上午2:59
# @version: 1.0


'''

多维度的xQuAD

主要三个
1、jig feedback
2、query suggested
3、根据情况考虑LDA

实际tf-idf的相似和w2v的相似的结合也是可以考虑的

'''

import copy
import math
from constants import *
from collections import Counter
import math
from xQuAD import cos_dis,cos_sim_tf_idf,get_qi_q_u


def doclist2dict(doc_list):
    ret = {}
    for d in doc_list:
        ret[ d[0][KEY] ] = d
    return ret


#BUG:
# def merge_doc_score( doc_list_a, doc_list_b, ws):
#     dic_a = doclist2dict(doc_list_a)
#     dic_b = doclist2dict(doc_list_b)
#
#     ret = []
#     tot_keys = dic_a.keys() + dic_b.keys()
#     #[d, (1 - self.lmd) * rel_score + self.lmd * div_score, rel_score, div_score]
#     for k in tot_keys:
#         scores = [0,0,0]
#         d = None
#         if dic_a.has_key(k):
#             scores[1] += ws[0] * 1.0 * dic_a[k][1]
#             scores[2] += ws[0] * 1.0 * dic_a[k][2]
#             d = dic_a[k][0]
#         if dic_b.has_key(k):
#             scores[1] += ws[1] * 1.0 * dic_b[k][1]
#             scores[1] += ws[1] * 1.0 * dic_b[k][2]
#             d = dic_b[k][0]
#         scores[0] = sum(scores[1:])
#         ret.append( [d] + scores )
#
#     return sorted(ret, reverse=True, key=lambda d:d[1])

def merge_doc_score( doc_list_a, doc_list_b, ws):
    dic_a = doclist2dict(doc_list_a)
    dic_b = doclist2dict(doc_list_b)

    ret = []
    tot_keys = dic_a.keys() + dic_b.keys()
    #[d, (1 - self.lmd) * rel_score + self.lmd * div_score, rel_score, div_score]
    for k in tot_keys:
        scores = [0,0,0]
        d = None
        if dic_a.has_key(k):
            scores[0] += ws[0] * 1.0 * dic_a[k][1]
            scores[1] += ws[0] * 1.0 * dic_a[k][2]
            scores[2] += ws[0] * 1.0 * dic_a[k][3]

            d = dic_a[k][0]
        if dic_b.has_key(k):
            scores[0] += ws[1] * 1.0 * dic_b[k][1]
            scores[1] += ws[1] * 1.0 * dic_b[k][2]
            scores[2] += ws[1] * 1.0 * dic_b[k][3]
            d = dic_b[k][0]

        ret.append( [d] + scores )

    return sorted(ret, reverse=True, key=lambda d:d[1])


class xQuAD_multi(object):
    def __init__(self, LM, lmd=[], ws=[]):
        '''

        :param LM:
        :param lmd: 表示每一个算法的lmd
        :param w: 表示每一部分分数的权重
        '''
        self.LM = LM
        self.algorithm_w = lmd

        self.lmd = lmd
        self.w = ws

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

    def select_doc_u_multi(self, query, R_left, D, Tq_subquery, Tq_passage_text, query_field='content', dc_dicts=None, cal_qi_q = get_qi_q_u, if_log=False, ret_rel_div_score=False, boost_div_params=1.0):
        # print "weight:"

        if len(Tq_subquery) == 0 and len(Tq_passage_text) == 0:
            #TODO:外面需要特判一下这种情况
            print "[WARN]  len(Tq_subquery) == 0 and len(Tq_passage_text) ==0, q_word_list: ", query
            return None


        if len(Tq_subquery) != 0:
            doc_list_by_subquery = self.select_doc_u_cos(query, R_left, D, Tq_subquery, query_field=query_field, dc_dicts=dc_dicts, cal_qi_q=cal_qi_q, if_log=if_log, ret_rel_div_score=ret_rel_div_score, boost_div_params=boost_div_params, lmd=self.algorithm_w[0])
            use_subquery = True
        else:
            use_subquery = False

        if len(Tq_passage_text) != 0:
            doc_list_by_passage_text = self.select_doc_u_cos(query, R_left, D, Tq_passage_text, query_field=query_field, dc_dicts=dc_dicts, cal_qi_q=cal_qi_q, if_log=if_log, ret_rel_div_score=ret_rel_div_score, boost_div_params=boost_div_params, lmd=self.algorithm_w[1])
            use_feedback = True
        else:
            use_feedback = False

        if use_subquery and use_feedback:
            return merge_doc_score(doc_list_by_subquery, doc_list_by_passage_text, self.w)
        else:
            if use_subquery:
                return doc_list_by_subquery
            else:
                return doc_list_by_passage_text

    #R_left表示R-D
    def select_doc_u_cos(self, query, R_left, D, Tq, query_field='content', dc_dicts=None, cal_qi_q = get_qi_q_u, if_log=False, ret_rel_div_score=False, boost_div_params=1.0, lmd=None):
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

        if lmd is not None:
            print "change lmd...:", lmd
            self.lmd = lmd

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





if __name__ == '__main__':
    pass

__END__ = True