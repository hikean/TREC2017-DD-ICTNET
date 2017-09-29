# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/11 上午9:17
# @version: 1.0

'''
融合多种简单的模型
外层写暴力枚举参数的程序

retrieve_docs的返回值doc_list里面是这样的：
('ebola-1bbd62fe484a96be675ab80a304f0320a742a2da67f696cde413aee99e9f9349', [79.451401, [9.644032, 12.596348, 14.692121, 10.634488], {'score': 9.644032, 'key': 'ebola-1bbd62fe484a96be675ab80a304f0320a742a2da67f696cde413aee99e9f9349'}])
最后一个dict其实是一个

'''

#TODO:好好检查一下重复，一定不要在单轮或者多轮里面出现重复

from basic_init import *
from src.utils.constants import *
from src.utils.IR_utils import *
from src.utils.JigClient import *
from src.utils.Document import *


class IRSys(object):
    def __init__(self, solrs, ws=None):
        #TODO:这里其实欠考虑，比如2个solr搜到了 而且分数很高，但是其他没有搜到呢?
        if ws is None:
            ws = [ 1.0/len(solrs) for _ in range(len(solrs)) ]

        self.ws = ws
        self.solrs = solrs


    def retrieve_docs(self, query_key_words, ret_cnt=1000, fl = 'key', query_field='content', with_query_field=False):
        '''
        :desp: 首先检索所有文档，然后求文档的并集，然后score按权重相加，然后排序
                顺便统计一下各个模型的score
        :param query_key_words:
        :param ret_cnt:
        :return:
        '''

        if with_query_field:
            fl = fl + "," + query_field.strip()

        doc_score_dict = {}
        # tot_score, score_list, d
        doc_key_set = set()
        docs_list = []
        for i, solr in enumerate(self.solrs):
            docs_list.append(
                solr.query_fields( query_key_words, query_field, fl, rows = ret_cnt )
            )
        CHECK = True
        tot_doc_cnt_before_filter = 0
        for docs in docs_list:
            for d in docs:
                #TODO:写好点
                if type(d[KEY]) == list:
                    d[KEY] = d[KEY][0]
                # else:

                if CHECK:
                    print "===> d[KEY]:", d[KEY]
                    print "d:", d
                    CHECK = False

                doc_key_set.add( d[KEY] )
                tot_doc_cnt_before_filter += 1
        logging.info("retrieve doc cnt, before filter:{0} after merge:{1}".format(tot_doc_cnt_before_filter, len(doc_key_set)) )


        CHECK = True
        for i,docs in enumerate(docs_list):
            for d in docs:
                if CHECK and i == 0:
                    print "d[KEY]", d[KEY]
                    CHECK = False

                if doc_score_dict.has_key(d[KEY]):
                    # doc_score_dict[d[KEY]] [0] += self.ws[i] * d[SCORE] / float( sum( self.ws[0:len(self.solrs)] ) )
                    # print "len(docs_list), i:", len(docs_list), i
                    doc_score_dict[d[KEY]] [0] += self.ws[i] * d[SCORE]
                    doc_score_dict[d[KEY]] [1].append( d[SCORE] )
                else:
                    doc_score_dict[d[KEY]] = [
                        # self.ws[i] * d[SCORE]  / float( sum( self.ws[0:len(self.solrs)] ) ) ,
                        self.ws[i] * d[SCORE] ,
                        [d[SCORE],],
                        d,
                    ]
        return sorted(doc_score_dict.items(), reverse=True, key=lambda v:v[1][0])[0:ret_cnt]



    #返回格式，三元组(随便什么，docno, score),输入iterms
    def items2jigdocs(self, docs_items):
        ret = []
        for d in docs_items:
            ret.append(
                ( 0, d[0], d[1][0])
            )

        return ret

    def raw2jigdocs(self, docs_items):
        ret = []
        for d in docs_items:
            ret.append(
                (  0, d[KEY], d[SCORE] )
            )

    # def item2jigdocs_with_text(self, docs_items, field = 'content'):
    #     ret = []
    #     for d in docs_items:
    #         ret.append(
    #             ( 0, d[0], d[1][0] )
    #         )


def test_full_irsys(w = None, topics=EBOLA_TOPICS):

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # solrs += [SolrClient(solr_url=SOLR_EBOLA_LMD2500)]
    w = [3, 1, 1, 1, 1, ] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    tot_itr_times = 1
    every_itr_doc_cnt = 5

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:

            logging.info("search for topic %s %s" % (tid, topic))
            #
            docs_list = irsys.retrieve_docs([topic])
            # docs_list = irsys.retrieve_docs(topic.split())

            print " =====>>>  CHECK:", docs_list[0]

            key_set = set()
            # 强制再搞一次去重
            logging.info("======> STRICT REMOVE DUP")
            print "before remove dup by key:", len(docs_list)
            new_docs_list = []
            for d in docs_list:
                key = d[0].strip()
                if key not in key_set:
                    new_docs_list.append(d)
            print "after remove dup by key:", len(new_docs_list)

            docs_list = new_docs_list

            logging.info("======> REMOVE DUP END")
            for i in range(tot_itr_times):
                jig_format_docs = irsys.items2jigdocs(docs_list)[i*every_itr_doc_cnt:i*every_itr_doc_cnt + every_itr_doc_cnt]

                print "itr:", i, " tid:", tid
                irslt = jig.run_itr(jig_format_docs, topic_id = tid)
                print "itr i:", i, " rslt:"
                if irslt is not None:
                    for _ in irslt:
                        print _
                else:
                    print None

            jig.judge()


