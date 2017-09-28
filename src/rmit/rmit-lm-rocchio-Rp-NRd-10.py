# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/10 下午12:08
# @version: 1.0

from basic_init import *
from src.global_settings import *
from src.utils.w2v_utils import *
import numpy as np
from src.utils.SolrClient import SolrClient
from src.utils.Document import *
from src.utils.JigClient import *
import json
import codecs
from src.utils.rf_algorithm_utils import *
from rmit_psg_max import retrieval_top_k_doc,interact_with_jig
from src.utils.preprocess_utils import *
from src.utils.qe_algorithm_utils import *


#计算tf_idf 并按tf-idf值由大到小返回
def cal_tf_idf(idf_dic, doc, set_one=False, ret_cnt=10):

    cnt_dic = {}
    spd = doc.split(' ')
    ret_dic = {}
    ret_len = min(ret_cnt, len(spd))

    doc_len = 1.0 * len(spd)
    for w in spd:
        if len(w.strip()) == 0:continue
        try:
            w = str(w)
        except Exception, e:
            print "ERROR word:", w

        if cnt_dic.has_key(w):
            cnt_dic[w] += 1
        else:
            cnt_dic[w] = 1
    for w in spd:
        if len(w.strip()) == 0:
            continue
        if idf_dic.has_key(w):
            # print cnt_dic[w]
            # print idf_dic[w], type(idf_dic[w])
            ret_dic[w] = cnt_dic[w] * idf_dic[w] / doc_len

    ret_dic = dict( sorted(ret_dic.items(), reverse=True, key=lambda d: d[1])[0:ret_len] )

    if set_one: ret_dic = set_dic_w(ret_dic, 1.0)

    return ret_dic


def set_dic_w(dic, w=1.0):
    ret = {}
    for k in dic.keys():
        ret[k] = w
    return ret


'''
test_1:
暂时不用查询扩展
先按照字段索引段落，然后再根据tf-idf筛选出来10个词，然后修改查询向量 修改词向量的w2v， 然后做匹配


'''

def add_range(docs, field):
    ret = []
    k = QFIELD
    for d in docs:
        d[k] = field
        ret.append(d)
    return docs

def doc2tuple_with_content(doc):
    try:
        # print "doc2tuple_with_content QFIELD:", doc[QFIELD], " FIELD:" , doc[doc[QFIELD]]
        if type(doc[doc[QFIELD]]) == list: doc[doc[QFIELD]] = ' '.join(doc[doc[QFIELD]])
        if type(doc[KEY]) == list:doc[KEY] = doc[KEY][0]
        if not doc.has_key(DOC_ID): doc[DOC_ID] = 0
        return (doc[DOC_ID], doc[KEY], doc[SCORE], doc[doc[QFIELD]])
    except Exception, e:
        print "WARN:", e
        # print doc
        #TODO: 缺失字段，为什么，{'qfield': 'content_title', 'score': 4.475323, 'doc_id': 8730, 'key': 'ebola-9070355fd6319526a595a71af72767b0475a312fa6cab449737a133422cd8141'}  比如这样一个doc，为什么没有content_title
        # exit(-1)
        return None

def irdocs2tuple_with_content(docs):
    ret = set()
    key_set = set()
    error_format_doc_cnt = 0
    logging.info("irdocs2tuple_with_content before filter:" + str(len(docs)))
    for i, d in enumerate(docs):
        if i == 0:
            # print "=========>>  ", d
            pass
        if type(d[KEY]) == list:
            ikey = d[KEY][0]
        else:
            ikey = d[KEY]
        if ikey not in key_set:
            # if d[KEY] == "ebola-ae8951e07f77c9288331e546ab6349541d70d4fc0c32ca3db9c76c96b0c03c71":
            #     print "=========>>  FIND  d1"
            key_set.add(ikey)
            d = doc2tuple_with_content(d)
            if i == 0:
                print "===FULL ======>>  ", d
            # if type(d) == list: d = ' '.join(d)
            if d is not None:ret.add(d)
            else:
                error_format_doc_cnt += 1
    logging.info("ERROR FORMAT DOC FORMAT:" + str(error_format_doc_cnt))

    logging.info("irdocs2tuple_with_content after filter:" + str(len(ret)))
    ret = sorted(list(ret), key=lambda d: d[SCORE_IDX_JIG], reverse=True)

    return ret

