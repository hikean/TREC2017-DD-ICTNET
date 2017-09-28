# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/11 下午4:43
# @version: 1.0

from basic_init import *
from w2v_utils import *
import copy


'''
用的时候可以考虑按照段落划分是不是相关
'''


#参数都是vec表示
def rocchio_vec(q, rdocs, nrdocs, a, b, r):

    q = np.array(q)
    rdocs = np.array(rdocs)
    nrdocs = np.array(nrdocs)
    ret = a * q + b * rdocs - r * nrdocs

    return ret.tolist()

#参数都是文档表示
def rocchio_docs(q, rdocs, nrdocs, wv_model=None, a=1.0, b=0.75, r=0.25):
    if wv_model is None:
        logging.info("wv model not init, load model...")
        wv_model = VecUtils()

    q_vec = wv_model.doc2vec(q)
    rdocs = wv_model.docs_avg_vec(rdocs)
    nrdocs = wv_model.docs_avg_vec(nrdocs)

    return rocchio_docs(q_vec, rdocs, nrdocs, a, b, r)


'''
直接根据查询词权重来查询的rocchio算法

输入:query,相关文档的、不相关文档的tfidf dict
输出:新的query的dict
'''

def solr_w(k, w):
    return str(k) + '^' + str(w)

def qjoin(qa, qb, sp=' '):
    return qa.strip() + sp + qb.strip()

#TODO:检查一下这里的间隔关键词的符号到底应该是,还是' '以及二者区别
def wdic2str(dic, sp=','):
    ret = ""
    for i, (k, v) in enumerate(dic.items()):
        ret += solr_w(k, v)
        if i != len(dic.items()) - 1:
            ret += sp
    return ret.strip()

def addW(dic, a=1.0):
    ret = {}
    for (k, v) in dic.items():
        ret[k] = a * dic[k]
    return ret

def rocchio_update_qurey(q_dic, rdic, nrdic, a=1.0, b=0.75, r=0.25):
    wq_dic = addW(q_dic, a)
    wrdic = addW(rdic, b)
    wnrdic = addW(nrdic, r)

    tot_keys = q_dic.keys() + rdic.keys() + nrdic.keys()

    ret = {}

    for k in tot_keys:
        v = 0.0
        if wq_dic.has_key(k): v += wq_dic[k]
        if wrdic.has_key(k): v += wrdic[k]
        if wnrdic.has_key(k): v -= wnrdic[k]
        ret[k] = v

    return ret






if __name__ == '__main__':
    pass

__END__ = True