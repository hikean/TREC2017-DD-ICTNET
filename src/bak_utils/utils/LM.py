# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/3 下午11:24
# @version: 1.0

'''
参考了 王斌信息检索导论 LM的实现
使用线性插值法


根据这个LM可以考虑再扩展成n-gram的

因为没有处理，所以外部可以根据传入的数据来决定是bi-gram或者其他

'''

import json
import codecs

from collections import defaultdict

class LM(object):
    def __init__(self, lmd = 0.5):
        self.lmd = lmd
        self.C = {}
        self.vocab = {}
        self.tot_words = 0

    #doc_list表示[doc1,doc2...]doc是words的表示
    def train(self, doc_list, model_file=None):

        for doc in doc_list:
            for w in doc:
                if self.vocab.has_key(w):
                    self.vocab[w] += 1
                else:
                    self.vocab[w] = 1

        for k,v in self.vocab.items():
            self.tot_words += v

        for k,v in self.vocab.items():
            self.C[w] = v/float(self.tot_words)

        if model_file is not None:
            with codecs.open(model_file, 'w', 'utf-8') as fobj:
                fobj.write(json.dumps(self.C))
    #返回dict,内容是P(w|d)
    def cal_q_d(self, q, dc=None, d=None):
        if dc is None and d is None:
            dc = defaultdict(int)
            for w in d:
                dc[w] += 1.0/len(d)
        ret = 1.0
        for w in q:
            ret *= self.lmd * self.C[w] + (1-self.lmd) * dc[w]

        return ret

    def cal_dc(self, d):

        dc = defaultdict(int)
        for w in d:
            dc[w] += 1.0 / len(d)
        return dc

    def cal_w_d(self, w, d):
        cnt = 0
        for _ in d:
            if _ == w:
                cnt += 1
        return self.lmd * self.C[w] + (1 - self.lmd) * cnt/float(len(d))

if __name__ == '__main__':
    pass

__END__ = True