def retrieval_top_k_doc_with_content(query, solr=SolrClient(), k=RET_DOC_CNT, query_range=[ "content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"]):
    fl = 'key,doc_id'

    irdocs = []

    for v in query_range:
        logging.info("ir: " + v)
        docs = solr.query_fields(query, v, v+','+fl, rows=k)
        if len(docs) == 0:continue
        # print docs
        add_range_docs = add_range(docs, v)
        irdocs += add_range_docs

    print "tot ir doc cnt:", len(irdocs)

    # print docs
    return irdocs2tuple_with_content(irdocs)[0:k]
    # return irdocs2tuple_with_field(irdocs)[0:k]

#传入的docs的list， 返回docs的dict key是docno val是相关的文档内容
def docs2segdic(docs):
    ret = {}
    for i,d in enumerate(docs):
        k = d[QFIELD]
        ret[d[KEY]] = d[k]

    return ret

'''
对于on topic = 0的 直接过滤掉
这里可以试验的几种思路：
（1）只是按照w2v修改查询向量然后匹配 （加或者不加tf-idf）
（2）不根据查询向量，而是根据tf-idf筛选词, 相关的加入查询， 否则剔除查询词
'''

def interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5, topic_id = 'DD16-1',query_range=[ "content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"]):

    logging.info("interact with jig...")
    rel_psgs = []
    nrel_psgs = []
    ret_rtext = set()
    ret_nrtext = set()

    update_q = query[0]


    # already_select_set = set()

    query_tf_idf = {}#cal_tf_idf(idf_dic, update_q)
    for w in update_q.split():
        query_tf_idf[w] = 1.0

    # query_tf_idf = cal_tf_idf(idf_dic, update_q)

    #存储了已经
    use_set = set()

    i_query = '，'.join(query[0].split())

    for i in range(itr_cnt):
        print "itr i:", i, [i_query]

        docs = retrieval_top_k_doc_with_content([i_query], solr, 1000, query_range=query_range)

        if i == 0:
            test_docs = docs[0:5]
            for d in test_docs:
                use_set.add(d[1])
        else:
            test_docs = []
            for d in docs:
                if d[1] in use_set:
                    continue
                use_set.add(d[1])
                test_docs.append(d)
                if len(test_docs) >= 5:break

        print "itr i:", i , " test_docs:", test_docs


        rslt = jig.run_itr( test_docs, topic_id=topic_id )
        print "itr i:", i, " rslt:"
        for _ in rslt:
            print _
        if i == itr_cnt - 1: continue

        for j,r in enumerate(rslt):
            if int(r[ON_TOPIC]) == 0:continue
            print "test docs len:", len(test_docs), j
            subs = r[SUBTOPICS]
            for s in subs:
                score = int(s[RATING])
                ret_seg = s[TEXT]
                ir_seg = test_docs[j][DOC_SEG_IDX]
                if score <= 2:
                    ret_nrtext.add( ret_seg )
                    rel_psgs.append(ir_seg)
                else:
                    ret_rtext.add( ret_seg )
                    nrel_psgs.append( ir_seg )

        i_rp = ' '.join(rel_psgs)
        i_nrp = ' '.join(nrel_psgs)

        i_rp_tfidf = cal_tf_idf(idf_dic, i_rp, set_one=True)
        i_nrp_tfidf = cal_tf_idf(idf_dic, i_nrp, set_one=True)

        query_tf_idf = rocchio_update_qurey(query_tf_idf, i_rp_tfidf, i_nrp_tfidf)

        i_query = wdic2str(query_tf_idf)

