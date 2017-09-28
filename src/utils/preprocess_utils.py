# -*- coding: utf-8 -*-
# @author: Weimin Zhang
# @date: 17/08/17

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

english_punctuations = [',', '-', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']

# def basic_preprocess(doc):
#     if type(doc) == unicode:
#         doc = doc.encode('utf8')
#     if type(doc) == str:
#         doc = doc.replace('\n', ' ')
#         doc = doc.replace('\t', ' ')
#         doc = cut_words(doc)
#     doc = remove_punctuations(doc)
#     #解决U.S. 不等于US的问题
#     doc = remove_punctuations_word_level(doc)
#     doc = remove_stop_words(doc)
#
#     return doc

def cut_words(sent, if_lower=False):
    ret = word_tokenize(sent)
    if if_lower:
        return [ w.lower() for w in ret ]
    else:
        return ret

def remove_punctuations_word_level(word_list):
    ret = []
    for w in word_list:
        nw = ''
        for c in w:
            if c not in english_punctuations:
                nw += c
        ret.append( nw )
    return ret


def remove_punctuations(word_lists):

    return [ w for w in word_lists if w not in english_punctuations ]

def remove_stop_words(doc):
    from constants import STOPWORDS
    #TODO:修改编码。。。
    return [ w for w in doc if w not in STOPWORDS ] #[ w for w in doc if w not in stopwords.words('english') ]

#TODO:做得更细致一些...
def doc2clean_words(doc):
    words = doc.split(' ')
    words = [ w.lower() for w in words ]
    return words

def cut_words(doc):
    if type(doc) == list:
        return doc
    #TODO:需要把文档都处理一遍， 以及分词不要按照空格分
    return doc.split(' ')

def mk_bigrams(doc):
    words = cut_words(doc)
    ret = []
    for i in range(len(words) - 1):
        ret.append( [words[i], words[i+1]] )
    return ret


def preprocess_query(q):
    q = q.replace('?',"")
    return q

DEFAULT_LANG = 'english'

# def is_stopwords(w, lang=DEFAULT_LANG):
#     return w.lower() in stopwords.words(lang)
#
# def remove_stopwords(words, language=DEFAULT_LANG):
#     return [_ for _ in words if _.lower() not in stopwords.words(language)]
