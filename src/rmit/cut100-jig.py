from basic_init import *

import codecs
import json
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
    print ("tot ir doc cnt:", len(irdocs))

    # print docs

    return irdocs2tuple(irdocs)[0:k]

def interact_with_jig(jig, docs, interact_times=10):
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5])
        st_ptr += 5
        print ("itr:", i) #, " rslt:", rslt
        for _ in rslt:
            print (_)
            
if __name__ == '__main__':

    topic_query = ["US,Military,Crisis,Response"]
    topic_query = [','.join(topic_query[0].split() )]
    topic_id = "DD16-1"

    tot_itr_times = 1

    #solr = SolrClient("http://172.22.0.11:8983/solr/ebola_extract/select?")
    solr = SolrClient("http://10.61.2.168:8989/solr/ebola_paragraph/select?")
    jig = JigClient(topic_id, tot_itr_times=tot_itr_times)

    docs = retrieval_top_k_doc(topic_query, solr, 1000)
    interact_with_jig(jig, docs, tot_itr_times)

    jig.judge()
    dict = jig.get_result_dict()
    
    #fl = codecs.open("dict.txt", "w", "utf-8")
    #fl.write(json.dumps(dict))

    print(dict)

__END__ = True