def interact_with_jig_to_change_vec_use_jig_ret(jig, solr, query, idf_dic, itr_cnt=5, topic_id = 'DD16-1', query_range=["content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"]):

    logging.info("interact with jig...")
    rel_psgs = []
    nrel_psgs = []
    ret_rtext = set()
    ret_nrtext = set()

    update_q = query[0]



    query_tf_idf = {}#cal_tf_idf(idf_dic, update_q)
    for w in update_q.split():
        query_tf_idf[w] = 1.0

    # query_tf_idf = cal_tf_idf(idf_dic, update_q)

    #存储了已经
    use_set = set()

    i_query = '，'.join(query[0].split())

    for i in range(itr_cnt):
        print "itr i:", i

        docs = retrieval_top_k_doc_with_content([i_query], solr, 1000, query_range=query_range)

        if i == 0:
            test_docs = docs[0:5]
        else:
            test_docs = []
            for d in docs:
                if d[1] in use_set:
                    continue
                use_set.add(d[1])
                test_docs.append(d)
                if len(test_docs) >= 5:break

        print "itr i:", i , " test_docs:", test_docs


        rslt = jig.run_itr( test_docs, topic_id=topic_id )
        print "itr i:", i, " rslt:"
        for _ in rslt:
            print _
        if i == itr_cnt - 1: continue

        for j,r in enumerate(rslt):
            if int(r[ON_TOPIC]) == 0:continue
            print "test docs len:", len(test_docs), j
            subs = r[SUBTOPICS]
            for s in subs:
                score = int(s[RATING])
                ret_seg = s[TEXT]
                ir_seg = test_docs[j][DOC_SEG_IDX]
                if score <= 2:
                    rel_psgs.append(ir_seg)
                    ret_rtext.add(ret_seg)
                else:
                    ret_nrtext.add(ret_seg)
                    nrel_psgs.append( ir_seg )

        i_rp = ' '.join(rel_psgs)
        i_nrp = ' '.join(nrel_psgs)

        i_rp_tfidf = cal_tf_idf(idf_dic, i_rp, set_one=True)
        i_nrp_tfidf = cal_tf_idf(idf_dic, i_nrp, set_one=True)

        query_tf_idf = rocchio_update_qurey(query_tf_idf, i_rp_tfidf, i_nrp_tfidf)

        i_ret_rp = ' '.join(list(ret_rtext))
        i_ret_nrp = ' '.join(list(ret_nrtext))
        #jig 反馈信息
        i_ret_rp_tfidf = cal_tf_idf(idf_dic, i_ret_rp, set_one=True, ret_cnt=5)
        i_ret_nrp_tfidf = cal_tf_idf(idf_dic, i_ret_nrp, set_one=True, ret_cnt=5)
        query_tf_idf = rocchio_update_qurey(query_tf_idf, i_ret_rp_tfidf, i_ret_nrp_tfidf)

        logging.info("filtering query dup words...")
        print "before filter:", len(query_tf_idf.items())
        query_tf_idf = dict(list( set( query_tf_idf.items() ) ))
        print "after filter:", len(query_tf_idf)

        i_query = wdic2str(query_tf_idf)


