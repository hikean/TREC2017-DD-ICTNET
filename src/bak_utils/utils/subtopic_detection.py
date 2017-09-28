# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/28 上午11:10
# @version: 1.0

'''
1.      CC      Coordinating conjunction 连接词
2.     CD     Cardinal number  基数词
3.     DT     Determiner  限定词（如this,that,these,those,such，不定限定词：no,some,any,each,every,enough,either,neither,all,both,half,several,many,much,(a) few,(a) little,other,another.
4.     EX     Existential there 存在句
5.     FW     Foreign word 外来词
6.     IN     Preposition or subordinating conjunction 介词或从属连词
7.     JJ     Adjective 形容词或序数词
8.     JJR     Adjective, comparative 形容词比较级
9.     JJS     Adjective, superlative 形容词最高级
10.     LS     List item marker 列表标示
11.     MD     Modal 情态助动词
12.     NN     Noun, singular or mass 常用名词 单数形式
13.     NNS     Noun, plural  常用名词 复数形式
14.     NNP     Proper noun, singular  专有名词，单数形式
15.     NNPS     Proper noun, plural  专有名词，复数形式
16.     PDT     Predeterminer 前位限定词
17.     POS     Possessive ending 所有格结束词
18.     PRP     Personal pronoun 人称代词
19.     PRP$     Possessive pronoun 所有格代名词
20.     RB     Adverb 副词
21.     RBR     Adverb, comparative 副词比较级
22.     RBS     Adverb, superlative 副词最高级
23.     RP     Particle 小品词
24.     SYM     Symbol 符号
25.     TO     to 作为介词或不定式格式
26.     UH     Interjection 感叹词
27.     VB     Verb, base form 动词基本形式
28.     VBD     Verb, past tense 动词过去式
29.     VBG     Verb, gerund or present participle 动名词和现在分词
30.     VBN     Verb, past participle 过去分词
31.     VBP     Verb, non-3rd person singular present 动词非第三人称单数
32.     VBZ     Verb, 3rd person singular present 动词第三人称单数
33.     WDT     Wh-determiner 限定词（如关系限定词：whose,which.疑问限定词：what,which,whose.）
34.     WP      Wh-pronoun 代词（who whose which）
35.     WP$     Possessive wh-pronoun 所有格代词
36.     WRB     Wh-adverb   疑问代词（how where when）


'''

'''
程序逻辑：
 (0) 检索出来top-N
（1）先对query按照pattern和text匹配 筛选出来三种sub-query candidates
（2）再对sub-query candidates根据文档频率筛选，这里有点矛盾的地方，暂时两种方法都试试，1)强制只筛选出来一个query-left和一个query-right， 2)所有大于50%的晒出来，不强制1)但是根据一些条件筛选一下***
（3）对（2）的筛选结果做SS的筛选，这样已经能筛选出来primary的sub-query了，
（4）递归调用上面过程 得到secondary sub-query

'''

import nltk
import numpy as np
from basic_init import *
from src.global_settings import *
from repattern import *
import copy

def isN(tag):
    return tag in ["NN", "NNS", "NNP", "NNPS" ]

def isAdj(tag):
    return tag in ["JJ", "JJR", "JJS"]


def get_noun(text):
    text = nltk.word_tokenize(text)
    pos = nltk.pos_tag(text)
    ret = []
    for id,p in pos:
        if isN(p):
            ret.append( (id, p) )

    return ret

#只要每个词都在里面都认为match
def match_by_word_in(q, d, sp=' '):
    qw = q.split(sp)
    for w in qw:
        if w.strip() not in d:
            return False
    return True

def appear_cnt(query, docs, field="content"):
    cnt = 0
    for d in docs:
        if match_by_word_in(query, d):
        # if query in d[field]:
            cnt += 1
    return cnt

#这里的solr屏蔽掉细节（Full 还是字段, 这里的k=300可能有点小
def get_docs_keys(docs):
    keys = []
    for d in docs:
        keys.append( d['key'] )
    return keys

def get_docs_by_keys(docs, keys):
    ret = []
    for d in docs:
        if d['key'] in keys:
            ret.append( d )
    return ret

def doc2sent(text, split_tag=['.', '?', '!', '\n', ]):

    sent = []
    st_idx = 0
    for i,c in enumerate(text.strip()):
        if c in split_tag:
            sent.append( text[st_idx:i].strip() )
            st_idx = i + 1



#按照key去重
def set_intersection(a,b):
    ret = []
    return ret

def set_union(a,b):
    ret = []
    return ret

def get_D_sc_keys(st, D_st):

    ret = set()
    for (k, v) in D_st.items():
        if k != D_st:
            for d in v:
                ret.add(d['key'])

    return ret

#计算 Distinctness Entropy (DE)
def cal_DE(D_st):
    # if len(D_st[st]) == 0: return 0
    de = 0

    for (k, v) in D_st.items():
        D_st_keys = get_docs_keys(v)
        D_sc_keys = get_D_sc_keys(k, D_st)
        intersection = set(D_sc_keys) & set(D_st_keys)
        if len(D_st_keys) == 0:
            print "cal_DE: len(D_st_keys) == 0, st", k
            continue

        sv = len(intersection) / float(len(D_st_keys))
        #TODO: 这里的log...log10????
        de += sv * np.log(sv)

    return de

