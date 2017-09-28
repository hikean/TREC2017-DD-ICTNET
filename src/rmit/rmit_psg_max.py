# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/8 上午11:53
# @version: 1.0

'''
由于我们分的更细，所以方便给不同段落权重

目前做法，先按照段落匹配，每个字段都是1000篇文章，然后merge 按照score排序

'''

from basic_init import *

from src.utils.SolrClient import SolrClient
from src.utils.Document import *
from src.utils.JigClient import *



def retrieval_top_k_doc(query, solr=SolrClient(), k=RET_DOC_CNT, query_range=[ "content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"]):
    fl = 'key,doc_id'

    irdocs = []

    for v in query_range:
        logging.info("ir: " + v)
        docs = solr.query_fields(query, v, fl, rows=k)
        irdocs += docs
    print "tot ir doc cnt:", len(irdocs)

    # print docs

    return irdocs2tuple(irdocs)[0:k]

def retrieval_top_k_doc_full(query, solr=SolrClient(), k=RET_DOC_CNT, query_range=[ "content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"]):
    fl = 'key,doc_id'

    irdocs = []

    for v in query_range:
        logging.info("ir: " + v)
        docs = solr.query_fields(query, v, fl, rows=k)
        irdocs += docs
    print "tot ir doc cnt:", len(irdocs)

    # print docs

    return irdocs2tuple_full(irdocs)[0:k]

def interact_with_jig(jig, docs, interact_times=10):
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5])
        st_ptr += 5
        print "itr:", i #, " rslt:", rslt
        for _ in rslt:
            print _

def interact_with_jig_by_topic(jig, docs, interact_times=10, tid=None):
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5], topic_id=tid)
        st_ptr += 5
        print "itr:", i #, " rslt:", rslt
        for _ in rslt:
            print _

def use_psg():
    topic_query = ["US Military Crisis Response"]
    # topic_query = ["US Military Crisis Response fight combat commits against seeks"]
    # topic_query = [ "US Military Crisis Response ebola outbreak epidemic"  ]
    # topic_query = ["US Military Crisis Response ebola"] #fight combat commits against seeks" ]
    # topic_query = ["US Military Crisis Response outbreak"]
    # topic_query = [','.join(topic_query[0].split() )]
    # topic_query = [ ','.join(topic_query[0].split()  + [ "US Military", "Military Crisis", "Crisis Response", ] ) ]

    # topic_query = ["Who are key leaders (field grade officers and senior NCO’s) in charge of U.S. military units combating the ebola epidemic in Africa, what are the protocols for personnel safety, and what is their mission"]

    topic_id = "DD16-1"

    tot_itr_times = 1
    print "topic query:", topic_query

    query_range = ["content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"]
    query_range = [ "content_p",   "content_h3", "content_h4", "content_h5"]

    solr = SolrClient(BASE_SOLR_URL)
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)

    docs = retrieval_top_k_doc(topic_query, solr, 1000, query_range=query_range)
    interact_with_jig(jig, docs, tot_itr_times)

    jig.judge()


'''
第一轮
只用content_p:     all	 0.2717600	 0.2231492	 0.2789686
content_h1    all	 0.2603637	 0.1770285	 0.2667526
content_h2       all	 0.2835539	 0.2093327	 0.2899223
content_h3      all	 0.2333650	 0.1676595	 0.2396293
content_h4       all	 0.2254122	 0.1512512	 0.2320286
content_h5       all	 0.2165610	 0.1550530	 0.2230543
'''
def use_psg_all_topic():
    tot_itr_times = 1
    jig = JigClient(topic_id="DD16-1", tot_itr_times=tot_itr_times)
    solr = SolrClient(BASE_SOLR_URL)
    for topic_id, topic_query in EBOLA_TOPICS:

        print "topic query:", topic_query

        query_range = ["content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4",
                       "content_h5"]
        # query_range = ["content_h5", ]
        query_range =[ "content_p", "content_h2" ]

        print "!!!!!+++++++++++> query_range:", query_range


        docs = retrieval_top_k_doc([topic_query], solr, 1000, query_range=query_range)
        interact_with_jig_by_topic(jig, docs, tot_itr_times, tid=topic_id)

        jig.judge()

def use_full():
    topic_query = ["US Military Crisis Response"]
    # topic_query = ["Crisis Response"]

    # topic_query = [ "US Military Crisis Response ebola outbreak epidemic"  ]
    # topic_query = ["US Military Crisis Response ebola"] #fight combat commits against seeks" ]
    # topic_query = ["US Military Crisis Response outbreak"]

    # topic_query = ["Who are key leaders (field grade officers and senior NCO’s) in charge of U.S. military units combating the ebola epidemic in Africa, what are the protocols for personnel safety, and what is their mission"]

    # topic_query = ["US Military Crisis Response fight combat"]

    topic_query = [','.join(topic_query[0].split())]
    topic_id = "DD16-1"


    # topic_id, topic_query = ('DD16-26', ' African Culture') #('DD16-24', 'Olu-Ibukun Koye Spread EVD to Port Harcourt') #('DD16-3', 'healthcare impacts of ebola')
    # topic_query = [','.join(topic_query[0].split())]

    tot_itr_times = 1

    print "topic query:", topic_query

    solr = SolrClient(FULL_SOLR_URL)
    jig = JigClient(topic_id,tot_itr_times=tot_itr_times)

    docs = retrieval_top_k_doc_full(topic_query, solr, 1000, query_range=['title', 'content'])

    interact_with_jig(jig, docs, tot_itr_times)

    jig.judge()


if __name__ == '__main__':
    # use_full()
    # use_psg()
    use_psg_all_topic()


__END__ = True