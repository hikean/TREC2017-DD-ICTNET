# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/7/28 下午8:46
# @version: 1.0

import numpy as np
# from sklearn.model_selection import train_test_split

a = [
    [1,2],
    [3,4,5],
    [6,7,8,9],
]

c = [
    [-1,2],
    [3,24,5],
    [6,37,58,79],
]

y = [0,1,0]


b = np.array(a)

# print b.dtype

print type(b)
print type(b[0])
print type(b[0][0])


def test_avg():
    a = [
        [1, 2,3.6],
        [3, 4, 5],
        [6, 7, 8,],
    ]

    a = np.asarray(a)
    print sum(a) /(1.0 * a.shape[0])

test_avg()
if __name__ == '__main__':
    pass

__END__ = True