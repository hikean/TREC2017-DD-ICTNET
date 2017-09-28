# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/27 下午4:06
# @version: 1.0

from xQuAD_multi_source_feedback import *


def xQuAD_Multi_source_Feedback_Ebola_NYT_1():

    EBOLA_TOPICS = [
        ('DD16-1', 'US Military Crisis Response'),
        ('DD16-3', 'healthcare impacts of ebola'),
        ('DD16-25', "Emory University's role in Ebola treatment"),
    ]
    NYT_TOPICS = [
        ('dd17-2', 'Who Outed Valerie Plame?'),
        ('dd17-46', 'PGP'),
    ]
    multi_xquad_lmd = [0.6, 0.8]
    source_weight = [0.4,0.6]
    tot_itr_times = 10
    xquad_lmd = 0.8
    use_jig_feedback_cnt_limit = 1
    candidate_doc_cnt = 30
    every_expand_words_cnt = 10
    print "candidate_doc_cnt:", candidate_doc_cnt
    print "use_jig_feedback_cnt_limit:", use_jig_feedback_cnt_limit
    print "xquad_lmd:", xquad_lmd
    print "tot_itr_times:", tot_itr_times
    print "every_expand_words_cnt:", every_expand_words_cnt
    print "multi_xquad_lmd:", multi_xquad_lmd
    print "source_weight:", source_weight

    logging.info("tot itr times:%d" % tot_itr_times)

    logging.info("loading key2id dict ebola nyt")
    ebola_key2id_dict = json.load(codecs.open(FULL_KEY2ID))
    nyt_key2id_dict = NytKey2Id()

    logging.info("load stem idf dict")
    nyt_stem_idf_dict = json.load(codecs.open(nyt_idf_idf_dic_stem_clean, 'r', 'utf-8'))
    nyt_without_stem_idf_dict = json.load(codecs.open(nyt_idf_idf_dic_nostem_clean, 'r', 'utf-8'))
    ebola_stem_idf_dict = json.load(codecs.open(STEM_IDF_DICT_EBOLA_CLEAN, 'r', 'utf-8'))
    ebola_idf_dict_without_stem = json.load(codecs.open(ebola_nostem_idf_dic_path_clean, 'r', 'utf-8'))

    logging.info("initing irsys...")
    ebola_solr_ws = [3, 1, 1, 1, 1, 1]
    ebola_irsys = IRSys(get_all_ebola_solrs(), ebola_solr_ws)

    nyt_solrs_ws = [1]
    nyt_irsys = IRSys(get_all_nyt_seg_solrs(), nyt_solrs_ws)

    logging.info("initing suggestors...")
    # TODO: 这里有一些策略来过滤
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)

    logging.info("initing jig")  # EBOLA_NYT_JIG_DIR
    jig = JigClient(tot_itr_times=tot_itr_times, base_jig_dir=EBOLA_NYT_JIG_DIR)


    logging.info("ebola ...")
    xQuAD_multisource_with_feedback(topics=EBOLA_TOPICS,
                                                                  suggestor=suggestor,
                                                                  if_use_clean_text=True,
                                                                  boost_params=1,
                                                                  if_stem=True,
                                                                  candidate_doc_cnt=30,
                                                                  tot_itr_times=tot_itr_times,
                                                                  every_itr_doc_cnt=5,
                                                                  use_subquery_cnt=5,
                                                                  lm_lmd=1.0,
                                                                  xquad_lmd=multi_xquad_lmd,
                                                                  idf_dict=ebola_stem_idf_dict,
                                                                  jig=jig,
                                                                  irsys=ebola_irsys,
                                                                  data_dir=EBOLA_FULL_NOT_CLEAN,
                                                                  data_field='content',
                                                                  key2id_dict=ebola_key2id_dict,
                                                                  use_jig_feedback_cnt_limit=2,
                                                                  query_expansion_feedback_cnt_limit=1,
                                                                  tot_retrival_doc=700,
                                                                  idf_dict_without_stem=ebola_idf_dict_without_stem,
                                                                  every_expand_words_cnt=every_expand_words_cnt,
                                                                  source_weights=source_weight
                                                                  )

    logging.info("nyt...")
    xQuAD_multisource_with_feedback(topics=NYT_TOPICS,
                                                                  suggestor=suggestor,
                                                                  if_use_clean_text=True,
                                                                  boost_params=1,
                                                                  if_stem=True,
                                                                  candidate_doc_cnt=30,
                                                                  tot_itr_times=tot_itr_times,
                                                                  every_itr_doc_cnt=5,
                                                                  use_subquery_cnt=5,
                                                                  lm_lmd=1.0,
                                                                  xquad_lmd=multi_xquad_lmd,
                                                                  idf_dict=nyt_stem_idf_dict,
                                                                  jig=jig,
                                                                  irsys=nyt_irsys,
                                                                  data_dir=NYT_SEG_DATA_DIR,
                                                                  data_field='content_full_text',
                                                                  key2id_dict=nyt_key2id_dict,
                                                                  use_jig_feedback_cnt_limit=2,
                                                                  query_expansion_feedback_cnt_limit=1,
                                                                  tot_retrival_doc=700,
                                                                  idf_dict_without_stem=nyt_without_stem_idf_dict,
                                                                  every_expand_words_cnt=every_expand_words_cnt,
                                    source_weights=source_weight
                                                                  )


