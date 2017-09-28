# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/12 下午3:13
# @version: 1.0

'''
针对new_york_times
使用基本检索结果做的baseline

new york times的数据辅助信息比较多...

'''

from basic_init import *
from src.utils.SolrClient import SolrClient
from src.utils.Document import *
from src.utils.JigClient import *
from src.rmit.rmit_psg_max import retrieval_top_k_doc_full, interact_with_jig
from src.utils.IR_utils import *
from ir_sys_blending import *

def nyt_seg_LMD(topic_id , query ):
    tot_itr_times = 1
    solr = SolrClient(SOLR_SEG_nyt_LMD_URL)
    jig = JigClient(topic_id=topic_id, tot_itr_times=tot_itr_times, base_jig_dir=NYT_JIG_DIR)
    print "jig dir:", jig.base_dir
    query_range = [
        # '',
        'content_full_text',
    ]

    docs = retrieval_top_k_doc_full(query, solr, k=1000, query_range=query_range)
    # interact_with_jig(jig, docs, tot_itr_times)

    st_ptr = 0

    for i in range(tot_itr_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr + 5], topic_id=topic_id)
        st_ptr += 5
        print "itr:", i  # , " rslt:", rslt
        if rslt is not None:
            for _ in rslt:
                print _
        else:
            print "None"





def base_nyt_seg_data():
    # NYT_TOPICS = [
    #     ('dd17-2', 'Who Outed Valerie Plame?'),
    # ]
    topic_id = 'dd17-1'
    # topic_name = "Return of Klimt paintings to Maria Altmann"#.split(' ')
    tot_itr_times = 1
    solr_url = SOLR_SEG_nyt_LMD768_URL
    solr = SolrClient(solr_url)

    jig = JigClient(topic_id=topic_id, tot_itr_times=tot_itr_times, base_jig_dir=NYT_JIG_DIR)
    print "jig dir:", jig.base_dir

    for topic_id, topic_name in NYT_TOPICS:
        # print topic_name
        print "topic id, topic name:", topic_id, topic_name

        query = [topic_name]
        query_range = [
            # '',
            'content_full_text',
        ]

        docs = retrieval_top_k_doc_full(query, solr, k=1000, query_range=query_range)
        # interact_with_jig(jig, docs, tot_itr_times)
        print "BEFORE REMOVE DUP:", len(docs)
        docs = remove_dup(docs)
        print "AFTER REMOVE DUP:", len(docs)

        st_ptr = 0

        for i in range(tot_itr_times):
            rslt = jig.run_itr(docs[st_ptr:st_ptr + 5], topic_id=topic_id)
            st_ptr += 5
            print "itr:", i  # , " rslt:", rslt
            if rslt is not None:
                for _ in rslt:
                    print _
            else:
                print "None"

        jig.judge()


def remove_dup(docs, idx=1):
    ret = []
    use_set = set()
    for d in docs:
        if d[idx] in use_set:
            continue
        use_set.add(d[idx])
        ret.append( d )
    return ret

def base_nyt_full_data():
    topic_id = 'dd17-1'
    # topic_name = "Return of Klimt paintings to Maria Altmann"#.split(' ')
    tot_itr_times = 1
    solr = SolrClient(SOLR_SEG_nyt_LMD_URL)
    jig = JigClient(topic_id=topic_id, tot_itr_times=tot_itr_times, base_jig_dir=NYT_JIG_DIR)
    print "jig dir:", jig.base_dir

    for topic_id, topic_name in NYT_TOPICS:
        # print topic_name
        print "topic id, topic name:", topic_id, topic_name

        query = [topic_name]
        query_range = [
            # '',
            'content',
        ]

        docs = retrieval_top_k_doc_full(query, solr, k=1000, query_range=query_range)
        # interact_with_jig(jig, docs, tot_itr_times)
        print "BEFORE REMOVE DUP:", len(docs)
        docs = remove_dup(docs)
        print "AFTER REMOVE DUP:", len(docs)


        st_ptr = 0

        for i in range(tot_itr_times):
            rslt = jig.run_itr(docs[st_ptr:st_ptr + 5], topic_id=topic_id)
            st_ptr += 5
            print "itr:", i  # , " rslt:", rslt
            if rslt is not None:
                for _ in rslt:
                    print _
            else:
                print "None"

        jig.judge()

