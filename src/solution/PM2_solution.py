# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/17 下午3:04
# @version: 1.0

#TODO: 记录一下xQuAD两边的分数值的比例...
'''
从第三轮开始XXX...
'''

from basic_init import *
from src.utils.xQuAD import *
from src.utils.LMDirichlet import *
from ir_sys_blending import *
from src.utils.preprocess_utils import *
from src.utils.Suggestor import *
from src.utils.PM2 import *
from xQuAD_solution import cal_dc_dicts, clean_subquerys_to_query_lists, get_R_left, preproces_docs_list

def get_vs_by_rank(tot_vs=[]):
    pass


def PM2_by_IRSyS_without_query_feedback(
        topics=EBOLA_TOPICS,
        w = None,
        suggestor=None,
        if_use_clean_text=False,
        boost_params=1e11,
        tot_itr_times = 2,
        every_itr_doc_cnt = 5,
        use_subquery_cnt = 5,
        result_div_lmd = 0.5,
        lm_lmd = 2000.0):
    logging.info("init IR sys...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    irsys = IRSys(solrs, ws=w)

    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        lm.load(LMDirichlet_clean_Json)
    else:
        lm.load(LMDirichlet_Json)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
        print "tot_itr_times:", tot_itr_times
        print "every_itr_doc_cnt:", every_itr_doc_cnt
        print "use_subquery_cnt:", use_subquery_cnt
        print "lm_lmd:", lm_lmd
        print "result_div_lmd:", result_div_lmd

        logging.info("prepare data for %s" % topic)
        already_select_key_set = set()
        D = []
        #TODO 求vs... 还是按照subquery的能检索出来的东西来算
        subquerys_vs = []
        subquerys = suggestor.get_subquery_by_topic_id(tid)
        logging.info("init PM2 for %s" % topic)
        docs_list = irsys.retrieve_docs([topic], with_query_field=
                                       True)[0:1000]
        docs_list = preproces_docs_list(docs_list)
        R_left = get_R_left(docs_list, already_select_key_set)
        pm2 = PM2(subquerys, subquerys_vs, R_left, lmd=result_div_lmd)

        for i in range(tot_itr_times):
            if i == 0:
                file_cnt = 0
                for _ in docs_list:
                    if _[0] not in already_select_key_set:
                        already_select_key_set.add(_)
                        D.append(docs_list[1][2][KEY])
                        R_left.remove(_[1][2])
                        file_cnt += 1
                        if file_cnt >= every_itr_doc_cnt: break
            # elif i == 1:
            else:
                #TODO:根据迭代的轮次做修改
                subquerys = suggestor.get_subquery_by_topic_id(tid)
                ranked_docs = pm2.select_doc()


if __name__ == '__main__':
    pass

__END__ = True