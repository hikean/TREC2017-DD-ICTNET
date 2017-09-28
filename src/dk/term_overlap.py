import json
import codecs
import sys
import jieba
from gensim.models import Word2Vec


stopword = [line.strip() for line in codecs.open('data/stopwords.txt',encoding='UTF-8').readlines()];

def substring_match(str_query,int_doc_id):
    list_query_pre = jieba.cut(str_query,cut_all=False)
    list_query = []
    for word in list_query_pre:
        if (word not in stopword) and (len(word) > 1):
            list_query.append(word)
    
    json_doc = json.load(codecs.open("data/clean_ebola_json/{}.json".format(int_doc_id) ) )
    list_doc_word_pre = jieba.cut(json_doc["content_p"],cut_all=False)
    list_doc_word = []
    for word in list_doc_word_pre:
        if (word not in stopword) and (len(word) > 1):
            list_doc_word.append(word)
    
    int_ans = 0
    for word in list_query:
        if word in list_doc_word:
            int_ans = 1
            break
        
    return int_ans

def term_overlap(str_query,int_doc_id):
    
    list_query_pre = jieba.cut(str_query,cut_all=False)
    list_query = []
    for word in list_query_pre:
        if (word not in stopword) and (len(word) > 1):
            list_query.append(word)
    
    json_doc = json.load(codecs.open("data/clean_ebola_json/{}.json".format(int_doc_id) ) )
    list_doc_word_pre = jieba.cut(json_doc["content_p"],cut_all=False)
    list_doc_word = []
    for word in list_doc_word_pre:
        if (word not in stopword) and (len(word) > 1):
            list_doc_word.append(word)
    
    n_include = 0.0
    n_word = 0.0
    for word in list_query:
        n_word += 1.0
        if word in list_doc_word:
            n_include += 1.0
        
    return n_include/n_word

def term_synonym_overlap(str_query,int_doc_id):
    
    model_path = "/home/zhangwm/zhangweimin/Data/trec/build_data/ebola/textmodel/content_w2v.model"
    model = Word2Vec.load(model_path)
    
    list_query_pre = jieba.cut(str_query,cut_all=False)
    list_query = []
    for word in list_query_pre:
        if (word not in stopword) and (len(word) > 1):
            list_query.append(word)
    
    json_doc = json.load(codecs.open("data/clean_ebola_json/{}.json".format(int_doc_id) ) )
    list_doc_word_pre = jieba.cut(json_doc["content_p"],cut_all=False)
    list_doc_word = []
    for word in list_doc_word_pre:
        if (word not in stopword) and (len(word) > 1):
            list_doc_word.append(word)
    
    n_include = 0.0
    n_word = 0.0
    for word in list_query:
        n_word += 1.0
        list_synonym = model.similar_by_word(word)
        
        for tuple_syn_word in list_synonym:
            if tuple_syn_word[0] in list_doc_word:
                n_include += 1.0
                break
        
    return n_include/n_word
    
if __name__ == '__main__':
    test_substring_match = substring_match("ha,ta ge",1)
    test_term_overlap = term_overlap("ha,ta ge",1)
    test_term_synonym_overlap = term_synonym_overlap("ha,ta ge",1)
    
    print(test_substring_match,test_substring_match,test_term_synonym_overlap)
    