def one_topic_test():
    topic_id = 'dd17-1'
    topic_name = "Return of Klimt paintings to Maria Altmann"  # .split(' ')
    tot_itr_times = 1
    # base_nyt_seg_data()

    nyt_seg_LMD(topic_id, [topic_name])


def nyt_irsys_blending():
    tot_itr_times = 1
    topic_id = 'dd17-1'
    ws = [3,1,1,1,1]
    jig = JigClient(topic_id=topic_id, tot_itr_times=tot_itr_times, base_jig_dir=NYT_JIG_DIR)
    solrs = get_all_nyt_solrs()
    irsys = IRSys(solrs, ws=ws)

    for topic_id, topic_name in NYT_TOPICS:
        print "topic_id, topic name:", topic_id, topic_name
        query = [topic_name]
        query_range = [
            # '',
            # 'content_full_text',
            'content',
        ]
        for i in range(tot_itr_times):
            docs = irsys.retrieve_docs(query, query_field='content', with_query_field=False)
            print "docs 0~3:", docs[0:3]
            jig_format_docs = irsys.items2jigdocs(docs)
            iresult = jig.run_itr(jig_format_docs[i*5:i*5+5], topic_id=topic_id)
            print "iresult, i:", i
            if iresult is not None:
                for _ in iresult:
                    print _
            else:
                logging.error("[ERROR] iresult None ")
        jig.judge()


def nyt_irsys_blending_sep(ws = [3.0, 1., 1., 1., 1.]):
    tot_itr_times = 2
    topic_id = 'dd17-1'

    jig = JigClient(topic_id=topic_id, tot_itr_times=tot_itr_times, base_jig_dir=NYT_JIG_DIR)
    solrs = get_all_nyt_seg_solrs()
    irsys = IRSys(solrs, ws=ws)

    for topic_id, topic_name in NYT_TOPICS:
        print "topic_id, topic name:", topic_id, topic_name
        print "w:", ws
        print "solrs:", solrs
        query = [topic_name]
        query_range = [
            # '',
            # 'content_full_text',
            'content',
        ]
        for i in range(tot_itr_times):
            docs = irsys.retrieve_docs(query, query_field='content_full_text', with_query_field=False)
            # print "docs 0~3:", docs[0:3]
            jig_format_docs = irsys.items2jigdocs(docs)
            iresult = jig.run_itr(jig_format_docs[i * 5:i * 5 + 5], topic_id=topic_id)
            print "iresult, i:", i
            if iresult is not None:
                for _ in iresult:
                    print _
            else:
                logging.error("[ERROR] iresult None ")
        if topic_id == NYT_TOPICS[-1][0]:
            print "FINAL_REAULT_TAG"
        jig.judge()



def brew_nyt_params():
    for ibs_i in range(0,3):
        for bm_i in range(0,3):
            for dfr_i in range(0, 2):
                for cla_i in range(0,2):
                    for lmjk_i in range(0,2):
                        print "PARAMAS_TAG,ibs_i, bm_i, dfr_i, cla_i, lmjk_i:", ibs_i, bm_i, dfr_i, cla_i, lmjk_i

                        ws = [ibs_i, bm_i, dfr_i, cla_i, lmjk_i]
                        if sum(ws) <=1:
                            print "sum <=1"
                            continue
                        ws = [3.0] + ws
                        nyt_irsys_blending_sep(ws)

if __name__ == '__main__':

    try:
        urls = [
            'http://172.22.0.11:8983/solr/nyt_lmd2500/select?',
            'http://172.22.0.11:8983/solr/nyt_lmd3000/select?',
            'http://172.22.0.11:8983/solr/nyt_lmd3500/select?'
        ]
        import sys
        index = int(sys.argv[1])
        global SOLR_SEG_nyt_LMD768_URL
        SOLR_SEG_nyt_LMD768_URL = urls[index]
        print SOLR_SEG_nyt_LMD768_URL
        logging.root.setLevel(logging.WARNING)
    except Exception as e:
        logging.exception("[!] Exception: %s", e)

    base_nyt_seg_data()

    # nyt_irsys_blending()
    # base_nyt_full_data()
    # nyt_irsys_blending_sep()
    # brew_nyt_params()


__END__ = True