def interact_with_jig_to_change_vec_use_jig_ret_use_pseudo_query(jig, solr, query, idf_dic, itr_cnt=5, topic_id = 'DD16-1', query_range=["content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"], use_pseudo = False, pseudo_query = None ):

    logging.info("interact with jig...")
    rel_psgs = []
    nrel_psgs = []
    ret_rtext = set()
    ret_nrtext = set()

    update_q = query[0]



    query_tf_idf = {}#cal_tf_idf(idf_dic, update_q)
    for w in update_q.split():
        query_tf_idf[w] = 1.0

    # query_tf_idf = cal_tf_idf(idf_dic, update_q)

    #存储了已经
    use_set = set()

    i_query = '，'.join(query[0].split())



    for i in range(itr_cnt):
        print "itr i:", i
        print "DEBUG use_pseudo, pseudo_query:", use_pseudo, pseudo_query
        if i == 0 and use_pseudo and pseudo_query is not None:
            # pseudo_query = pseudo_query
            print "use pseudo query:", pseudo_query
            print "i_query:", pseudo_query
            docs = retrieval_top_k_doc_with_content([pseudo_query], solr, 1000, query_range=query_range)
        else:
            print "i_query:", i_query
            docs = retrieval_top_k_doc_with_content([i_query], solr, 1000, query_range=query_range)

        if i == 0:
            test_docs = docs[0:5]
        else:
            test_docs = []
            for d in docs:
                if d[1] in use_set:
                    continue
                use_set.add(d[1])
                test_docs.append(d)
                if len(test_docs) >= 5:break

        print "itr i:", i , " test_docs:", test_docs


        rslt = jig.run_itr( test_docs, topic_id=topic_id )
        print "itr i:", i, " rslt:"
        if rslt is None:
            logging.warn("jig ret None:", rslt)
            continue
        else:
            for _ in rslt:
                print _

        if i == itr_cnt - 1: continue

        for j,r in enumerate(rslt):
            if int(r[ON_TOPIC]) == 0:continue
            print "test docs len:", len(test_docs), j
            subs = r[SUBTOPICS]
            for s in subs:
                score = int(s[RATING])
                ret_seg = s[TEXT]
                ir_seg = test_docs[j][DOC_SEG_IDX]
                if score <= 2:
                    rel_psgs.append(ir_seg)
                    ret_rtext.add(ret_seg)
                else:
                    ret_nrtext.add(ret_seg)
                    nrel_psgs.append( ir_seg )

        i_rp = ' '.join(rel_psgs)
        i_nrp = ' '.join(nrel_psgs)

        i_rp_tfidf = cal_tf_idf(idf_dic, i_rp, set_one=True)
        i_nrp_tfidf = cal_tf_idf(idf_dic, i_nrp, set_one=True)

        query_tf_idf = rocchio_update_qurey(query_tf_idf, i_rp_tfidf, i_nrp_tfidf)

        i_ret_rp = ' '.join(list(ret_rtext))
        i_ret_nrp = ' '.join(list(ret_nrtext))
        #jig 反馈信息
        i_ret_rp_tfidf = cal_tf_idf(idf_dic, i_ret_rp, set_one=True, ret_cnt=5)
        i_ret_nrp_tfidf = cal_tf_idf(idf_dic, i_ret_nrp, set_one=True, ret_cnt=5)
        query_tf_idf = rocchio_update_qurey(query_tf_idf, i_ret_rp_tfidf, i_ret_nrp_tfidf)

        logging.info("filtering query dup words...")
        print "before filter:", len(query_tf_idf.items())
        query_tf_idf = dict(list( set( query_tf_idf.items() ) ))
        print "after filter:", len(query_tf_idf)

        i_query = wdic2str(query_tf_idf)


