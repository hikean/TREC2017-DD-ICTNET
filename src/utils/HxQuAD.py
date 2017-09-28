# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/3 下午8:55
# @version: 1.0

'''
符号统一:
t和qi认为是同一个东西

P(t|q)的几种算法参考xQuAD的论文：
(1)P(t|q)c 这种简单先用着



'''

class HxQuAD(object):
    def __init__(self, LM, lmd=0.5, alpha=0.5):
        self.LM = LM
        self.lmd = 0.5
        self.alpha = 0.5

    #R_left表示R-D
    def select_doc_u(self, query, R_left, D, Tq, secondaryTq):
        score_list = []
        for d in R_left:
            rel_score = (1 - self.lmd) * self.LM.cal_q_d(query, d=d)




    def diversity_score(self, R):

        pass

if __name__ == '__main__':
    pass

__END__ = True