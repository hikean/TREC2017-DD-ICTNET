# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/6/17 下午11:45
# @version: 1.0

import random

def test_shuffle():
    list = [20, 16, 10, 5]
    for i in range(4):
        random.shuffle(list)
        print list



if __name__ == '__main__':
    test_shuffle()

__END__ = True