def interact_with_jig_to_change_vec_use_jig_ret_full(jig, solr, query, idf_dic, itr_cnt=5, topic_id = 'DD16-1', query_range=["content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"], set_one=True):

    logging.info("interact with jig...")
    rel_psgs = []
    nrel_psgs = []
    ret_rtext = set()
    ret_nrtext = set()

    update_q = query[0]



    query_tf_idf = {}#cal_tf_idf(idf_dic, update_q)
    for w in update_q.split():
        query_tf_idf[w] = 1.0

    # query_tf_idf = cal_tf_idf(idf_dic, update_q)

    #存储了已经
    use_set = set()

    # i_query = '，'.join(query[0].split())
    i_query = query[0]

    for i in range(itr_cnt):
        print "itr i, query:", i, i_query

        docs = retrieval_top_k_doc_with_content([i_query], solr, 1000, query_range=query_range)

        if i == 0:
            test_docs = docs[0:5]
            for d in test_docs:
                use_set.add(d[1])
        else:
            test_docs = []
            for d in docs:
                if d[1] in use_set:
                    continue
                use_set.add(d[1])
                test_docs.append(d)
                if len(test_docs) >= 5:break

        print "itr i:", i , " test_docs:", test_docs


        rslt = jig.run_itr( test_docs, topic_id=topic_id )
        if rslt is None:
            print "WARN None rslt:", rslt, test_docs
            continue
        print "itr i:", i, " rslt:"
        for _ in rslt:
            print _
        if i == itr_cnt - 1: continue

        for j,r in enumerate(rslt):
            if int(r[ON_TOPIC]) == 0:continue
            print "test docs len:", len(test_docs), j
            subs = r[SUBTOPICS]
            for s in subs:
                score = int(s[RATING])
                ret_seg = s[TEXT]
                ir_seg = test_docs[j][DOC_SEG_IDX]
                if score <= 2:
                    rel_psgs.append(ir_seg)
                    ret_rtext.add(ret_seg)
                else:
                    ret_nrtext.add(ret_seg)
                    nrel_psgs.append( ir_seg )

        i_rp = ' '.join(rel_psgs)
        i_nrp = ' '.join(nrel_psgs)

        i_rp_tfidf = cal_tf_idf(idf_dic, i_rp, set_one=set_one)
        i_nrp_tfidf = cal_tf_idf(idf_dic, i_nrp, set_one=set_one)

        query_tf_idf = rocchio_update_qurey(query_tf_idf, i_rp_tfidf, i_nrp_tfidf)

        i_ret_rp = ' '.join(list(ret_rtext))
        i_ret_nrp = ' '.join(list(ret_nrtext))
        #jig 反馈信息
        i_ret_rp_tfidf = cal_tf_idf(idf_dic, i_ret_rp, set_one=set_one, ret_cnt=5)
        i_ret_nrp_tfidf = cal_tf_idf(idf_dic, i_ret_nrp, set_one=set_one, ret_cnt=5)
        query_tf_idf = rocchio_update_qurey(query_tf_idf, i_ret_rp_tfidf, i_ret_nrp_tfidf)

        logging.info("filtering query dup words...")
        print "before filter:", len(query_tf_idf.items())
        query_tf_idf = dict(list( set( query_tf_idf.items() ) ))
        print "after filter:", len(query_tf_idf)

        i_query = wdic2str(query_tf_idf, sp=' ')


def test_1():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    topic_query = ["US Military Crisis Response"]

    topic_id = "DD16-1"

    print "topic query:", topic_query

    solr = SolrClient(BASE_SOLR_URL)
    # jig = JigClient(topic_id)

    irdocs = retrieval_top_k_doc_with_content(topic_query, solr, 10)

def test_2():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    topic_query = ["US Military Crisis Response"]

    topic_id = "DD16-1"

    print "topic query:", topic_query

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 5
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)

    #interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
    interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

    jig.judge()

def test_2_1():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    topic_query = ["US Military Crisis Response"]

    topic_id = "DD16-1"

    print "topic query:", topic_query

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 2
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)

    #interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
    interact_with_jig_to_change_vec_use_jig_ret(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

    jig.judge()

'''
test_3和test_2唯一的不同，就是把jig反馈的文档也作为一个文档，然后用于修改查询
'''
def test_3():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 2
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #

    for topic in EBOLA_TOPICS:
        topic_query = [ preprocess_query(topic[1]) ]
        topic_id = topic[0]

        print "topic query:", topic_query
        print "topic id:", topic_id



        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        #interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

        interact_with_jig_to_change_vec_use_jig_ret(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times, topic_id= topic_id)

        jig.judge()


#不用jig的返回文本
def test_4():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 1
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #

    for topic in EBOLA_TOPICS:
        topic_query = [ preprocess_query(topic[1]) ]
        topic_id = topic[0]

        print "topic query:", topic_query
        print "topic id:", topic_id



        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times, topic_id= topic_id)

        jig.judge()


