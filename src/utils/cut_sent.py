# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/22 上午11:04
# @version: 1.0


import nltk
import nltk.data
from sample_doc import *

def splitSentence(paragraph):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(paragraph)
    return sentences

def clean_error_words_splitSentence(doc):
    doc = clean_str(doc)
    return splitSentence(unicode(doc))

def clean_str(s):
    sw = s.split()
    ret = []
    for w in sw:
        try:
            w = str(w)
            ret.append(w)
        except Exception, e:
            # print w
            pass

    return ' '.join(ret)

if __name__ == '__main__':

    print type(sample_doc)

    # sample_doc = clean_str(sample_doc)
    # sample_doc = unicode(sample_doc)
    # out = splitSentence(sample_doc)
    # print out
    # for s in out:
    #     print s

    out = clean_error_words_splitSentence(sample_doc)
    for s in out:
        print s


__END__ = True