# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/25 下午9:14
# @version: 1.0


def order(mu=10):
    orde = "nohup bin/post -p 8986 -c nyt_lmd_%s /home/zhangwm/trec/datas/nonested > Log_nyt_lm_%s_sep.log 2>&1 &" % (str(mu), str(mu))

    print orde

if __name__ == '__main__':
    order(10)
    order(1500)
    order(768)


__END__ = True