'''
 就是把jig反馈的文档也作为一个文档，然后用于修改查询，使用full的solr
'''
def test_5():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(FULL_SOLR_URL)
    tot_itr_times = 10
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #

    for topic in EBOLA_TOPICS:
        topic_query = [ preprocess_query(topic[1]) ]
        topic_id = topic[0]

        print "topic query:", topic_query
        print "topic id:", topic_id



        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        #interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

        interact_with_jig_to_change_vec_use_jig_ret_full(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times, topic_id= topic_id, query_range=[ 'content'], set_one=True)

        jig.judge()


'''
 test_11 就是把jig反馈的文档也作为一个文档，然后用于修改查询，使用full的solr, 加上了MLT
'''
def test_11():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(FULL_SOLR_URL, mlt=True)
    tot_itr_times = 1
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #

    for topic in EBOLA_TOPICS:
        topic_query = [ preprocess_query(topic[1]) ]
        topic_id = topic[0]

        print "topic query:", topic_query
        print "topic id:", topic_id



        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        #interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

        interact_with_jig_to_change_vec_use_jig_ret_full(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times, topic_id= topic_id, query_range=[ 'content'])

        jig.judge()

'''
test_6和test_2唯一的不同，就是把jig反馈的文档也作为一个文档，然后用于修改查询, 以及不要title
'''
def test_6():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 1
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #

    for topic in EBOLA_TOPICS:
        topic_query = [ preprocess_query(topic[1]) ]
        topic_id = topic[0]

        print "topic query:", topic_query
        print "topic id:", topic_id



        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        #interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

        interact_with_jig_to_change_vec_use_jig_ret(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times, topic_id= topic_id, query_range=[  "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"])

        jig.judge()


'''
在第一轮的时候做查询扩展，先使用伪相关反馈算法

可以考虑的策略：
（1）w2v 等算法去实现
（2）设置solr score阈值来确定要不要查询扩展
（3）扩展用n-gram、RM3等
'''
'''
test_7：
使用w2v来扩展，从排名高的里面取关键词
'''
def test_7_w2v():

    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 1
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #
    vecutils = VecUtils()

    pseudo_cnt = 25
    pseudo_word_cnt = 5
    sim_limit = 0.7

    logging.info("sim_limit:" + str(sim_limit))

    for topic in EBOLA_TOPICS:
        topic_query = [preprocess_query(topic[1])]
        init_query_words = topic_query[0].split()
        topic_id = topic[0]

        print "pseudo_cnt, pseudo_word_cnt, sim_limit",pseudo_cnt, pseudo_word_cnt, sim_limit
        print "topic query:", topic_query
        print "topic id:", topic_id

        logging.info("qe...")
        qe = QE_w2v(topic_query[0], vecutils)
        pre_docs = retrieval_top_k_doc_with_content(topic_query, solr, k=pseudo_cnt, query_range=[ "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"])


        pseudo_top_doc = []
        for d in pre_docs:
            pseudo_top_doc.append( d[3] )

        pseudo_top_doc = ' '.join( pseudo_top_doc )
        query_vec = vecutils.doc2vec(topic_query[0])
        pseudo_top_doc = pseudo_top_doc.split()
        pseudo_top_words = qe.expand_by_candidate_words(query_vec, pseudo_top_doc, init_words= init_query_words,ret_cnt=pseudo_word_cnt, sim_limit=sim_limit)
        pseudoquery = word2query_by_sim(pseudo_top_words)
        pseudoquery = topic_query[0] + ' ' + pseudoquery
        print "init query before pseudoquery:", topic_query[0]
        print "form pseudoquery:", pseudoquery


        logging.info("qe end...")

        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        # interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

        interact_with_jig_to_change_vec_use_jig_ret_use_pseudo_query(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times,
                                                    topic_id=topic_id,
                                                    query_range=["content_p", "content_h1", "content_h2", "content_h3",  "content_h4", "content_h5"], use_pseudo=True, pseudo_query =pseudoquery)

        jig.judge()


