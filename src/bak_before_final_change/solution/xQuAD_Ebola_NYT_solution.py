# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/26 下午12:39
# @version: 1.0

'''
为提交做的solution，及调参， 调参看act
1、只用xQuAD + 用Aspect
2、结合干净的suggestor和aspect跑xQuAD


'''

from basic_init import *
from src.utils.xQuAD import *
from src.utils.LMDirichlet import *
from src.utils.xQuAD_by_LDA import *
from ir_sys_blending import *
from src.utils.preprocess_utils import *
from src.utils.Suggestor import *
# from src.utils.data_utils import basic_preprocess
from gensim import corpora
from gensim.models import LdaModel
from xQuAD_solution import cal_dc_dicts, get_R_left, preproces_docs_list, clean_subquerys_to_query_lists_and_filter_query
from xQuAD_ebola_polar_test import clean_subquery_list
from src.utils.JIGClient_OLD import *
from xQuAD_LDA_solution import get_corpus_by_keys
from src.utils.cut_sent import *
from src.utils.xQuAD import xQuAD, cos_dis
from xQuAD_LDA_solution import get_doc_keys_from_doc_list
from xQuAD_rocchio_solution import NytKey2Id
from xQuAD_rocchio_solution import xQuAD_clean_use_local_data_without_feedback


'''
10轮：
Log_nyt_ebola_boost_xQuAD_lmd0_8_candidate20_itr10_re.log
     all	 0.0632014	 0.1418313	 0.6423097
'''

def xQuAD_feedback_ebola_nyt():
    # EBOLA_TOPICS = [
    #     ('DD16-1', 'US Military Crisis Response'),
    # ]
    # NYT_TOPICS = [
    #     # ('dd17-2', 'Who Outed Valerie Plame?'),
    #     ('dd17-4', 'Origins Tribeca Film Festival'),
    #     ('dd17-46', 'PGP')
    # ]

    tot_itr_times = 10
    xquad_lmd = 0.9
    use_jig_feedback_cnt_limit = 1
    candidate_doc_cnt = 20
    print "candidate_doc_cnt:",candidate_doc_cnt
    print "use_jig_feedback_cnt_limit:", use_jig_feedback_cnt_limit
    print "xquad_lmd:", xquad_lmd
    print "tot_itr_times:", tot_itr_times


    logging.info("tot itr times:%d" % tot_itr_times)

    logging.info( "loading key2id dict ebola nyt" )
    ebola_key2id_dict = json.load(codecs.open(FULL_KEY2ID))
    nyt_key2id_dict = NytKey2Id()

    logging.info("load stem idf dict")
    nyt_stem_idf_dict = json.load(codecs.open(nyt_idf_idf_dic_stem_clean, 'r', 'utf-8'))
    ebola_stem_idf_dict = idf_dict = json.load(codecs.open(STEM_IDF_DICT_EBOLA_CLEAN, 'r', 'utf-8'))

    logging.info("initing irsys...")
    ebola_solr_ws = [3,1,1,1,1,1]
    ebola_irsys = IRSys(get_all_ebola_solrs(), ebola_solr_ws)

    nyt_solrs_ws = [1]
    nyt_irsys = IRSys( get_all_nyt_seg_solrs(), nyt_solrs_ws )

    logging.info("initing suggestors...")
    #TODO: 这里有一些策略来过滤
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)

    logging.info("initing jig") #EBOLA_NYT_JIG_DIR
    jig = JigClient(tot_itr_times=tot_itr_times, base_jig_dir=EBOLA_NYT_JIG_DIR)

    logging.info("ebola running...")
    xQuAD_clean_use_local_data_without_feedback(topics=EBOLA_TOPICS,
                                                suggestor=suggestor,
                                                if_use_clean_text=True,
                                                boost_params=1,
                                                if_stem=True,
                                                candidate_doc_cnt=candidate_doc_cnt,
                                                tot_itr_times=tot_itr_times,
                                                every_itr_doc_cnt=5,
                                                use_subquery_cnt=5,
                                                lm_lmd=1.0,
                                                xquad_lmd=xquad_lmd,
                                                idf_dict=ebola_stem_idf_dict,
                                                jig=jig,
                                                irsys=ebola_irsys,
                                                data_dir=EBOLA_FULL_NOT_CLEAN,
                                                data_field='content',
                                                key2id_dict=ebola_key2id_dict,
                                                use_jig_feedback_cnt_limit=use_jig_feedback_cnt_limit,
                                                )
    logging.info("nyt running...")
    xQuAD_clean_use_local_data_without_feedback(topics=NYT_TOPICS,
                                                suggestor=suggestor,
                                                if_use_clean_text=True,
                                                boost_params=1,
                                                if_stem=True,
                                                candidate_doc_cnt=candidate_doc_cnt,
                                                tot_itr_times=tot_itr_times,
                                                every_itr_doc_cnt=5,
                                                use_subquery_cnt=5,
                                                lm_lmd=1.0,
                                                xquad_lmd=xquad_lmd,
                                                idf_dict=nyt_stem_idf_dict,
                                                jig=jig,
                                                irsys=nyt_irsys,
                                                data_dir=NYT_SEG_DATA_DIR,
                                                data_field='content_full_text',
                                                key2id_dict=nyt_key2id_dict,
                                                use_jig_feedback_cnt_limit=use_jig_feedback_cnt_limit,
                                                )


    jig.judge()

if __name__ == '__main__':
    xQuAD_feedback_ebola_nyt()

__END__ = True