# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/11 下午2:29
# @version: 1.0

from basic_init import *

from gensim.models import Word2Vec
from src.global_settings import *
from src.global_objs import global_w2v_model,get_w2v_model
from constants import *
import numpy as np

class VecUtils(object):
    def __init__(self, w2v_model_path=w2v_content_model):
        try:
            logging.info("Vec utils load model...")
            if w2v_content_model == w2v_model_path:
                self.wv_model = get_w2v_model()
            else:
                self.wv_model = Word2Vec.load(w2v_model_path)
        except Exception, e:
            logging.info("load w2v model error")

    def __getitem__(self, w):
        if self.wv_model.__contains__(w):
            return self.wv_model[w]
        else:
            return np.array([0.0] * self.wv_model.vector_size)

    def contains(self, w):
        return self.wv_model.__contains__(w)

    def doc2vec(self, doc, sp=' '):
        if type(doc) == list:
            words = doc
        else:
            words = doc.split(sp)

        ret = []
        for w in words:
            if self.wv_model.wv.__contains__(w):
                ret.append(self.wv_model[w])
                # print "get one word:", model[w]
        ret = np.asarray(ret)
        if ret.shape[0] == 0:
            return [0.0] * self.wv_model.vector_size
        else:
            return (sum(ret) / (1.0 * ret.shape[0])).tolist()

    def docs_avg_vec(self, docs):
        if len(docs) == 0: return []
        # word_lists = []
        if type(docs[0]) == list:
            word_lists = docs
        else:
            word_lists = [_.strip().split() for _ in docs if len(_.strip()) != 0]

        tot_words = []
        for d in word_lists:
            tot_words += d

        return self.doc2vec(tot_words)

    #返回值格式：[('we', 1.0), ('you', 0.7824262976646423), ('We', 0.7636411190032959)]
    def similar_by_vector(self, vec, cnt = 10):
        return self.wv_model.wv.similar_by_vector(vec, topn=cnt)

    def most_similary_vec(self, top_k=5):
        pass

    def most_similary_docs(self, top_k = 5):
        pass

if __name__ == '__main__':
    pass

__END__ = True