'''
test_8 和 7 相比，只是把qe的算法改成tfidf的，但是还是单个词
'''
def test_8_tf_idf():

    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 1
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #
    # vecutils = VecUtils()

    pseudo_cnt = 5
    pseudo_word_cnt = 0

    for topic in EBOLA_TOPICS:
        topic_query = [preprocess_query(topic[1])]
        init_query_words = topic_query[0].split()
        topic_id = topic[0]

        print "pseudo_cnt, pseudo_word_cnt:",pseudo_cnt, pseudo_word_cnt
        print "topic query:", topic_query
        print "topic id:", topic_id

        logging.info("qe...")
        # qe = QE_w2v(topic_query[0], vecutils)
        Query_Range = ["content_p"]
        pre_docs = retrieval_top_k_doc_with_content(topic_query, solr, k=pseudo_cnt, query_range=Query_Range)


        pseudo_top_doc = []
        for d in pre_docs:
            pseudo_top_doc.append( d[3] )

        pseudo_top_doc = ' '.join( pseudo_top_doc )

        pseudo_top_doc = pseudo_top_doc.split()
        pseudo_top_words = expand_by_tfidf_candidate_words(idf_dic, init_words=init_query_words, cwords=pseudo_top_doc, ret_cnt=pseudo_word_cnt)

        pseudoquery = word2query_by_sim(pseudo_top_words)
        pseudoquery = topic_query[0] + ' ' + pseudoquery
        print "init query before pseudoquery:", topic_query[0]
        print "form pseudoquery:", pseudoquery

        logging.info("qe end...")

        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        # interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

        interact_with_jig_to_change_vec_use_jig_ret_use_pseudo_query(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times,
                                                    topic_id=topic_id,
                                                    query_range=Query_Range, use_pseudo=True, pseudo_query =pseudoquery)

        jig.judge()


'''
test_9 和 8 相比，只是把LM改成BM25
'''
def test_9_tf_idf():

    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(SOLR_BM25_URL)
    print "using BM25:", SOLR_BM25_URL
    tot_itr_times = 1
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #
    # vecutils = VecUtils()

    pseudo_cnt = 200
    pseudo_word_cnt = 10

    for topic in EBOLA_TOPICS:
        topic_query = [preprocess_query(topic[1])]
        init_query_words = topic_query[0].split()
        topic_id = topic[0]

        print "pseudo_cnt, pseudo_word_cnt:",pseudo_cnt, pseudo_word_cnt
        print "topic query:", topic_query
        print "topic id:", topic_id

        logging.info("qe...")
        # qe = QE_w2v(topic_query[0], vecutils)
        pre_docs = retrieval_top_k_doc_with_content(topic_query, solr, k=pseudo_cnt, query_range=[ "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"])


        pseudo_top_doc = []
        for d in pre_docs:
            pseudo_top_doc.append( d[3] )

        pseudo_top_doc = ' '.join( pseudo_top_doc )

        pseudo_top_doc = pseudo_top_doc.split()
        pseudo_top_words = expand_by_tfidf_candidate_words(idf_dic, init_words=init_query_words, cwords=pseudo_top_doc, ret_cnt=pseudo_word_cnt)

        pseudoquery = word2query_by_sim(pseudo_top_words)
        pseudoquery = topic_query[0] + ' ' + pseudoquery
        print "init query before pseudoquery:", topic_query[0]
        print "form pseudoquery:", pseudoquery

        logging.info("qe end...")

        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        # interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times)

        interact_with_jig_to_change_vec_use_jig_ret_use_pseudo_query(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times,
                                                    topic_id=topic_id,
                                                    query_range=["content_p", "content_h1", "content_h2", "content_h3",  "content_h4", "content_h5"], use_pseudo=True, pseudo_query =pseudoquery)

        jig.judge()