'''
总的w之和是100 然后枚举分给各个solr
'''
def brew_search_params(tot_w = 10.0):
    st = 0
    en = int(tot_w + 1)
    for s1 in range(st, en):
        for s2 in range(st, en):
            for s3 in range(st, en):
                for s4 in range(st, en):
                    w = [s1,s2,s3,s4, tot_w - sum([s1,s2,s3,s4])]
                    test_full_irsys(w)



def test_lm_irsys(w = None, topics=EBOLA_TOPICS):

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    solrs = [
        # SolrClient(solr_url=SOLR_EBOLA_CLEAN_FULL_WITH_A)
        SolrClient(solr_url=SOLR_EBOLA_LMD2500)
    ]
    print "solr cnt:", len(solrs)
    w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    tot_itr_times = 1
    every_itr_doc_cnt = 5

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:

            logging.info("search for topic %s %s" % (tid, topic))
            #
            docs_list = irsys.retrieve_docs([topic])
            # docs_list = irsys.retrieve_docs(topic.split())

            print " =====>>>  CHECK:", docs_list[0]

            key_set = set()
            # 强制再搞一次去重
            logging.info("======> STRICT REMOVE DUP")
            print "before remove dup by key:", len(docs_list)
            new_docs_list = []
            for d in docs_list:
                key = d[0].strip()
                if key not in key_set:
                    new_docs_list.append(d)
            print "after remove dup by key:", len(new_docs_list)

            docs_list = new_docs_list

            logging.info("======> REMOVE DUP END")
            for i in range(tot_itr_times):
                jig_format_docs = irsys.items2jigdocs(docs_list)[i*every_itr_doc_cnt:i*every_itr_doc_cnt + every_itr_doc_cnt]

                print "itr:", i, " tid:", tid
                irslt = jig.run_itr(jig_format_docs, topic_id = tid)
                print "itr i:", i, " rslt:"
                if irslt is not None:
                    for _ in irslt:
                        print _
                else:
                    print None

            jig.judge()



'''
print client.query_fields_by_weight(keywords=['ebola'], query_fields=['title', 'content', 'a'], ws=[0.3, 0.7, 0.1], fl='content,key')

'''


def test_lm_weight_field(w = None, topics=EBOLA_TOPICS):

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    solrs = [
        SolrClient(solr_url=SOLR_EBOLA_CLEAN_FULL_WITH_A)
    ]
    print "solr cnt:", len(solrs)
    w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    # irsys = IRSys(solrs, ws=w)
    solr = SolrClient(solr_url=SOLR_EBOLA_CLEAN_FULL_WITH_A)

    tot_itr_times = 1
    every_itr_doc_cnt = 5

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:

            logging.info("search for topic %s %s" % (tid, topic))
            #
            docs_list = solr.query_fields_by_weight(keywords=[topic], query_fields=['title', 'content', 'a'], ws=[0.3, 0.7, 0.1], fl='key')
            # docs_list = irsys.retrieve_docs(topic.split())

            print " =====>>>  CHECK:", docs_list[0]

            key_set = set()
            # 强制再搞一次去重
            logging.info("======> STRICT REMOVE DUP")
            print "before remove dup by key:", len(docs_list)
            new_docs_list = []
            for d in docs_list:
                key = d['key'].strip()
                if key not in key_set:
                    new_docs_list.append(d)
            print "after remove dup by key:", len(new_docs_list)

            docs_list = new_docs_list

            logging.info("======> REMOVE DUP END")
            for i in range(tot_itr_times):
                st = i*every_itr_doc_cnt
                en = i*every_itr_doc_cnt + every_itr_doc_cnt
                jig_format_docs = []
                for j_ in range(st, en):
                    jig_format_docs.append(
                        (0, docs_list[j_]['key'], docs_list[j_]['score'])
                    )
                # jig_format_docs = irsys.items2jigdocs(docs_list)[i*every_itr_doc_cnt:i*every_itr_doc_cnt + every_itr_doc_cnt]

                print "itr:", i, " tid:", tid
                irslt = jig.run_itr(jig_format_docs, topic_id = tid)
                print "itr i:", i, " rslt:"
                if irslt is not None:
                    for _ in irslt:
                        print _
                else:
                    print None

            jig.judge()

if __name__ == '__main__':
    w = [3,  1, 1, 1, 1, 1]
    # EBOLA_TOPICS = [
    #     ('DD16-7', 'Urbanisation/Urbanization '),
    # ]
    test_full_irsys(w, topics=EBOLA_TOPICS)
    # test_lm_irsys(w=w, topics=EBOLA_TOPICS)

    # test_lm_weight_field()

__END__ = True