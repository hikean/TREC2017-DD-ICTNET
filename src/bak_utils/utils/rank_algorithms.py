# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/7 上午10:45
# @version: 1.0

# from zope.interface import Interface, implements

class Base_scorer(object):
    def __init__(self):
        pass

    #返回q和一篇文档的分数
    def get_score(self, q, d):
        return 1.0

    #返回q和所有文档的分数，Ret格式 按score由大到小排序[ [doc1, score1], [doc2, score2], ]
    def get_scores(self, q, docs):
        pass

# class BM25_scorer(Base_scorer):

class Ranker(object):
    def __init__(self, scorer):
        self.scorer = scorer
    def rank(self, query, docs):
        pass


if __name__ == '__main__':
    pass

__END__ = True