#D_st_cnt表示的是D_st的并集的元素个数之和
def cal_ss(st, D_st, USC, D_st_cnt):

    D_st_ele = D_st[st]
    USC_keys = get_docs_keys(USC)
    D_st_ele_keys = get_docs_keys(D_st_ele)
    join_key_set = set_intersection(USC_keys, D_st_ele_keys)

    #Coverage(st,US)
    cover_ratio = float( len(join_key_set) ) / D_st_cnt

    if cover_ratio == 0:
        print "cover ratio 0, st:", st
        return 0.0
    else:
        return cover_ratio * cal_DE(D_st)

def select_st_by_ss(D_st, USC, L, D_st_cnt):
    keys = set(D_st.keys()) - set(L)
    ss_list = []
    for k in keys:
        ss = cal_ss(k, D_st, USC, D_st_cnt)
        ss_list.append( [k, ss, ] )
    sorted(ss_list, key=lambda t:t[1], reverse=True)
    if len(ss_list) > 0:
        return ss_list[0]
    else:
        return None

def get_USC(R_keys, US):
    ret = []
    R_keys = set(R_keys)
    for (k, v) in US.items():
        for d in v:
            if d['key'] not in R_keys:
                ret.append(d)
    return ret

#D_st_cnt是D_st的并集的文章个数,D_st有可能重复
def subtopic_selection(R, D_st={}, D_st_cnt = 0):
    US = {}
    R_keys = get_docs_keys(R)

    L = []
    while len(US) < len(D_st):
        USC = get_USC(R_keys, US)
        st = select_st_by_ss(D_st, USC, L, D_st_cnt)
        # st_keys = get_docs_keys(D_st[st])
        L.append(st)
        US[st] = D_st[st]
    return L


'''
伪码中说的HR应该就是top-N文档，这里用R代替
K是最终要留下的subtopic的个数
'''
def subtopic_ranking(R, D_st={}, D_st_cnt = 0, K=5):

    # L = subtopic_mining_by_full()

    pass

def primary_subtopic_mining_by_full(query, solr, k = 300, query_field="content", appear_ratio = 0.5):

    rdocs = solr.retrive_top_k_docs(keywords=[query,], rcnt=k, query_field=query_field)
    rdocs_keys = get_docs_keys(rdocs)

    raw_candidate_topics = []
    D_st = {}
    D_st_keys_set = set()
    # primary_querys = []
    # q_left = []
    # q_right = []
    less_than_half_cnt = 0

    for d in rdocs:
        text = d[query_field]
        cqs = extract_subtopic_candidate(text, query)
        for cq in cqs:
            cnt = appear_cnt(cq[0], rdocs, field=query_field)
            if float(cnt) / len(rdocs) >= appear_ratio:
                raw_candidate_topics.append(cq[0])
                #TODO:分几种pattern, 以及merge一次
            else:
                less_than_half_cnt += 1

    logging.info("less than half cnt:" + str(less_than_half_cnt))
    print "tot candidate query cnt:", len(raw_candidate_topics)
    logging.info("retrive candidate docs...")
    for cq in raw_candidate_topics:
        #这里本来是能检索到的在top-k里面的文档，但是这里我写的是，先用subtopic取出来k个文档，然后看是不是在top-k里面
        #TODO:这里相当于给了用原始query查询的结果很大权重，而原始查询出来的top-k不一定靠谱
        cq_rdocs = solr.retrive_top_k_docs(keywords=[cq], rcnt=k, query_field=query_field)
        cq_keys = get_docs_keys(cq_rdocs)
        D_st_keys_set += set(cq_keys)
        D_st[cq] = get_docs_keys(rdocs, cq_keys)

    logging.info("start select topics...")
    print "params:"
    print "R cnt:", len(rdocs)
    print "candidate topics:", len(raw_candidate_topics)
    print "D_st docs:", len(D_st_keys_set)
    L = subtopic_selection(rdocs, raw_candidate_topics, D_st, len(D_st_keys_set))

    # PS = copy.deepcopy(L)
    return L

'''
返回primary和secondary
'''
def secondary_subtopic_mining_by_full(init_query, solr, k = 300, query_field="content", appear_ratio = 0.5):
    L_primary = primary_subtopic_mining_by_full(init_query, solr, k = 300, query_field="content", appear_ratio = 0.5)
    secondary_subtopic_list = []
    secondary_subtopic_dic = {}
    for subquery, ss in L_primary:
        logging.info("cal subquery: " + subquery)
        secondary_subtopic_dic[subquery] = primary_subtopic_mining_by_full(subquery, solr, k, query_field, appear_ratio)
        secondary_subtopic_list += secondary_subtopic_dic[subquery]

    print "sort..."
    secondary_subtopic_list = sorted(secondary_subtopic_list, reverse=True, key=lambda d:d[1])

    return L_primary, secondary_subtopic_list, secondary_subtopic_dic


if __name__ == '__main__':
    pass




__END__ = True