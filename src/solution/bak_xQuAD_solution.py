# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/13 上午12:39
# @version: 1.0

#TODO:!!!一定要注意去重
'''

文件格式：('ebola-1bbd62fe484a96be675ab80a304f0320a742a2da67f696cde413aee99e9f9349', [79.451401, [9.644032, 12.596348, 14.692121, 10.634488], {'score': 9.644032, 'key': 'ebola-1bbd62fe484a96be675ab80a304f0320a742a2da67f696cde413aee99e9f9349'}])


文本的预处理在本文件做了，也就是里面的d是包含了处理过的doc的。。。

可以实现的几个版本:
1、每次用richoo...更新查询，这个可能不好。。
2、一次性的
3、related和suggested合并



===
其中 没有clean的model是没有做小写的

'''

from basic_init import *
from src.utils.xQuAD import *
from src.utils.LMDirichlet import *
from ir_sys_blending import *
from src.utils.preprocess_utils import *
from src.utils.Suggestor import *



def cal_dc_dicts(doclists, content_field='content'):
    '''
    :param doclists:
    :return: 返回dict, k: key, v: word_list
    '''
    logging.info("cal dc dicts, doc cnt: %d" % len(doclists))
    ret = {}
    for d in doclists:
        dc = defaultdict(int)
        for w in d[1][2][content_field]:
            dc[w] += 1.0
        key = d[0]
        ret[key] = dc

    return ret

#还是在SolrClient中改把、。。
def append_doc_content(doc_list):
    '''
    :param doc_list:根据key从本地访问数据
    :return:
    '''
    pass



def clean_subquerys_to_query_lists(subquerys):
    ret = []
    for q in subquerys:
        ret.append( basic_preprocess(q) )

    return ret

def get_R_left(doc_list, selected_key_set):
    ret = []
    for d in doc_list:
        if d[0] not in selected_key_set:
            ret.append( d[1][2] )
            ret[-1][SCORE] = d[1][0]
        if len(ret) == 1:
            print '====> CHECK get R left:', ret[-1]
            # print ret[-1]['key']
    if len(ret) == 0:
        print "[ERROR] when cal R_left"
    return ret

def preproces_docs_list(docs_list, field='content'):
    for i in range(len(docs_list)):
        docs_list[i][1][2][field] = basic_preprocess(docs_list[i][1][2][field])
    return docs_list


def xQuAD_by_IRSys_ebola_without_query_feedback(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1e11):
    logging.info("loading... LMD...")
    lm = LMDirichlet()
    if if_use_clean_text:
        lm.load(LMDirichlet_clean_Json)
    else:
        lm.load(LMDirichlet_Json)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=0.5, alpha=0.5)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    tot_itr_times = 5
    every_itr_doc_cnt = 5

    jig = JigClient(tot_itr_times=tot_itr_times)

    # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
    already_select_key_set = set()
    D = []

    for tid, topic in topics:
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            query_word_list = basic_preprocess(topic)
            print "query_word_list:", query_word_list

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)
            docs_list = preproces_docs_list(docs_list)[0:1000]

            logging.info("cal dcs...")
            dcs_dict = cal_dc_dicts(docs_list)


            key_set = set()
            #强制再搞一次去重
            logging.info("======> STRICT REMOVE DUP")
            print "before remove dup by key:", len(docs_list)
            new_docs_list = []
            for d in docs_list:
                key = d[0].strip()
                if key not in key_set:
                    new_docs_list.append(d)
            print "after remove dup by key:", len(new_docs_list)

            logging.info("======> REMOVE DUP END")

            docs_list = new_docs_list
            file_ptr = 0
            for i in range(tot_itr_times):
                print "itr:", i, " tid:", tid
                this_itr_select_docs = []
                if i == 0:
                    print docs_list[0]
                    while len(this_itr_select_docs) < 5  and file_ptr < len(docs_list):
                        if docs_list[file_ptr][0] in already_select_key_set:
                            continue
                        this_itr_select_docs.append( docs_list[file_ptr][1][2] )
                        already_select_key_set.add( docs_list[file_ptr][1][2]['key'] )
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    jig.run_itr(jig_format_docs, topic_id=tid)
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    docs_left = docs_list[file_ptr:]
                    R_left = get_R_left(docs_left, already_select_key_set)

                    subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:5]

                    subquerys = clean_subquerys_to_query_lists(subquerys)
                    print "===> subqueries:", subquerys

                    ranked_docs = xquad.select_doc_u(query_word_list, R_left, D, subquerys)

                    for d in ranked_docs[0:5]:
                        D.append( d[0] )
                        D[-1][SCORE] = d[1]

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )

                    jig.run_itr(jig_format_docs, topic_id=tid)


    jig.judge()

def test_1():
    suggestor = SubQueryGenerator_by_title(TITLE_BING)
    xQuAD_by_IRSys_ebola_without_query_feedback(topics=EBOLA_TOPICS, suggestor=suggestor)


if __name__ == '__main__':
    test_1()

__END__ = True