def xQuAD_Multi_source_Feedback_Ebola_NYT_fix_suggested():

    # EBOLA_TOPICS = [
    #     ('DD16-1', 'US Military Crisis Response'),
    #     ('DD16-25', "Emory University's role in Ebola treatment"),
    # ]
    # NYT_TOPICS = [
    #     ('dd17-2', 'Who Outed Valerie Plame?'),
    #     ('dd17-46', 'PGP'),
    # ]
    multi_xquad_lmd = [0.6, 0.8]
    source_weight = [0.3,0.7]
    tot_itr_times = 10
    xquad_lmd = 0.8
    use_jig_feedback_cnt_limit = 2
    query_expansion_feedback_cnt_limit = 1
    candidate_doc_cnt = 30
    every_expand_words_cnt = 5
    if_use_stop_stop_strategy = True

    print "candidate_doc_cnt:", candidate_doc_cnt
    print "use_jig_feedback_cnt_limit:", use_jig_feedback_cnt_limit
    print "xquad_lmd:", xquad_lmd
    print "tot_itr_times:", tot_itr_times
    print "every_expand_words_cnt:", every_expand_words_cnt
    print "multi_xquad_lmd:", multi_xquad_lmd
    print "source_weight:", source_weight
    print "if_use_stop_stop_strategy:", if_use_stop_stop_strategy

    logging.info("tot itr times:%d" % tot_itr_times)

    logging.info("loading key2id dict ebola nyt")
    ebola_key2id_dict = json.load(codecs.open(FULL_KEY2ID))
    nyt_key2id_dict = NytKey2Id()

    logging.info("load stem idf dict")
    nyt_stem_idf_dict = json.load(codecs.open(nyt_idf_idf_dic_stem_clean, 'r', 'utf-8'))
    nyt_without_stem_idf_dict = json.load(codecs.open(nyt_idf_idf_dic_nostem_clean, 'r', 'utf-8'))
    ebola_stem_idf_dict = json.load(codecs.open(STEM_IDF_DICT_EBOLA_CLEAN, 'r', 'utf-8'))
    ebola_idf_dict_without_stem = json.load(codecs.open(ebola_nostem_idf_dic_path_clean, 'r', 'utf-8'))

    logging.info("initing irsys...")
    ebola_solr_ws = [3, 1, 1, 1, 1, 1]
    ebola_irsys = IRSys(get_all_ebola_solrs(), ebola_solr_ws)

    nyt_solrs_ws = [1]
    nyt_irsys = IRSys(get_all_nyt_seg_solrs(), nyt_solrs_ws)

    logging.info("initing suggestors...")
    # TODO: 这里有一些策略来过滤
    ebola_suggestor = SubQueryGenerator_V1(js_file=GOOGLE_SUGGESTED_V1_EBOLA)
    nyt_suggestor = SubQueryGenerator_V1(js_file=GOOGLE_SUGGESTED_V1_NYT)

    logging.info("initing jig")  # EBOLA_NYT_JIG_DIR
    jig = JigClient(tot_itr_times=tot_itr_times, base_jig_dir=EBOLA_NYT_JIG_DIR)


    logging.info("ebola ...")
    xQuAD_multisource_with_feedback(topics=EBOLA_TOPICS,
                                                                  suggestor=ebola_suggestor,
                                                                  if_use_clean_text=True,
                                                                  boost_params=1,
                                                                  if_stem=True,
                                                                  candidate_doc_cnt=30,
                                                                  tot_itr_times=tot_itr_times,
                                                                  every_itr_doc_cnt=5,
                                                                  use_subquery_cnt=5,
                                                                  lm_lmd=1.0,
                                                                  xquad_lmd=multi_xquad_lmd,
                                                                  idf_dict=ebola_stem_idf_dict,
                                                                  jig=jig,
                                                                  irsys=ebola_irsys,
                                                                  data_dir=EBOLA_FULL_NOT_CLEAN,
                                                                  data_field='content',
                                                                  key2id_dict=ebola_key2id_dict,
                                                                  use_jig_feedback_cnt_limit=use_jig_feedback_cnt_limit,
                                                                  query_expansion_feedback_cnt_limit=query_expansion_feedback_cnt_limit,
                                                                  tot_retrival_doc=700,
                                                                  idf_dict_without_stem=ebola_idf_dict_without_stem,
                                                                  every_expand_words_cnt=every_expand_words_cnt,
                                                                  source_weights=source_weight,if_use_stop_stop_strategy=if_use_stop_stop_strategy
                                                                  )

    logging.info("nyt...")
    xQuAD_multisource_with_feedback(topics=NYT_TOPICS,
                                                                  suggestor=nyt_suggestor,
                                                                  if_use_clean_text=True,
                                                                  boost_params=1,
                                                                  if_stem=True,
                                                                  candidate_doc_cnt=30,
                                                                  tot_itr_times=tot_itr_times,
                                                                  every_itr_doc_cnt=5,
                                                                  use_subquery_cnt=5,
                                                                  lm_lmd=1.0,
                                                                  xquad_lmd=multi_xquad_lmd,
                                                                  idf_dict=nyt_stem_idf_dict,
                                                                  jig=jig,
                                                                  irsys=nyt_irsys,
                                                                  data_dir=NYT_SEG_DATA_DIR,
                                                                  data_field='content_full_text',
                                                                  key2id_dict=nyt_key2id_dict,
                                                                  use_jig_feedback_cnt_limit=use_jig_feedback_cnt_limit,
                                                                  query_expansion_feedback_cnt_limit=query_expansion_feedback_cnt_limit,
                                                                  tot_retrival_doc=700,
                                                                  idf_dict_without_stem=nyt_without_stem_idf_dict,
                                                                  every_expand_words_cnt=every_expand_words_cnt,
                                    source_weights=source_weight, if_use_stop_stop_strategy=if_use_stop_stop_strategy
                                                                  )


if __name__ == '__main__':
    xQuAD_Multi_source_Feedback_Ebola_NYT_fix_suggested()

__END__ = True