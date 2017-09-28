# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/4 下午11:20
# @version: 1.0

import time

cur_time = time.asctime( time.localtime(time.time()) ).replace(' ', '_')

import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/home/zhangwm/zhangweimin/Codelibrary/TREC/src/logs/trec_dd_run'  + '_' + cur_time + '.log',
                filemode='w')

#################################################################################################
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
formatter = logging.Formatter( '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s' )
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)