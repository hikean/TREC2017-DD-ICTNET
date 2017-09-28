
# -*- encoding: utf-8 -*-

import json
import sys
# import os
# import codecs
import re
from collections import Counter
from nltk import ngrams
import math


class LangModel(object):
    "language model"

    def __init__(self, model=None, ngram=(1,), miu=200.0):
        self.ngram, self.model = ngram, model
        self.msum = 1e-9
        if model is not None:
            self.msum = sum(model.values())
        self.miu = miu

    def make_ngram(self, words, ngram=None):
        if ngram is None:
            ngram = self.ngram
        if isinstance(words, str):
            words = LangModel.cut_words(words)
        return [x for n in ngram for x in ngrams(words, n)]

    def get_FwC(self, word):
        if self.model is None:
            raise ValueError("self.model is None")
        return self.model.get(word, 0)

    def get_PwC(self, key):
        return self.model.get(key, 0.0) / (self.msum * 1.0)

    def model_loads(self, model_json):
        self.model = json.lodas(model_json)
        self.msum = sum(self.model.values())

    def model_load(self, file_name):
        self.model_loads(open(file_name, "r").read())

    @staticmethod
    def cut_words(document):
        return re.findall(r"\w+", document.lower(), re.UNICODE)

    def make_probability(self, document=None, words=None, ngram=None):
        return LangModel.normalize(self.make_counter(document, words, ngram))

    def make_counter(self, document=None, words=None, ngram=None):
        if isinstance(document, dict):
            return document
        if document is None and not isinstance(words, list):
            raise ValueError("wrong arguments passed")
        if isinstance(document, str):
            words = LangModel.cut_words(document)
        elif isinstance(document, list):
            words = document
        ngram_words = self.make_ngram(words, ngram)
        return Counter(ngram_words)

    def compute_score(self, f_document, f_query,
                      smooth=lambda a, b: (a + 1.0) / (b + 1.0)):
        dsum, qsum = sum(f_document.values()), sum(f_query.values())
        PwQ = {key: smooth(f_query.get(key, 0.0), qsum) for key in f_query}
        return sum([
            PwQ[key] * math.log(PwQ[key] / (
                smooth(f_document.get(key, 0.0), dsum))) for key in PwQ
        ])

    def score_DQ(self, document, query, ngram=None):
        if isinstance(document, str) and isinstance(query, str):
            document = LangModel.cut_words(document)
            query = LangModel.cut_words(query)
        elif not isinstance(document, list) or not isinstance(query, list):
            raise ValueError("document and query should be the same type")
        d_counter = Counter(self.make_ngram(document, ngram))
        q_counter = Counter(self.make_ngram(query, ngram))
        return self.compute_score(d_counter, q_counter)

    @staticmethod
    def normalize(dct, smooth=lambda a, b: float(a) / float(b)):
        total = sum([dct[key] for key in dct])
        return {key: smooth(dct[key], total) for key in dct}

    def calcu_PQD(documentc, queryc):
        dsum = sum(documentc.values())
        ndoc = len(documentc)
        probability = 1.0
        for gram in queryc:
            probability *= (
                ((documentc.get(gram, 0) + 1.0) / (dsum + ndoc)) **
                queryc.get(gram))
        return probability

    def compute_PQD(self, documents, query, ngram=None,
                    smooth=lambda a, b: (a + 1.0) / (b + 1.0)):
        counters = {k: self.make_counter(document=documents[k], ngram=ngram)
                    for k in documents}
        qcounter = self.make_counter(query)
        return {k: self.calcu_PQD(counters[k], qcounter) for k in counters}
        raise ValueError("Function Needs To Be Implemented")

    def compute_PwD(self, document, miu):


    def compute_PwR(self, documents, query, PQD, ngram=None):
        """documents should be {key: documents_words}"""
        p_documents = {key: self.make_probability(
            document=documents[key], ngram=ngram)
            for key in documents
        }
        grams = set([
            gram for doc in p_documents for gram in p_documents[doc].keys()])
        return {gram: sum([
            p_documents[doc].get(gram, 0.0) * PQD.get(doc)
            for doc in documents]) for gram in grams
        }

    def update_PwR(self, PwR, PwQ, lmbd=0.5):
        return {
            gram: lmbd * PwR.get(gram, 0) + (1 - lmbd) * PwQ.get(gram, 0)
            for gram in PwR
        }

    def get_candidate_words(self, documents, query, ignorecase=False):
        """use documents and query caculate the relative words to expand query
        documents should be {doc_id: doc_text_string} or {doc_id: [doc_word]}
        query should be string or [query word]
        """
        pass


def main():

    lang = LangModel()
    document = "12 3 4 5 5  5"
    documents = {0: document}
    query = "1 2 2 2 12"
    print lang.compute_PQD(
        documents, query), lang.compute_PwR(documents, query)
    print lang.score_DQ(document, query)


if __name__ == "main":
    main()

