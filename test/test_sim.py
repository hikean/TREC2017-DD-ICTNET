# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/17 上午10:57
# @version: 1.0

from scipy import spatial
import numpy as np
from scipy.linalg.misc import norm

def cos_sim(a=[],b=[]):
    a_ = np.asarray(a)
    b_ = np.asarray(b)
    ret = np.dot(a_, b_) / (norm(a_) * norm(b_) )

    return ret

if __name__ == '__main__':
    a = [1]
    b = [1]
    c = [2]

    print cos_sim(a,b)
    print cos_sim(a,c)

__END__ = True