'''
test_10 第一轮不用伪相关反馈
'''
def test_10():

    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 5
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #
    # vecutils = VecUtils()

    pseudo_cnt = 5
    pseudo_word_cnt = 0

    for topic in EBOLA_TOPICS:
        topic_query = [preprocess_query(topic[1])]
        init_query_words = topic_query[0].split()
        topic_id = topic[0]

        logging.info("qe end...")

        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times, topic_id=topic_id , query_range=[  "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"])

        # interact_with_jig_to_change_vec_use_jig_ret_use_pseudo_query(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times,
        #                                             topic_id=topic_id,
        #                                             query_range=Query_Range, use_pseudo=True, pseudo_query =pseudoquery)

        jig.judge()

'''
test_11 DFR模型
'''
def test_11():
    print "before load..."
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    solr = SolrClient(SOLR_DFR_URL)
    tot_itr_times = 1
    topic_id = "DD16-1"
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)
    # topic_query = ["US Military Crisis Response"]
    #
    # vecutils = VecUtils()

    pseudo_cnt = 5
    pseudo_word_cnt = 0

    for topic in EBOLA_TOPICS:
        topic_query = [preprocess_query(topic[1])]
        init_query_words = topic_query[0].split()
        topic_id = topic[0]

        # print "pseudo_cnt, pseudo_word_cnt:",pseudo_cnt, pseudo_word_cnt
        # print "topic query:", topic_query
        # print "topic id:", topic_id
        #
        # logging.info("qe...")
        # # qe = QE_w2v(topic_query[0], vecutils)
        # Query_Range = ["content_p"]
        # pre_docs = retrieval_top_k_doc_with_content(topic_query, solr, k=pseudo_cnt, query_range=Query_Range)
        #
        #
        # pseudo_top_doc = []
        # for d in pre_docs:
        #     pseudo_top_doc.append( d[3] )
        #
        # pseudo_top_doc = ' '.join( pseudo_top_doc )
        #
        # pseudo_top_doc = pseudo_top_doc.split()
        # pseudo_top_words = expand_by_tfidf_candidate_words(idf_dic, init_words=init_query_words, cwords=pseudo_top_doc, ret_cnt=pseudo_word_cnt)
        #
        # pseudoquery = word2query_by_sim(pseudo_top_words)
        # pseudoquery = topic_query[0] + ' ' + pseudoquery
        # print "init query before pseudoquery:", topic_query[0]
        # print "form pseudoquery:", pseudoquery

        logging.info("qe end...")

        # interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        interact_with_jig_to_change_vec(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times, topic_id=topic_id , query_range=[  "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"])

        # interact_with_jig_to_change_vec_use_jig_ret_use_pseudo_query(jig, solr, topic_query, idf_dic, itr_cnt=tot_itr_times,
        #                                             topic_id=topic_id,
        #                                             query_range=Query_Range, use_pseudo=True, pseudo_query =pseudoquery)

        jig.judge()




'''
1、严格去重
2、用多个topic

'''
def test_12():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    topic_query = ["US Military Crisis Response"]

    topic_id = "DD16-1"

    print "topic query:", topic_query

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 5
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)

    for tid, topic_query in EBOLA_TOPICS:

        #interact_with_jig_to_change_vec(jig, solr, query, idf_dic, itr_cnt=5)
        interact_with_jig_to_change_vec(jig, solr, [topic_query], idf_dic, topic_id=tid, itr_cnt=tot_itr_times)

        jig.judge()


'''
查询返回 用全文检索
'''

def test_13():
    logging.info("read idf dic... ")
    idf_dic = json.load(codecs.open(idf_dic_path, 'r'))
    logging.info("load idf dic end...")

    topic_query = ["US Military Crisis Response"]

    topic_id = "DD16-1"

    print "topic query:", topic_query

    solr = SolrClient(BASE_SOLR_URL)
    tot_itr_times = 5
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)

    for tid, topic_query in EBOLA_TOPICS:
        pass
if __name__ == '__main__':

    # test_2()
    # test_2_1()
    # test_6()
    # test_4()
    # test_5()


    # test_8_tf_idf()

    # test_9_tf_idf()

    # test_10()
    #full 有mlt
    print "test 11"
    # test_11()

    # test_12()


    test_5()

__END__ = True




