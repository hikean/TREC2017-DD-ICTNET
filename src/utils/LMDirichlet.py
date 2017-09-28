# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/4 下午7:29
# @version: 1.0


'''
参考 将从全部文档集中获得的语言模型（不是像 11.3.2 节讨论的那样看成均 匀分布）看成贝叶斯更新过程（Bayesian updating process）的一个先验分布

信息检索导论 12-11公式

'''

from basic_init import *
from src.global_settings import *
from src.utils.constants import *
from src.data_preprocess.doc_preprocess import *
from preprocess_utils import *
from sample_doc import *

import json
import codecs
import math

from collections import defaultdict

class LMDirichlet(object):
    def __init__(self, lmd = 800):
        print "LMDirichlet"
        self.lmd = lmd
        self.C = {}
        self.vocab = {}
        self.tot_words = 0

    def __getitem__(self, w):
        if self.C.has_key(w):return self.C[w]
        else: return 0.0


    def load(self, js_file, code_type='utf-8'):
        logging.info("loading %s" % js_file)
        js = json.load(codecs.open(js_file, 'r', code_type))
        self.C = js


    #doc_list表示[doc1,doc2...]doc是words的表示
    def train(self, doc_list, model_file=None):
        logging.info("training LMDirichlet...")
        for doc in doc_list:
            for w in doc:
                if self.vocab.has_key(w):
                    self.vocab[w] += 1
                else:
                    self.vocab[w] = 1

        for k,v in self.vocab.items():
            self.tot_words += v

        logging.info("LM training, cal p(w|C)...")
        for k,v in self.vocab.items():
            self.C[k] = v/float(self.tot_words)

        if model_file is not None:
            with codecs.open(model_file, 'w', 'utf-8') as fobj:
                fobj.write(json.dumps(self.C))

    def cal_q_d(self, q, dc=None, d=None, clean=False, content_field='content'):
        '''
        :param q: 必须是word list
        :param dc:
        :param d: d是{}类型，d[content_field]表示的是内容，这个内容是做过了基本处理的内容
        :param clean:
        :param content_field:
        :return:内容是P(w|d)
        '''
        # print "QUERY:", q
        if type(q) != list:
            print "before process q:", q
            q = basic_preprocess(q)
            print "after process q:", q
        if type(d[content_field]) != list:
            d[content_field] = basic_preprocess(d[content_field][0])

        if clean: q = clean_tools(q)
        if dc is None and d is not None:
            if clean:
                d[content_field] = clean_tools(d[content_field])
            dc = defaultdict(int)

            for w in d[content_field]:
                dc[w] += 1.0

            # print 'CHECKING..., doc len:', len(d[content_field])
            # for w in q:
            #     print "check w cnt:", w, dc[w]


        # print '[DEBUG] dc:', dc['US'], dc
        ret = 1.0
        for w in q:
            ret *= (dc[w] + self.lmd * self.C[w])  / (
                float(len(d[content_field]) + self.lmd) # * self.C[w] # * len(d[content_field])
            )
            # ret *= (dc[w] + self.lmd * self.C[w]) / (
            #     float(len(d[content_field]) + self.lmd)
            # ) #self.lmd * self.C[w] + (1-self.lmd) * dc[w]

        return ret

    #这里的d和q都是必须是wordlist
    def cal_q_d_log(self, q, dc=None, d=None, clean=False, content_field='content'):
        '''
        :param q: 这个q可以是string句子，可以是wordlist，这个我来处理，
        :param dc:
        :param d: d是{}类型，d[content_field]表示的是内容，这个内容是做过了基本处理的内容
        :param clean:
        :param content_field:
        :return:内容是P(w|d)
        '''

        if type(q) != list:
            q = basic_preprocess(q)
        if type(d[content_field]) != list:
            d[content_field] = basic_preprocess(d[content_field][0])

        if clean: q = clean_tools(q)
        if dc is None and d is not None:
            if clean:
                d[content_field] = clean_tools(d[content_field])
            dc = defaultdict(int)

            for w in d[content_field]:
                dc[w] += 1.0

        # print '[DEBUG] dc:', dc['US'], dc
        ret = 1.0
        for w in q:
            ret += math.log((dc[w] + self.lmd * self.C[w]) / float( len(d[content_field]) + self.lmd )) #self.lmd * self.C[w] + (1-self.lmd) * dc[w]

        return ret

    def cal_dc(self, d):
        '''
        :param d:显然这里的d也是word list
        :return:
        '''
        dc = defaultdict(int)
        for w in d:
            dc[w] += 1.0

        # for w, v in dc.items():
        #     dc[w] = (dc[w] + self.lmd * self.C[w]) / float( len(d) + self.lmd )

        return dc

    def cal_w_d(self, w, d):
        '''
        :param w: 一个词 str类型
        :param d: 这个d是一个word_list
        :return: 概率
        '''
        cnt = 0
        for _ in d:
            if _ == w:
                cnt += 1
        return (cnt + self.lmd * self.C[w]) / float( len(d) + self.lmd )


def cal_lm_raw(doc_file, out_file):
    with open(doc_file, 'r') as fobj:
        logging.info("read docs...")
        lines = fobj.readlines()
        docs = []
        for l in lines:
            if len(l.strip()) == 0: continue
            docs.append( [w.strip() for w in l.split(',')[1:] if len(w.strip()) != 0 ] )
        logging.info("data len:" + str(len(docs)))
        logging.info("processing docfile...")
        lm = LMDirichlet()
        lm.train(docs, out_file)


