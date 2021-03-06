# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/28 下午9:50
# @version: 1.0


from xQuAD_multi_source_feedback import *
from xQuAD_with_feedback_tc_algorithms import *


def submission_xQuAD_rocchio_tc_solution(
        xquad_lmd=0.6, e_cnt=5, c_doc_cnt=30):

    # EBOLA_TOPICS = [
    #     # ('DD16-1', 'US Military Crisis Response'),
    #     # ('DD16-3', 'healthcare impacts of ebola'),
    #     ('DD16-25', "Emory University's role in Ebola treatment"),
    # ]
    # NYT_TOPICS = [
    #     ('dd17-2', 'Who Outed Valerie Plame?'),
    #     ('dd17-46', 'PGP'),
    # ]
    # xquad_lmd =  0.6  # 0.5-0.9  0.6 +-%5 <1>
    multi_xquad_lmd = [0.6, xquad_lmd]  #
    source_weight = [0, 1]
    tot_itr_times = 10
    use_jig_feedback_cnt_limit = 2
    query_expansion_feedback_cnt_limit = 1
    candidate_doc_cnt = c_doc_cnt  # 30 # 25 35  <4>
    every_expand_words_cnt = e_cnt  # 5 # 3 6 <3>
    if_use_stop_stop_strategy = False


# def submission_xQuAD_rocchio_tc_solution():
#     xquad_lmd = 0.8
#     multi_xquad_lmd = [0.6, xquad_lmd]
#     source_weight = [0, 1.0]
#     tot_itr_times = 10

#     use_jig_feedback_cnt_limit = 2
#     query_expansion_feedback_cnt_limit = 1
#     candidate_doc_cnt = 30
#     every_expand_words_cnt = 5
#     if_use_stop_stop_strategy = True

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
    nyt_stem_idf_dict = json.load(codecs.open(
        nyt_idf_idf_dic_stem_clean, 'r', 'utf-8'))
    nyt_without_stem_idf_dict = json.load(
        codecs.open(nyt_idf_idf_dic_nostem_clean, 'r', 'utf-8'))
    ebola_stem_idf_dict = json.load(codecs.open(
        STEM_IDF_DICT_EBOLA_CLEAN, 'r', 'utf-8'))
    ebola_idf_dict_without_stem = json.load(
        codecs.open(ebola_nostem_idf_dic_path_clean, 'r', 'utf-8'))

    logging.info("initing irsys...")
    ebola_solr_ws = [3, 1, 1, 1, 1, 1]
    ebola_irsys = IRSys(get_all_ebola_solrs(), ebola_solr_ws)

    nyt_solrs_ws = [1]
    nyt_irsys = IRSys(get_all_nyt_seg_solrs(), nyt_solrs_ws)

    logging.info("initing suggestors...")
    # TODO: 这里有一些策略来过滤
    # ebola_suggestor = SubQueryGenerator_V1(js_file=GOOGLE_SUGGESTED_V1_EBOLA)
    # nyt_suggestor = SubQueryGenerator_V1(js_file=GOOGLE_SUGGESTED_V1_NYT)
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)

    logging.info("initing jig")  # EBOLA_NYT_JIG_DIR
    jig = JigClient(tot_itr_times=tot_itr_times,
                    base_jig_dir=EBOLA_NYT_JIG_DIR)

    logging.info("ebola ...")
    xQuAD_multisource_with_feedback_tc(
        topics=EBOLA_TOPICS,
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
        use_jig_feedback_cnt_limit=use_jig_feedback_cnt_limit,
        query_expansion_feedback_cnt_limit=query_expansion_feedback_cnt_limit,
        tot_retrival_doc=700,
        idf_dict_without_stem=ebola_idf_dict_without_stem,
        every_expand_words_cnt=every_expand_words_cnt,
        source_weights=source_weight, if_use_stop_stop_strategy=if_use_stop_stop_strategy
    )

    logging.info("nyt...")
    xQuAD_with_feedback_del_dup_dynamic_D_tc(
        topics=NYT_TOPICS,
        suggestor=suggestor,
        if_use_clean_text=True,
        boost_params=1,
        if_stem=True,
        candidate_doc_cnt=30,
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
        query_expansion_feedback_cnt_limit=query_expansion_feedback_cnt_limit,
        tot_retrival_doc=700,
        idf_dict_without_stem=nyt_without_stem_idf_dict,
        every_expand_words_cnt=every_expand_words_cnt,
        if_use_stop_stop_strategy=if_use_stop_stop_strategy)


if __name__ == '__main__':
    import logging
    logging.root.setLevel(logging.WARNING)
    a = [0.6, 0.65, 0.7, 0.75, 0.85]  # 5
    b = [3, 6]  # 4
    c = [25, 35]  # 3
    args = []
    for j in c:
        for k in b:
            for l in a:
                args.append([l, k, j])
    import sys
    try:
        xquad_lmd, e_cnt, c_doc_cnt = args[int(sys.argv[1])]
        submission_xQuAD_rocchio_tc_solution(
            xquad_lmd=xquad_lmd,
            e_cnt=e_cnt,
            c_doc_cnt=c_doc_cnt
        )
    except Exception as e:
        logging.exception("[!] exception: %s", e)
        exit(-1)


__END__ = True
