# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/17 上午10:00
# @version: 1.0

'''
注:所有词都做了小写处理
Query Expansion的算法


1、QE_w2v论文<Using Word Embeddings for Automatic Query Expansion>的算法
n-gram 去解决多义词问题
2、

'''

#TODO:需要看一下是否需要直接把query里面加一个ebola

'''
similar_by_vector
'''

import numpy as np
from scipy.linalg.misc import norm
from preprocess_utils import *
from w2v_utils import *

def cos_sim(a=[],b=[]):
    a_ = np.asarray(a)
    b_ = np.asarray(b)
    ret = np.dot(a_, b_) / (norm(a_) * norm(b_) )

    return ret

'''
把sim item的格式的化成一个query
'''
def word2query_by_sim(witems, sp=',',default_w = None):
    q = []
    for (word, w) in witems:
        if default_w is None:
            q.append( str(word) + '^' + str(w) )

    return ','.join(q)

def expand_by_tfidf_candidate_words(idf_dict, cwords, init_words = [], ret_cnt=10):
    doc_len = float( len(cwords) )
    tf_idf_w = {}
    # cwords = set(cwords)
    init_words = set( [ _.lower() for _ in init_words] )
    w_cnt = {}
    for w in cwords:
        if w in '{}|[]' or w.lower() in init_words:continue
        if w.lower() in STOPWORDS or w in BAD_WORDS:continue
        if w_cnt.has_key(w):
            w_cnt[w] += 1
        else:
            w_cnt[w] = 1

    for w in cwords:
        if idf_dict.has_key(w) and w_cnt.has_key(w):
            tf_idf_w[w] = w_cnt[w] * idf_dict[w] / doc_len

    return sorted(tf_idf_w.items(), reverse=True, key=lambda d:d[1])[0:ret_cnt]



