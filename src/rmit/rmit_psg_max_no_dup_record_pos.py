# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/18 上午10:48
# @version: 1.0


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

def interact_with_jig(jig, docs, interact_times=10):
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5])
        st_ptr += 5
        print "itr:", i #, " rslt:", rslt
        for _ in rslt:
            print _

if __name__ == '__main__':

    topic_query = ["US Military Crisis Response"]
    # topic_query = [ "US Military Crisis Response ebola outbreak epidemic fight seeks spread"  ]
    # topic_query = ["US Military Crisis Response ebola"] #fight combat commits against seeks" ]
    topic_query = ["US Military Crisis Response outbreak"]

    # topic_query = ["Who are key leaders (field grade officers and senior NCO’s) in charge of U.S. military units combating the ebola epidemic in Africa, what are the protocols for personnel safety, and what is their mission"]

    topic_id = "DD16-1"

    print "topic query:", topic_query

    solr = SolrClient(BASE_SOLR_URL)
    jig = JigClient(topic_id)

    docs = retrieval_top_k_doc(topic_query, solr, 1000)
    interact_with_jig(jig, docs, 5)

    jig.judge()

__END__ = True