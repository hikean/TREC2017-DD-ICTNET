# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/6 下午4:23
# @version: 1.0

'''
参考 Search Result Diversiﬁcation Based on Hierarchical Intents

以及 PM算法的原始论文

Diversity by Proportionality: An Election-based Approach to Search Result Diversiﬁcation


目前比例先按照 subquery在query的结果中占的比例来算， 也就是vi的大小这么算

'''

import copy
from LMDirichlet import LMDirichlet

class PM2(object):
    def __init__(self, sub_querys=[], sub_querys_vs=[], R=[], lmd=0.5, LM=LMDirichlet()):
        self.sub_querys = sub_querys
        self.sub_querys_vs = sub_querys_vs #vi
        self.R = R
        self.R_left = copy.deepcopy(self.R)
        self.S = []
        self.sub_querys_ss = [] #si
        self.quotients = []
        for i in range(len(self.sub_querys_vs)):
            self.quotients.append( self.sub_querys_vs[i]  * 1.0)
        self.lmd = lmd
        self.LM = LM

    #每次返回一篇文档
    def select_doc(self, field = 'content'):
        i_star = self.quotients.index(max(self.quotients))
        scores = []

        for j in range(len(self.R_left)):
            novalty_score = 0
            for i in range(len(self.sub_querys)):
                if i == i_star: continue
                novalty_score += self.LM.cal_q_d( self.sub_querys[i], self.R_left[j])
            rel_score = self.quotients[i_star] * self.LM.cal_q_d(self.sub_querys[i_star], self.R_left[j])
            scores.append( [self.R_left[j], self.lmd * rel_score + (1  - self.lmd) * novalty_score] )

        d_idx = scores.index( max([_[-1] for _ in scores]) )
        #update quotient si
        select_d = self.R_left[d_idx]
        self.S.append( self.R_left[d_idx] )
        self.R_left.remove( select_d )

        rel_sum = 0
        for i in range(len(self.sub_querys)):
            rel_sum += self.LM.cal_q_d(self.sub_querys[i], select_d)

        rel_sum = float(rel_sum)

        for i in range(len(self.sub_querys)):
            self.sub_querys_ss[i] += self.LM.cal_q_d(self.sub_querys[i], select_d) / rel_sum

        return select_d


if __name__ == '__main__':
    pass

__END__ = True