class QE_w2v(object):
    def __init__(self, query, w2v_model, base_words=[]):
        self.init_query = query.strip() + ' ' + ' '.join(base_words)
        self.init_query = self.init_query.strip()
        print "init query:", self.init_query
        self.clean_init_query_words = doc2clean_words(query)
        self.itr = 0
        self.wv_model = w2v_model
        self.init_query_vec = w2v_model.doc2vec(self.init_query)
        self.qc = None
        self.qc_vecs = None #
        self.q_exp = None
        self.q_exp_ws = None

        self.q_exp_vec = None
        self.q_joing_qc = None
        self.k_words = []

        self.q_join_vec = None


    #和原文Qc一样， 2-gram的向量
    def cal_qc(self):
        bigrams = mk_bigrams(self.init_query)
        self.qc = bigrams
        self.qc_vecs = []
        for b in bigrams:
            self.qc_vecs.append( self.wv_model.doc2vec(b) )

    #参考论文， Qexp，就是扩展的K个词的集合
    def expand_word_by_vec(self, query_vec, qwords, k = 1):
        print "DEBUG query_vec:", query_vec
        print "DEBUG qwords:", qwords
        query_vec = np.asarray(query_vec)
        words = self.wv_model.similar_by_vector(query_vec)
        get_cnt = 0
        ret = []
        for w_s in words:
            w = w_s[0].lower()
            if w in qwords:
                continue
            else:
                print "not dup:", w
                ret.append( w_s )
                get_cnt += 1
                if get_cnt >= k: return ret
        return []

    def update_query_vec(self, query_vec, old_len, word):
        if type(query_vec) == list:
            query_vec = np.asarray(query_vec)
        return ( query_vec * old_len + self.wv_model[word] ) / float(old_len + 1)

    def most_similar_words(self, candidate_words, word, k=10):
        score = dict()
        wv = self.wv_model[word]
        for w in candidate_words:
            score[w] = cos_sim(wv, self.wv_model[w])

        return sorted(score.items(), reverse=True, key=lambda d:d[1])

    def most_similar_ngrams(self):
        pass


    #返回值: (word, sim)
    #add的规则还需要设定sim阈值
    #计算qexp
    def expand_k_words_inc(self, k = 5, query = None):
        if query is not None:
            qwords = doc2clean_words(query)
            init_vec = self.wv_model.doc2vec(qwords)
        else:
            qwords = self.clean_init_query_words
            init_vec = self.init_query_vec

        expand_w_s = []
        expand_w = []
        new_query_vec = [v for v in init_vec]
        # new_qwords = [w for w in qwords]
        for i in range(k):
            inc_w_s = self.expand_word_by_vec(new_query_vec, qwords + expand_w)
            print "inc_w_s:", inc_w_s
            expand_w_s += inc_w_s
            nw = expand_w_s[-1][0]
            expand_w.append(nw.lower())
            new_query_vec = self.update_query_vec( new_query_vec, len(qwords), nw )
            qwords.append(nw)
        print "expand word cnt:", len(expand_w)
        self.q_exp_ws = expand_w_s
        self.q_exp = expand_w

    def avg_vecs(self, vecs):
        tot = np.asarray(vecs)
        return sum(tot)/float(tot.shape[0])

    def update_query_vec_by_vecs(self, vecs):
        if type(self.init_query_vec) == list:
            self.init_query_vec = np.asarray(self.init_query_vec)
        tot = self.init_query_vec * len(self.clean_init_query_words)
        tot_cnt = len(self.clean_init_query_words) + len(vecs)
        tot += sum( np.asarray(vecs) )
        return tot/float(tot_cnt)

    #调用这个函数之前要先调用cal_qc
    def cal_join_vec(self):
        if self.qc_vecs is None: self.cal_qc()
        self.q_join_vec = self.update_query_vec_by_vecs(self.qc_vecs)

    #调用之前要先调用cal_join_vec以及expand_k_words_inc
    #因为暂时不会算P(w|Q) 就先不考虑这一部分，只考虑sim
    #TODO:现在没考虑P, 需要考虑P的那一部分, 可以试试考虑跟原始查询相似度以及新的扩展查询相似度的加权
    def expand_by_lm(self, a=0.6):
        lm_words = [] #存储格式，[word, score]  score就是那个lm式子计算出来的p
        lm_ws_sim_query = {} #存储格式，key=word v=sim(w, q_join), sim(w, init_query)
        lm_ws_sim_query_list = []
        # lm_ws_sim_init_query = {}
        # for i,w_s in enumerate(self.q_exp_ws):
        for i,w_s in enumerate(self.q_exp_ws):
            w = w_s[0]
            lm_ws_sim_query[w] = [ cos_sim(self.wv_model[w], self.init_query_vec), cos_sim(self.wv_model[w], self.q_join_vec) ]
            score = sum(lm_ws_sim_query[w])
            lm_ws_sim_query_list.append( [w,] + lm_ws_sim_query[w] + [score, ] )

        lm_ws_sim_query_list = sorted( lm_ws_sim_query_list, key=lambda a:a[-1], reverse=True)
        return lm_ws_sim_query_list


    def expand_by_candidate_words(self, qvec, cwords, init_words=[] ,ret_cnt=10, sim_limit = 0.7):
        init_set = set([_.lower() for _ in init_words])
        dic = {}
        for w in cwords:
            if self.wv_model.contains(w):
                if w.lower() in init_set:continue
                sim = cos_sim(qvec, self.wv_model[w])
                if sim >= sim_limit:
                    dic[w] = sim


        return sorted(dic.items(), reverse=True, key=lambda d:d[1])[0:min(ret_cnt, len(dic.items()))]





if __name__ == '__main__':

    query = "US Military Crisis Response"
    base_words = []
    # base_words = ['ebola']


    vecutils = VecUtils()
    qe = QE_w2v(query, vecutils, base_words=base_words)
    logging.info("cal qc...")
    qe.cal_qc()

    logging.info("expand k words inc")
    qe.expand_k_words_inc()

    logging.info("cal_join_vec...")
    qe.cal_join_vec()

    logging.info("cal word list...")
    word_list = qe.expand_by_lm()

    print "expand words...", word_list

    new_query_words = []
    for w in word_list:
        new_query_words.append( w[0].lower() )

    print "new query:", ' '.join(new_query_words)

    #test_model = "/Users/zhangweimin/Desktop/TREC/model/textmodel/content_w2v.model"

__END__ = True