# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/6/17 下午10:42
# @version: 1.0

import nltk
from nltk.corpus import stopwords
from gensim.models.doc2vec import Doc2Vec,LabeledSentence,TaggedDocument
import re
import string

#sents是[ [词的list], [] ]每一个list表示一个文章
def sentsListToLabeledSents(sents, labels=[], label_prefix=""):
    ret_sents = []
    if labels == []:
        labels = [ str(i) for i in range(len(sents)) ]
    for i,v in enumerate(sents):
        label = '%s_%s' % (label_prefix, labels[i])
        ret_sents.append( TaggedDocument(v, [label]) )
    return ret_sents

def cleanPunctuation(line, filter_extra_space=False):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    #maketrans先把一些字符转化比如 maketrains('ABC','abc')会把
    #256个字符的ABC变成abc
    identify = string.maketrans('', '')
    cleanLine = line.translate(identify)  # 去掉ASCII 标点符号
    cleanLine = regex.sub('', cleanLine)

    if filter_extra_space:
        cleanLine = [w.strip() for w in cleanLine.split(' ') if len(w.strip()) != 0]
        cleanLine = ' '.join( cleanLine )

    return cleanLine

def file2cleansentence_en(filename, filter_extra_space=True, sp=' ') :
    ret_sent = []
    with open(filename, 'r') as f_obj:
        sens = f_obj.readlines()
        # print "SENS:", sens
        for i,s in enumerate(sens):
            s = s.strip()
            if len(s) == 0:continue
            ret_sent.append(
                cleanPunctuation(s, filter_extra_space)
            )
        return ' '.join(ret_sent)

def check_file2cleansentence_en():
    print "puncs:", string.punctuation
    filename = "/Users/zhangweimin/Desktop/TREC/Data/build_data/check_data/11100.json"
    line = file2cleansentence_en(filename)
    print [line]

if __name__ == '__main__':

    check_file2cleansentence_en()
    pass

__END__ = True