def process_raw():
    lm_file = LMDirichlet_Json
    doc_file = "/home/zhangwm/Data/clean_line/ebola_words.txt"
    cal_lm_raw(doc_file, lm_file)

def clean_tools(word_list):
    word_list = stemmer_by_porter(word_list)
    word_list = remove_punc(word_list)
    return word_list

def cal_lm_clean(doc_file, out_file):
    with open(doc_file, 'r') as fobj:
        logging.info("read docs...")
        lines = fobj.readlines()
        ignore_cnt = 0
        docs = []
        for l in lines:
            if len(l.strip()) == 0: continue
            line = [w.strip() for w in l.split(',')[1:] if len(w.strip()) != 0 ]
            line = clean_tools(line)
            if len(line) != 0:
                docs.append( line )
            else:
                ignore_cnt += 1

        print "ignore cnt:", ignore_cnt
        logging.info("data len:" + str(len(docs)))
        logging.info("processing docfile...")
        lm = LMDirichlet()
        lm.train(docs, out_file)

#TODO:smooth...
# def cal_KL_dis(lm_model, q_words, d_words):
#     kl_dis = 0.0
#     for i, t in enumerate(q_words):
#         if t in d_words:
#             kl_dis += lm_model[t] * math.log( lm_ )


def init_LM():
    lm_file = LMDirichlet_clean_Json
    doc_file = "/home/zhangwm/Data/clean_line/ebola_words.txt"
    cal_lm_clean(doc_file, lm_file)

'''
测试基本的，比如query中的w的概率以及q和d的概率
'''
def test_1():
    q = 'US Military Crisis Response'
    q = cut_words(q)
    d1 = sample_doc # 'US Military Crisis Response US Military Crisis Response US Military Crisis Response'
    d1 = basic_preprocess(d1)
    d2 = {'score': 9.644032, 'key': 'ebola-1bbd62fe484a96be675ab80a304f0320a742a2da67f696cde413aee99e9f9349', 'content':d1}
    lm = LMDirichlet()
    lm.load(LMDirichlet_Json)
    print 'lm.C[US]:', lm.C['US']
    p1 = lm.cal_w_d('US', d1)
    p2 = lm.cal_q_d(q, d=d2)
    p3 = lm.cal_q_d_log(q, d=d2)

    print "p w,d:", p1, math.log(p1)
    print "p q,d:", p2
    print "p q,d:", p3


'''
测试 传入dict的
'''
def test_2():
        q = 'US Military Crisis Response'
        q = cut_words(q)
        d1 = sample_doc  # 'US Military Crisis Response US Military Crisis Response US Military Crisis Response'
        d1 = basic_preprocess(d1)

        d2 = {
            'score': 9.644032,
            'key': 'ebola-1bbd62fe484a96be675ab80a304f0320a742a2da67f696cde413aee99e9f9349',
            'content': d1
            }
        lm = LMDirichlet()
        dc = lm.cal_dc(d1)

        lm.load(LMDirichlet_Json)
        print 'lm.C[US]:', lm.C['US']
        p1 = lm.cal_w_d('US', d1)
        p2 = lm.cal_q_d(q, d=d2)
        p3 = lm.cal_q_d_log(q, d=d2)
        p4  = lm.cal_q_d(q, d=d2, dc=dc)


        print "p w,d:", p1, math.log(p1)
        print "p q,d:", p2
        print "p q,d:", p3
        print "p d d by dc:", p4

'''
使用重新处理的没有做词干化的,但是query和语料用的是相同的处理
'''
def test_3():
    from data_utils import basic_preprocess
    q = 'US Military Crisis Response'
    q = cut_words(q)
    d1 = sample_doc  # 'US Military Crisis Response US Military Crisis Response US Military Crisis Response'
    q_list = basic_preprocess(q)
    d1 = basic_preprocess(d1)

    d2 = {
        'score': 9.644032,
        'key': 'ebola-1bbd62fe484a96be675ab80a304f0320a742a2da67f696cde413aee99e9f9349',
        'content': d1
    }
    lm = LMDirichlet()
    dc = lm.cal_dc(d1)

#LMDirichlet_without_stem
    lm.load(LMDirichlet_Json)
    # print 'lm.C[US]:', lm.C['US']
    # print d1

    p1 = lm.cal_w_d('US', d1)
    p2 = lm.cal_q_d(q, d=d2)
    p3 = lm.cal_q_d_log(q, d=d2)
    p4 = lm.cal_q_d(q, d=d2, dc=dc)

    print "p w,d:", p1, math.log(p1)
    print "p q,d:", p2
    print "p q,d:", p3
    print "p d d by dc:", p4

    print "===================="
    print "q list:", q_list
    lm.load(LMDirichlet_without_stem)
    # print 'lm.C[US]:', lm.C['US']
    p1 = lm.cal_w_d(q_list[0], d1)
    p2 = lm.cal_q_d(q, d=d2)
    p3 = lm.cal_q_d_log(q, d=d2)
    p4 = lm.cal_q_d(q, d=d2, dc=dc)

    print "p w,d:", p1, math.log(p1)
    print "p q,d:", p2
    print "p q,d:", p3
    print "p d d by dc:", p4

if __name__ == '__main__':
    # init_LM()

    # lm_file = LMDirichlet_clean_Json
    # test_1()
    # test_2()
    test_3()
__END__ = True