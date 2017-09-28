# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/7/24 上午1:16
# @version: 1.0


if __name__ == '__main__':
    s = 'a\r t \n c\r \nb\nc'
    s1 = s.replace('\r', ' ').replace('\n', ' ')
    # s1 = s1.replace('\n', ' ')
    s2 = ' '.join([ _.strip() for _ in s1.split(' ') if len(_.strip()) != 0 ])
    print s1
    print s2


__END__ = True