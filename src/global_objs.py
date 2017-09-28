# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/17 上午11:31
# @version: 1.0

'''
用于存一些可能会用到也可能不会用到的全局变量
'''

from gensim.models import Word2Vec
from basic_init import *
from global_settings import *
from src.utils.constants import w2v_content_model

global_w2v_model = None

def get_w2v_model():
    global global_w2v_model
    if global_w2v_model is None:
        try:
            logging.info("get w2v model, load w2v content model")
            global_w2v_model = Word2Vec.load(w2v_content_model)
        except Exception, e:
            logging.error("get w2v model error")

    return global_w2v_model



__END__ = True