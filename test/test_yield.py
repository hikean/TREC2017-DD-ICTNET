# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/7/27 下午1:33
# @version: 1.0


def test_yield():
    i = 0
    while True:
        print i
        i += 1
        yield i

if __name__ == '__main__':
    g = test_yield()
    print g.next()
    print g.next()
    print g.next()

__END__ = True