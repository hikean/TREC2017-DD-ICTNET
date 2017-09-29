# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/24 下午8:30
# @version: 1.0

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
from xQuAD_rocchio_solution import cal_sim_by_wc,update_state,remove_dup_from_words_by_set,passage_text_to_subqueries, passage_text_to_expand_query, cal_sim_by_word_set, judge_dup_doc, select_query_expansion_words_by_passage_text,dicts2query, append_docs_to_doc_list, cal_qe_words_by_dif_subtopics, cut_off_jig_feedback,NytKey2Id
from src.utils.stop_stratage import *


def get_top_docs_from_doc_list( tot_doc_list, already_select_key_set, ret_cnt ):
    ret = []
    for i,d in enumerate(tot_doc_list):
        if d[0] in already_select_key_set:
            # print "ALREADY SELECT:", d[0]
            continue
        # print "SELECT:", d[0]
        ret.append( d )
        if len(ret) >= ret_cnt:break
    return ret

# '''
# 这个是使用查询反馈的...
#
# '''
# def xQuAD_clean_use_local_data_with_feedback(topics = EBOLA_TOPICS,
#                 suggestor=None,
#                 if_use_clean_text=True,
#                 boost_params=1,
#                 if_stem=True,
#                 candidate_doc_cnt = 700, #表示每一轮的候选的文章数目，注意去重
#                 tot_itr_times = 2,
#                 every_itr_doc_cnt = 5,
#                 use_subquery_cnt = 5,
#                 lm_lmd = 1.0,
#                 xquad_lmd = 0.6,
#                 idf_dict = None,
#
#                 jig = None,
#                 irsys = None,
#                 data_dir=EBOLA_CLEAN_FULL_DATA_DIR,
#                 data_field='content',
#                 key2id_dict = {},
#                 use_jig_feedback_cnt_limit = 2,
#                 query_expansion_feedback_cnt_limit = 1,
#                 tot_retrival_doc = 700,
#                 idf_dict_without_stem = None,
#                 every_expand_words_cnt=5
#                 ):
#     lm = LMDirichlet(lmd=lm_lmd)
#     logging.info("initing xQuAD...")
#     xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)
#
#     subqueries_statics = {} # key: topic_id, v:[ 使用suggested subquery的次数， 使用jig feedback的次数 ]
#
#     for tid, topic in topics:
#             subqueries_statics[tid] = [0, 0]
#             logging.info("search for topic %s %s" % (tid, topic))
#             print "tot_itr_times:", tot_itr_times
#             print "every_itr_doc_cnt:", every_itr_doc_cnt
#             print "use_subquery_cnt:", use_subquery_cnt
#             print "lm_lmd:", lm_lmd
#             print "xquad_lmd:", xquad_lmd
#             print "if_stem:", if_stem
#             print "if_use_clean_text:", if_use_clean_text
#             print "candidate doc cnt:", candidate_doc_cnt
#             print "use_jig_feedback_cnt_limit:", use_jig_feedback_cnt_limit
#             print "query_expansion_feedback_cnt_limit:", query_expansion_feedback_cnt_limit
#             print "every_expand_words_cnt:", every_expand_words_cnt
#
#             # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
#             already_select_key_set = set()
#             interect_docs = {} #key: docno, v:[score, {subtopic_id:passage_text}, d,], 这里面的d是
#             score_key_dic = {} #key:score, v:set, 里面是文档的key 结合interect_docs足够获取很多东西了
#             D = []
#             # already_cover_topic_dict
#             # already_cover_topic_dict，格式 key:subtopic_id，
#             # v: dict形式， key是相关度， v [这个subtopic下已经有的文章个数, [passage_text], 筛选出来的词的list, ], 这个的格式还是看already_cover_topic_dict吧
#             already_cover_topic_dict = {}
#             sim_doc_pair = {} # key:docno, v:keys... key表示提交的文章的key， v是一个set，表示没有提交但是跟key文章相同的其他文章的key
#             left_doc_dict = {} #key:docno, v:doc_dic
#
#             init_query_word_list_this_itr = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
#             google_subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
#             google_subquerys = clean_subquery_list(google_subquerys, idf_dict, if_stem=if_stem, query_words=init_query_word_list_this_itr)
#
#             print "===> google_subquerys:", google_subquerys
#
#
#             tot_doc_list = irsys.retrieve_docs([topic], query_field=data_field, with_query_field=False)[0:tot_retrival_doc]
#             for i in range(tot_itr_times):
#                 print "itr:", i, " tid:", tid
#                 if i == 0:
#                     if_use_jig_feedback = False
#                     if_expand_query = False
#                 else:
#                     # 先决定用suggestor还是用jig返回的, 然后取top2的相关度， 除非没有3-4
#                     already_get_subtopics = 0
#                     for subtopic_id, info in already_cover_topic_dict.items():
#                         for rating in RATES:
#                             if info.has_key(rating):
#                                 already_get_subtopics += 1
#                                 break
#                     # 有use_jig_feedback_cnt_limit个以上的子话题已经拿到了
#                     if already_get_subtopics >= use_jig_feedback_cnt_limit:
#                         if_use_jig_feedback = True
#                     else:
#                         if_use_jig_feedback = False
#
#                     if already_get_subtopics >= query_expansion_feedback_cnt_limit:
#                         if_expand_query = True
#                     else:
#                         if_expand_query = False
#
#                 if if_expand_query:
#                     #TODO:这里的扩展两种方式，一是不断增加词，二是有筛选的，在Subtopic覆盖少的里面选，以及只选分数最高的, 目前只用feed_back做扩展，因为已经够长了对很多XXX
#
#                     feedbacks = passage_text_to_expand_query(already_cover_topic_dict)
#                     ####### 这种方式是直接连接所有subtopic的Feedback做qe
#                     # feedbacks = ' '.join(feedbacks)
#                     # #TODO:CHECK 这里if_lower的设置
#                     # feedbacks_words = basic_preprocess(feedbacks, if_lower=False, if_stem=False)
#                     # #TODO:CHECK这里的idf_dict
#                     # expanded_words_dic = select_query_expansion_words_by_passage_text(idf_dict_without_stem, feedbacks_words, qe_words_cnt=10)
#                     ###########
#
#                     expanded_words_dic = cal_qe_words_by_dif_subtopics(feedbacks, idf_dict_without_stem, if_lower=False, if_stem=False, every_expand_words_cnt=every_expand_words_cnt)
#
#                     init_q = cut_words(topic)
#
#                     expanded_query, query_word_list_this_itr = dicts2query(init_q, expanded_words_dic)
#
#                     query_this_itr = expanded_query
#
#                     #TODO:这样修改一下规则：
#                     #筛选词的个数 = min(10, 10-在这个subtopic下已经提交的3-4文档的个数)
#
#                     # expanded_query = expand_query
#                     print "retriving using expanded query:", query_this_itr
#                     tot_doc_list = docs_list = irsys.retrieve_docs([query_this_itr], with_query_field=False, query_field=data_field)[0:tot_retrival_doc]
#
#                 else:
#                     query_this_itr = topic
#                     query_word_list_this_itr = init_query_word_list_this_itr
#                     # docs_list = get_top_docs_from_doc_list(tot_doc_list, already_select_key_set,
#
#                     docs_list = get_top_docs_from_doc_list(tot_doc_list, already_select_key_set,
#                                                            ret_cnt=candidate_doc_cnt)
#
#                 print "topic:", topic
#                 print "QUERY:", if_expand_query, query_this_itr
#
#                 docs_keys = get_doc_keys_from_doc_list(docs_list)
#                 corpus = get_corpus_by_keys(data_dir, key2id_dict, docs_keys, if_stem=if_stem, field=data_field)
#                 docs_list = append_docs_to_doc_list(docs_list, docs_keys, corpus, field=data_field)
#                 logging.info("cal dcs...")
#                 dc_dict = cal_dc_dicts(docs_list, content_field=data_field)
#
#                 if if_use_jig_feedback:
#                     print "USE JIG PASSAGE TEXT AS subquery, itr:", i
#                     # TODO:这里要试试是不是要做筛选词处理，另外要考虑passage_text是不是已经用过
#                     subqueries = passage_text_to_subqueries(already_cover_topic_dict, user_top_k_text=2)
#                     subqueries = clean_subquery_list(subqueries, idf_dict, if_stem=if_stem, query_words=query_word_list_this_itr)
#                     subqueries_statics[tid][1] += 1
#                 else:
#                     print "USE Suggested query as subquery, itr:", i
#                     subqueries = google_subquerys
#                     subqueries_statics[tid][0] += 1
#                 print "USE SUBQUERIES:", subqueries
#                 this_itr_select_docs = []
#                 if i == 0 or ( not if_use_jig_feedback and len(subqueries) == 0 ):
#                     file_ptr = 0 #TODO:
#                     if len(subqueries) == 0:
#                         print "======@@@@@@@@@@@@> subquery cnt is zero, tid, topic:", tid, topic
#                     # print docs_list[0]
#                     while len(this_itr_select_docs) < 5  and file_ptr < len(docs_list):
#                         if docs_list[file_ptr][1][2]['key'] in already_select_key_set:
#                             continue
#                         this_itr_select_docs.append( docs_list[file_ptr] )
#                         already_select_key_set.add( docs_list[file_ptr][1][2]['key'] )
#                         #TODO CHECK:D 如果i!=0的时候  这个D是不是应该增大一些...
#                         # D.append( docs_list[file_ptr][1][2] )
#                         file_ptr += 1
#
#                     # jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]
#                     # print "already_select_key_set:", already_select_key_set
#                     jig_format_docs = irsys.items2jigdocs(this_itr_select_docs)
#                     print "USE:", jig_format_docs
#                     iresult = jig.run_itr(jig_format_docs, topic_id=tid)
#                     print "i itr:", i
#                     if iresult is not None:
#                         for _ in iresult:
#                             print _
#                     update_state(already_cover_topic_dict, iresult)
#                     continue
#                 else:
#
#                     #use xQuAD to select best docs
#                     #TODO:检查整个代码逻辑, docs_list应该是保持有candidate_cnt个没有select的
#                     R_left = get_R_left(docs_list, already_select_key_set)
#                     ranked_docs = []
#                     for ixquad_selected in range(every_itr_doc_cnt):
#                         print "==== [INFO] R_left cnt:", len(R_left)
#                         ranked_docs = xquad.select_doc_u_cos(query_word_list_this_itr, R_left, D, subqueries, dc_dicts=dc_dict,
#                                               ret_rel_div_score=True)
#                         d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
#                         if d[0][KEY] in already_select_key_set:
#                             print "############!!!!!!!!!ERROR >>>>>>>>>>>> SELECT DUP:", d[KEY]
#                         # if i == 0:
#                         print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
#                         D.append(d[0])
#                         D[-1][SCORE] = d[1]
#                         already_select_key_set.add(d[0][KEY])
#                         R_left.remove(d[0])
#
#                     # this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]
#                     this_itr_select_docs = []
#                     for idx_,_ in enumerate(ranked_docs):
#                         if _[0][KEY] in already_select_key_set:continue
#                         this_itr_select_docs.append(_)
#                         if len(this_itr_select_docs) >= 5:break
#
#
#                     jig_format_docs = []
#                     for d in this_itr_select_docs:
#                         #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
#                         jig_format_docs.append(
#                             (0, d[0][KEY], d[1] * boost_params)
#                         )
#
#                     iresult = jig.run_itr(jig_format_docs, topic_id=tid)
#                     if iresult is not None:
#                         print "itr result , i:",
#                         if type(iresult) is list:
#                             for _ in iresult:
#                                 print _
#                             update_state(already_cover_topic_dict, iresult)
#                         else:
#                             print iresult
#             print "======== CHECK DUP:", len(already_select_key_set), tot_itr_times * 5
#             if tot_itr_times * 5 != len(already_select_key_set):
#                 print "[ERROR]  FUCK, tid, itr:", tid, i
#                 exit(-1)
#
#             jig.judge()
#
#     for tid, v in subqueries_statics.items():
#         print "tid:", tid, "suggested, jig feedback:", v
#


'''
ebola数据

'''

def test_1():
    logging.info("loading key2id dict ebola")
    key2id_dict = json.load(codecs.open(FULL_KEY2ID))

    print "id of key[ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866]:", key2id_dict['ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866']

    logging.info("load polar stem idf dict...")
    idf_dict = json.load(codecs.open(STEM_IDF_DICT_EBOLA, 'r', 'utf-8'))
    print "tot word BEFORE to str cnt:", len(idf_dict.items())
    err_cnt = 0
    for k in idf_dict.keys():
        v = idf_dict[k]
        idf_dict.pop(k)
        try:
            k = str(k)
            idf_dict[k] = v
        except:
            err_cnt += 1
            # print "UNICODE TO STR ERR:", k
    print "UNICODE TO STR ERR CNT:", err_cnt
    print "tot word after to str cnt:", len(idf_dict.items())

    solrs = get_lm_ebola_solr()
    w = [3,1,1,1,1]
    irsys = IRSys(solrs, w)
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    jig = JigClient_OLD(tot_itr_times=2, base_jig_dir=EBOLA_POLAR_JIG_DIR)
    # xQuAD_clean(
    #     topics=EBOLA_TOPICS,
    #     suggestor=suggestor,
    #     if_use_clean_text=True,
    #     if_stem=True,
    #     candidate_doc_cnt=30,
    #     tot_itr_times=2,
    #     every_itr_doc_cnt=5,
    #     use_subquery_cnt=5,
    #     xquad_lmd=0.6,
    #     idf_dict=idf_dict,
    #     jig=jig,
    #     irsys=irsys
    # )

    # EBOLA_TOPICS = [
    #     ('DD16-21', 'Ebola medical waste'),
    # ]

    # xQuAD_clean_use_local_data_with_feedback(topics=EBOLA_TOPICS,
    #                                             suggestor=suggestor,
    #                                             if_use_clean_text=True,
    #                                             boost_params=1,
    #                                             if_stem=True,
    #                                             candidate_doc_cnt=30,
    #                                             tot_itr_times=2,
    #                                             every_itr_doc_cnt=5,
    #                                             use_subquery_cnt=5,
    #                                             lm_lmd=1.0,
    #                                             xquad_lmd=0.6,
    #                                             idf_dict=idf_dict,
    #                                             jig=jig,
    #                                             irsys=irsys,
    #                                             data_dir=EBOLA_FULL_NOT_CLEAN,
    #                                             data_field='content',
    #                                             key2id_dict=key2id_dict,
    #                                             use_jig_feedback_cnt_limit=1,
    #                                             )

    xQuAD_clean_use_local_data_with_feedback_clean_code(topics=EBOLA_TOPICS,
                                                 suggestor=suggestor,
                                                 if_use_clean_text=True,
                                                 boost_params=1,
                                                 if_stem=True,
                                                 candidate_doc_cnt=30,  # 表示每一轮的候选的文章数目，注意去重
                                                 tot_itr_times=2,
                                                 every_itr_doc_cnt=5,
                                                 use_subquery_cnt=5,
                                                 lm_lmd=1.0,
                                                 xquad_lmd=0.6,
                                                 idf_dict=idf_dict,
                                                 jig=jig,
                                                 irsys=irsys,
                                                 data_dir=EBOLA_FULL_NOT_CLEAN,
                                                 data_field='content',
                                                 key2id_dict=key2id_dict,
                                                 use_jig_feedback_cnt_limit=1,
                                                 query_expansion_feedback_cnt_limit=1,
                                                 tot_retrival_doc=700
                                                 )




'''
几点清理一下：
1、函数中不出现 魔数
2、tot_list保存上一次的retrival的内容
条数都是 tot_retrival_doc

3、在决定了是不是重新搞tot_list之后，决定本轮的doc_list
这个里面放candidate_doc_cnt 个文档

R_left就是doc_list里面去掉已经选的

dc_dict里面是doc_list的东西

'''

'''
对于D，只有jig返回确实相关的，才加入D
'''

def xQuAD_clean_use_local_data_with_feedback_clean_code_confirm_D(topics = EBOLA_TOPICS,
                suggestor=None,
                if_use_clean_text=True,
                boost_params=1,
                if_stem=True,
                candidate_doc_cnt = 30, #表示每一轮的候选的文章数目，注意去重
                tot_itr_times = 2,
                every_itr_doc_cnt = 5,
                use_subquery_cnt = 5,
                lm_lmd = 1.0,
                xquad_lmd = 0.6,
                idf_dict = None,

                jig = None,
                irsys = None,
                data_dir=EBOLA_CLEAN_FULL_DATA_DIR,
                data_field='content',
                key2id_dict = {},
                use_jig_feedback_cnt_limit = 2,
                query_expansion_feedback_cnt_limit = 1,
                tot_retrival_doc = 700,
                idf_dict_without_stem = None,
                every_expand_words_cnt=5,
                if_use_stop_stop_strategy=False,
                stop_at_cnt = 10
                ):
    lm = LMDirichlet(lmd=lm_lmd)
    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    subqueries_statics = {} # key: topic_id, v:[ 使用suggested subquery的次数， 使用jig feedback的次数 ]

    for tid, topic in topics:
            subqueries_statics[tid] = [0, 0]
            logging.info("search for topic %s %s" % (tid, topic))
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd
            print "if_stem:", if_stem
            print "if_use_clean_text:", if_use_clean_text
            print "candidate doc cnt:", candidate_doc_cnt
            print "use_jig_feedback_cnt_limit:", use_jig_feedback_cnt_limit
            print "query_expansion_feedback_cnt_limit:", query_expansion_feedback_cnt_limit
            print "every_expand_words_cnt:", every_expand_words_cnt
            print "i == 0, donnot add d to D this,exp"

            # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            interect_docs = {} #key: docno, v:[score, {subtopic_id:passage_text}, d,], 这里面的d是
            score_key_dic = {} #key:score, v:set, 里面是文档的key 结合interect_docs足够获取很多东西了
            D = []
            already_cover_topic_dict = {}
            sim_doc_pair = {} # key:docno, v:keys... key表示提交的文章的key， v是一个set，表示没有提交但是跟key文章相同的其他文章的key
            left_doc_dict = {} #key:docno, v:doc_dic
            not_on_topic_doc_set = {} # k:key v:d

            init_query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            google_subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            google_subquerys = clean_subquery_list(google_subquerys, idf_dict, if_stem=if_stem, query_words=init_query_word_list)

            print "===> google_subquerys:", google_subquerys


            tot_doc_list = irsys.retrieve_docs([topic], query_field=data_field, with_query_field=False)[0:tot_retrival_doc]

            for i in range(tot_itr_times):
                print "itr:", i, " tid:", tid

                if if_use_stop_stop_strategy:
                    not_on_topic_cnt = len(not_on_topic_doc_set.keys())
                    print "CHECK IF STOP, not_on_topic_cnt:", not_on_topic_cnt, " stop at cnt:", stop_at_cnt
                    if not_on_topic_cnt >= stop_at_cnt:
                        print "STOP THIS TOPIC,tid:", tid
                        break

                if i == 0:
                    if_use_jig_feedback = False
                    if_expand_query = False
                else:
                    # 先决定用suggestor还是用jig返回的, 然后取top2的相关度， 除非没有3-4
                    already_get_subtopics = 0
                    for subtopic_id, info in already_cover_topic_dict.items():
                        for rating in RATES:
                            if info.has_key(rating):
                                already_get_subtopics += 1
                                break
                    # 有use_jig_feedback_cnt_limit个以上的子话题已经拿到了
                    if already_get_subtopics >= use_jig_feedback_cnt_limit:
                        if_use_jig_feedback = True
                    else:
                        if_use_jig_feedback = False

                    if already_get_subtopics >= query_expansion_feedback_cnt_limit:
                        if_expand_query = True
                    else:
                        if_expand_query = False

                #这里决定是不是重新弄tot_list
                if if_expand_query:
                    #TODO:这里的扩展两种方式，一是不断增加词，二是有筛选的，在Subtopic覆盖少的里面选，以及只选分数最高的, 目前只用feed_back做扩展，因为已经够长了对很多XXX

                    feedbacks = passage_text_to_expand_query(already_cover_topic_dict)
                    ####### 这种方式是直接连接所有subtopic的Feedback做qe
                    # feedbacks = ' '.join(feedbacks)
                    # #TODO:CHECK 这里if_lower的设置
                    # feedbacks_words = basic_preprocess(feedbacks, if_lower=False, if_stem=False)
                    # #TODO:CHECK这里的idf_dict
                    # expanded_words_dic = select_query_expansion_words_by_passage_text(idf_dict_without_stem, feedbacks_words, qe_words_cnt=10)
                    ###########

                    expanded_words_dic = cal_qe_words_by_dif_subtopics(feedbacks, idf_dict_without_stem, if_lower=False, if_stem=False, every_expand_words_cnt=every_expand_words_cnt)

                    init_q = cut_words(topic)

                    expanded_query, query_word_list_this_itr = dicts2query(init_q, expanded_words_dic)

                    query_this_itr = expanded_query

                    #TODO:这样修改一下规则：
                    #筛选词的个数 = min(10, 10-在这个subtopic下已经提交的3-4文档的个数)

                    print "retriving using expanded query:", query_this_itr
                    tot_doc_list = irsys.retrieve_docs([query_this_itr], with_query_field=False, query_field=data_field)[0:tot_retrival_doc]

                else:
                    #这里暗含了 仍然用之前的tot_doc_list
                    query_this_itr = topic
                    query_word_list_this_itr = init_query_word_list
                    # docs_list = get_top_docs_from_doc_list(tot_doc_list, already_select_key_set,

                #这里取docs_list
                docs_list = get_top_docs_from_doc_list(tot_doc_list, already_select_key_set,
                                                           ret_cnt=candidate_doc_cnt)

                print "topic:", topic
                print "QUERY:", if_expand_query, query_this_itr

                docs_keys = get_doc_keys_from_doc_list(docs_list)
                corpus = get_corpus_by_keys(data_dir, key2id_dict, docs_keys, if_stem=if_stem, field=data_field)
                docs_list = append_docs_to_doc_list(docs_list, docs_keys, corpus, field=data_field, if_filter_null=True)
                logging.info("cal dcs...")
                dc_dict = cal_dc_dicts(docs_list, content_field=data_field)

                if if_use_jig_feedback:
                    print "USE JIG PASSAGE TEXT AS subquery, itr:", i
                    # TODO:这里要试试是不是要做筛选词处理，另外要考虑passage_text是不是已经用过
                    subqueries = passage_text_to_subqueries(already_cover_topic_dict, user_top_k_text=2)
                    subqueries = clean_subquery_list(subqueries, idf_dict, if_stem=if_stem, query_words=query_word_list_this_itr)
                    subqueries_statics[tid][1] += 1
                else:
                    print "USE Suggested query as subquery, itr:", i
                    subqueries = google_subquerys
                    subqueries_statics[tid][0] += 1
                print "USE SUBQUERIES:", subqueries
                this_itr_select_docs = []
                if i == 0 or ( not if_use_jig_feedback and len(subqueries) == 0 ):
                    file_ptr = 0 #TODO:检查所有的这个变量，，，
                    if len(subqueries) == 0:
                        print "======@@@@@@@@@@@@> subquery cnt is zero, tid, topic:", tid, topic
                    # print docs_list[0]
                    while len(this_itr_select_docs) < 5  and file_ptr < len(docs_list):
                        if docs_list[file_ptr][1][2]['key'] in already_select_key_set:
                            continue
                        this_itr_select_docs.append( docs_list[file_ptr] )
                        already_select_key_set.add( docs_list[file_ptr][1][2]['key'] )
                        #TODO CHECK:D 如果i!=0的时候  这个D是不是应该增大一些...
                        # D.append( docs_list[file_ptr][1][2] )
                        file_ptr += 1

                    # jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]
                    # print "already_select_key_set:", already_select_key_set
                    jig_format_docs = irsys.items2jigdocs(this_itr_select_docs)
                    print "USE:", jig_format_docs
                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    print "i itr:", i
                    if iresult is not None:
                        for ir, _ in enumerate(iresult):
                            print _
                            if ir == 0:continue
                            if _['on_topic'] == 1:
                                D.append(this_itr_select_docs[ir][1])
                                D[-1][SCORE] = this_itr_select_docs[ir][1]
                            else:
                                print "CCC this_itr_select_docs[ir]:", this_itr_select_docs[ir]
                                print "this_itr_select_docs[ir][0]:", this_itr_select_docs[ir][0]
                                not_on_topic_doc_set[this_itr_select_docs[ir][0]['key']] = \
                                    this_itr_select_docs[ir][0]
                    update_state(already_cover_topic_dict, iresult)

                    continue
                else:

                    #use xQuAD to select best docs
                    #TODO:检查整个代码逻辑, docs_list应该是保持有candidate_cnt个没有select的
                    R_left = get_R_left(docs_list, already_select_key_set)
                    # ranked_docs = []
                    # for ixquad_selected in range(every_itr_doc_cnt):
                    #     print "==== [INFO] R_left cnt:", len(R_left)
                    #     ranked_docs = xquad.select_doc_u_cos(query_word_list_this_itr, R_left, D, subqueries, dc_dicts=dc_dict,
                    #                           ret_rel_div_score=True)
                    #     d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                    #     if d[0][KEY] in already_select_key_set:
                    #         print "############!!!!!!!!!ERROR >>>>>>>>>>>> SELECT DUP:", d[KEY]
                    #     # if i == 0:
                    #     print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                    #     # D.append(d[0])
                    #     # D[-1][SCORE] = d[1]
                    #     already_select_key_set.add(d[0][KEY])
                    #     R_left.remove(d[0])
                    #
                    # # this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]
                    # this_itr_select_docs = []
                    # for idx_,_ in enumerate(ranked_docs):
                    #     if _[0][KEY] in already_select_key_set:continue
                    #     this_itr_select_docs.append(_)
                    #     if len(this_itr_select_docs) >= 5:break

                    this_itr_select_docs = []

                    for ixquad_selected in range(every_itr_doc_cnt):
                        print "==== [INFO] R_left cnt:", len(R_left)
                        ranked_docs = xquad.select_doc_u_cos(query_word_list_this_itr, R_left, D, subqueries, dc_dicts=dc_dict,
                                                             ret_rel_div_score=True)
                        ptr_ = 0
                        while ranked_docs[ptr_][0][KEY] in already_select_key_set:
                            ptr_ += 1
                            continue
                        d = ranked_docs[ptr_]  # 这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        if d[0][KEY] in already_select_key_set:
                            print "############!!!!!!!!!ERROR >>>>>>>>>>>> SELECT DUP:", d[KEY]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:], d[0]
                        this_itr_select_docs.append(d)
                        # D.append(d[0])
                        # D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])
                        print "len R_left, D, this_itr_select_docs, already_select_keys:", len(R_left), len(D), len(
                            this_itr_select_docs), len(already_select_key_set)


                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )

                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:",
                        if type(iresult) is list:
                            for ir,_ in enumerate(iresult):
                                print _
                                if _['on_topic'] == 1:
                                    D.append( this_itr_select_docs[ir][0] )
                                    D[-1][SCORE] = this_itr_select_docs[ir][1]
                                else:
                                    print "CCC this_itr_select_docs[ir]:", this_itr_select_docs[ir]
                                    not_on_topic_doc_set[this_itr_select_docs[ir][0]['key']] = \
                                    this_itr_select_docs[ir][0]

                            update_state(already_cover_topic_dict, iresult)
                        else:
                            print iresult
            print "======== CHECK DUP:", len(already_select_key_set), tot_itr_times * 5
            if tot_itr_times * 5 != len(already_select_key_set):
                print "tot_itr_times * 5 != len(already_select_key_set):", tot_itr_times * 5, len(
                    already_select_key_set)
                print "[ERROR]  FUCK, tid, itr:", tid, i
                # exit(-1)

            jig.judge()

    for tid, v in subqueries_statics.items():
        print "tid:", tid, "suggested, jig feedback:", v




# def xQuAD_clean_use_local_data_with_feedback_clean_code_confirm_D(topics = EBOLA_TOPICS,
def xQuAD_clean_use_local_data_with_feedback_clean_code(topics = EBOLA_TOPICS,
                suggestor=None,
                if_use_clean_text=True,
                boost_params=1,
                if_stem=True,
                candidate_doc_cnt = 30, #表示每一轮的候选的文章数目，注意去重
                tot_itr_times = 2,
                every_itr_doc_cnt = 5,
                use_subquery_cnt = 5,
                lm_lmd = 1.0,
                xquad_lmd = 0.6,
                idf_dict = None,

                jig = None,
                irsys = None,
                data_dir=EBOLA_CLEAN_FULL_DATA_DIR,
                data_field='content',
                key2id_dict = {},
                use_jig_feedback_cnt_limit = 2,
                query_expansion_feedback_cnt_limit = 1,
                tot_retrival_doc = 700,
                idf_dict_without_stem = None,
                every_expand_words_cnt=5
                ):
    lm = LMDirichlet(lmd=lm_lmd)
    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    subqueries_statics = {} # key: topic_id, v:[ 使用suggested subquery的次数， 使用jig feedback的次数 ]

    for tid, topic in topics:
            subqueries_statics[tid] = [0, 0]
            logging.info("search for topic %s %s" % (tid, topic))
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd
            print "if_stem:", if_stem
            print "if_use_clean_text:", if_use_clean_text
            print "candidate doc cnt:", candidate_doc_cnt
            print "use_jig_feedback_cnt_limit:", use_jig_feedback_cnt_limit
            print "query_expansion_feedback_cnt_limit:", query_expansion_feedback_cnt_limit
            print "every_expand_words_cnt:", every_expand_words_cnt

            # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            interect_docs = {} #key: docno, v:[score, {subtopic_id:passage_text}, d,], 这里面的d是
            score_key_dic = {} #key:score, v:set, 里面是文档的key 结合interect_docs足够获取很多东西了
            D = []
            NOT_ON_TOPIC_DUP = [] #TODO
            already_cover_topic_dict = {}
            sim_doc_pair = {} # key:docno, v:keys... key表示提交的文章的key， v是一个set，表示没有提交但是跟key文章相同的其他文章的key
            left_doc_dict = {} #key:docno, v:doc_dic

            init_query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            google_subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            google_subquerys = clean_subquery_list(google_subquerys, idf_dict, if_stem=if_stem, query_words=init_query_word_list)

            print "===> google_subquerys:", google_subquerys


            tot_doc_list = irsys.retrieve_docs([topic], query_field=data_field, with_query_field=False)[0:tot_retrival_doc]

            for i in range(tot_itr_times):
                print "itr:", i, " tid:", tid
                if i == 0:
                    if_use_jig_feedback = False
                    if_expand_query = False
                else:
                    # 先决定用suggestor还是用jig返回的, 然后取top2的相关度， 除非没有3-4
                    already_get_subtopics = 0
                    for subtopic_id, info in already_cover_topic_dict.items():
                        for rating in RATES:
                            if info.has_key(rating):
                                already_get_subtopics += 1
                                break
                    # 有use_jig_feedback_cnt_limit个以上的子话题已经拿到了
                    if already_get_subtopics >= use_jig_feedback_cnt_limit:
                        if_use_jig_feedback = True
                    else:
                        if_use_jig_feedback = False

                    if already_get_subtopics >= query_expansion_feedback_cnt_limit:
                        if_expand_query = True
                    else:
                        if_expand_query = False

                #这里决定是不是重新弄tot_list
                if if_expand_query:
                    #TODO:这里的扩展两种方式，一是不断增加词，二是有筛选的，在Subtopic覆盖少的里面选，以及只选分数最高的, 目前只用feed_back做扩展，因为已经够长了对很多XXX

                    feedbacks = passage_text_to_expand_query(already_cover_topic_dict)
                    ####### 这种方式是直接连接所有subtopic的Feedback做qe
                    # feedbacks = ' '.join(feedbacks)
                    # #TODO:CHECK 这里if_lower的设置
                    # feedbacks_words = basic_preprocess(feedbacks, if_lower=False, if_stem=False)
                    # #TODO:CHECK这里的idf_dict
                    # expanded_words_dic = select_query_expansion_words_by_passage_text(idf_dict_without_stem, feedbacks_words, qe_words_cnt=10)
                    ###########

                    expanded_words_dic = cal_qe_words_by_dif_subtopics(feedbacks, idf_dict_without_stem, if_lower=False, if_stem=False, every_expand_words_cnt=every_expand_words_cnt)

                    init_q = cut_words(topic)

                    expanded_query, query_word_list_this_itr = dicts2query(init_q, expanded_words_dic)

                    query_this_itr = expanded_query

                    #TODO:这样修改一下规则：
                    #筛选词的个数 = min(10, 10-在这个subtopic下已经提交的3-4文档的个数)

                    print "retriving using expanded query:", query_this_itr
                    tot_doc_list = irsys.retrieve_docs([query_this_itr], with_query_field=False, query_field=data_field)[0:tot_retrival_doc]

                else:
                    #这里暗含了 仍然用之前的tot_doc_list
                    query_this_itr = topic
                    query_word_list_this_itr = init_query_word_list
                    # docs_list = get_top_docs_from_doc_list(tot_doc_list, already_select_key_set,

                #这里取docs_list
                docs_list = get_top_docs_from_doc_list(tot_doc_list, already_select_key_set,
                                                           ret_cnt=candidate_doc_cnt)

                print "topic:", topic
                print "QUERY:", if_expand_query, query_this_itr

                docs_keys = get_doc_keys_from_doc_list(docs_list)
                corpus = get_corpus_by_keys(data_dir, key2id_dict, docs_keys, if_stem=if_stem, field=data_field)
                docs_list = append_docs_to_doc_list(docs_list, docs_keys, corpus, field=data_field, if_filter_null=True)
                logging.info("cal dcs...")
                dc_dict = cal_dc_dicts(docs_list, content_field=data_field)

                if if_use_jig_feedback:
                    print "USE JIG PASSAGE TEXT AS subquery, itr:", i
                    # TODO:这里要试试是不是要做筛选词处理，另外要考虑passage_text是不是已经用过
                    subqueries = passage_text_to_subqueries(already_cover_topic_dict, user_top_k_text=2)
                    subqueries = clean_subquery_list(subqueries, idf_dict, if_stem=if_stem, query_words=query_word_list_this_itr)
                    subqueries_statics[tid][1] += 1
                else:
                    print "USE Suggested query as subquery, itr:", i
                    subqueries = google_subquerys
                    subqueries_statics[tid][0] += 1
                print "USE SUBQUERIES:", subqueries
                this_itr_select_docs = []
                if i == 0 or ( not if_use_jig_feedback and len(subqueries) == 0 ):
                    file_ptr = 0 #TODO:
                    if len(subqueries) == 0:
                        print "======@@@@@@@@@@@@> subquery cnt is zero, tid, topic:", tid, topic
                    # print docs_list[0]
                    while len(this_itr_select_docs) < 5  and file_ptr < len(docs_list):
                        if docs_list[file_ptr][1][2]['key'] in already_select_key_set:
                            continue
                        this_itr_select_docs.append( docs_list[file_ptr] )
                        already_select_key_set.add( docs_list[file_ptr][1][2]['key'] )
                        #TODO CHECK:D 如果i!=0的时候  这个D是不是应该增大一些...
                        # D.append( docs_list[file_ptr][1][2] )
                        file_ptr += 1

                    # jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]
                    # print "already_select_key_set:", already_select_key_set
                    jig_format_docs = irsys.items2jigdocs(this_itr_select_docs)
                    print "USE:", jig_format_docs
                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    print "i itr:", i
                    if iresult is not None:
                        for _ in iresult:
                            print _
                    update_state(already_cover_topic_dict, iresult)
                    continue
                else:

                    #use xQuAD to select best docs
                    #TODO:检查整个代码逻辑, docs_list应该是保持有candidate_cnt个没有select的
                    R_left = get_R_left(docs_list, already_select_key_set)
                    # ranked_docs = []
                    # for ixquad_selected in range(every_itr_doc_cnt):
                    #     print "==== [INFO] R_left cnt:", len(R_left)
                    #     ranked_docs = xquad.select_doc_u_cos(query_word_list_this_itr, R_left, D, subqueries, dc_dicts=dc_dict,
                    #                           ret_rel_div_score=True)
                    #     d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                    #     if d[0][KEY] in already_select_key_set:
                    #         print "############!!!!!!!!!ERROR >>>>>>>>>>>> SELECT DUP:", d[KEY]
                    #     # if i == 0:
                    #     print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                    #     D.append(d[0])
                    #     D[-1][SCORE] = d[1]
                    #     already_select_key_set.add(d[0][KEY])
                    #     R_left.remove(d[0])
                    #
                    # # this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]
                    # this_itr_select_docs = []
                    # for idx_,_ in enumerate(ranked_docs):
                    #     if _[0][KEY] in already_select_key_set:continue
                    #     this_itr_select_docs.append(_)
                    #     if len(this_itr_select_docs) >= 5:break

                    this_itr_select_docs = []

                    for ixquad_selected in range(every_itr_doc_cnt):
                        print "==== [INFO] R_left cnt:", len(R_left)
                        ranked_docs = xquad.select_doc_u_cos(query_word_list_this_itr, R_left, D, subqueries, dc_dicts=dc_dict,
                                                             ret_rel_div_score=True)
                        ptr_ = 0
                        while ranked_docs[ptr_][0][KEY] in already_select_key_set:
                            ptr_ += 1
                            continue
                        d = ranked_docs[ptr_]  # 这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        if d[0][KEY] in already_select_key_set:
                            print "############!!!!!!!!!ERROR >>>>>>>>>>>> SELECT DUP:", d[KEY]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:], d[0]
                        this_itr_select_docs.append(d)
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])
                        print "len R_left, D, this_itr_select_docs, already_select_keys:", len(R_left), len(D), len(
                            this_itr_select_docs), len(already_select_key_set)

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )

                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:",
                        if type(iresult) is list:
                            for _ in iresult:
                                print _
                            update_state(already_cover_topic_dict, iresult)
                        else:
                            print iresult
            print "======== CHECK DUP:", len(already_select_key_set), tot_itr_times * 5
            if tot_itr_times * 5 != len(already_select_key_set):
                print "tot_itr_times * 5 != len(already_select_key_set):", tot_itr_times * 5, len(
                    already_select_key_set)
                print "[ERROR]  FUCK, tid, itr:", tid, i

            jig.judge()

    for tid, v in subqueries_statics.items():
        print "tid:", tid, "suggested, jig feedback:", v

'''
使用nyt的数据
'''
def test_1_nyt():
    logging.info("loading key2id dict ebola")
    # key2id_dict = json.load(codecs.open(FULL_KEY2ID))
    key2id_dict = NytKey2Id()

    # print "id of key[ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866]:", key2id_dict[
    #     'ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866']

    logging.info("load nyt stem idf dict...")
    # idf_dict = json.load(codecs.open(STEM_IDF_DICT_EBOLA, 'r', 'utf-8'))
    idf_dict = json.load(codecs.open(nyt_idf_idf_dic_stem, 'r', 'utf-8'))
    print "tot word BEFORE to str cnt:", len(idf_dict.items())


    logging.info("load nyt without stem idf dict")
    idf_dict_without_stem = json.load(codecs.open(nyt_idf_idf_dic_nostem, 'r', 'utf-8'))

    err_cnt = 0
    for k in idf_dict.keys():
        v = idf_dict[k]
        idf_dict.pop(k)
        try:
            k = str(k)
            idf_dict[k] = v
        except:
            err_cnt += 1
            # print "UNICODE TO STR ERR:", k
    print "UNICODE TO STR ERR CNT:", err_cnt
    print "tot word after to str cnt:", len(idf_dict.items())

    solrs = get_all_nyt_seg_solrs()
    w = [1, ] * len(solrs)
    irsys = IRSys(solrs, w)
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    jig = JigClient(tot_itr_times=2, base_jig_dir=NYT_JIG_DIR)


    # EBOLA_TOPICS = [
    #     ('DD16-21', 'Ebola medical waste'),
    # ]

    # NYT_TOPICS = [
    #     # ('dd17-46', 'PGP')
    #
    #     # ('dd17-4', 'Origins Tribeca Film Festival'),
    #
    #     # ('dd17-15', 'arik afek yair klein link'),
    #     # ('dd17-14', 'Montserrat eruption effects'),
    #     ('dd17-2', 'Who Outed Valerie Plame?'),
    #     # ('dd17-16', 'Eggs actually are good for you'),
    # ]

    xQuAD_clean_use_local_data_with_feedback_clean_code(topics=NYT_TOPICS,
                                                suggestor=suggestor,
                                                if_use_clean_text=True,
                                                boost_params=1,
                                                if_stem=True,
                                                candidate_doc_cnt=30,
                                                tot_itr_times=2,
                                                every_itr_doc_cnt=5,
                                                use_subquery_cnt=5,
                                                lm_lmd=1.0,
                                                xquad_lmd=0.6,
                                                idf_dict=idf_dict,
                                                jig=jig,
                                                irsys=irsys,
                                                data_dir=NYT_SEG_DATA_DIR,
                                                data_field='content_full_text',
                                                key2id_dict=key2id_dict,
                                                use_jig_feedback_cnt_limit=2,
                                                query_expansion_feedback_cnt_limit=2,
                                                tot_retrival_doc=700,
                                             idf_dict_without_stem = idf_dict_without_stem,
                                             every_expand_words_cnt=3
                                                )



'''
使用nyt的数据
修改了D，只有jig认为是相关的，才加入D
'''
def test_2_nyt():
    logging.info("loading key2id dict ebola")
    # key2id_dict = json.load(codecs.open(FULL_KEY2ID))
    key2id_dict = NytKey2Id()

    # print "id of key[ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866]:", key2id_dict[
    #     'ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866']

    logging.info("load nyt stem idf dict...")
    # idf_dict = json.load(codecs.open(STEM_IDF_DICT_EBOLA, 'r', 'utf-8'))
    idf_dict = json.load(codecs.open(nyt_idf_idf_dic_stem, 'r', 'utf-8'))
    print "tot word BEFORE to str cnt:", len(idf_dict.items())


    logging.info("load nyt without stem idf dict")
    idf_dict_without_stem = json.load(codecs.open(nyt_idf_idf_dic_nostem, 'r', 'utf-8'))

    err_cnt = 0
    for k in idf_dict.keys():
        v = idf_dict[k]
        idf_dict.pop(k)
        try:
            k = str(k)
            idf_dict[k] = v
        except:
            err_cnt += 1
            # print "UNICODE TO STR ERR:", k
    print "UNICODE TO STR ERR CNT:", err_cnt
    print "tot word after to str cnt:", len(idf_dict.items())

    solrs = get_all_nyt_seg_solrs()
    w = [1, ] * len(solrs)
    irsys = IRSys(solrs, w)
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    jig = JigClient(tot_itr_times=2, base_jig_dir=NYT_JIG_DIR)


    # EBOLA_TOPICS = [
    #     ('DD16-21', 'Ebola medical waste'),
    # ]

    # NYT_TOPICS = [
    #     # ('dd17-46', 'PGP')
    #
    #     # ('dd17-4', 'Origins Tribeca Film Festival'),
    #
    #     # ('dd17-15', 'arik afek yair klein link'),
    #     # ('dd17-14', 'Montserrat eruption effects'),
    #     ('dd17-2', 'Who Outed Valerie Plame?'),
    #     # ('dd17-16', 'Eggs actually are good for you'),
    # ]

    xQuAD_clean_use_local_data_with_feedback_clean_code_confirm_D(topics=NYT_TOPICS,
                                                suggestor=suggestor,
                                                if_use_clean_text=True,
                                                boost_params=1,
                                                if_stem=True,
                                                candidate_doc_cnt=30,
                                                tot_itr_times=2,
                                                every_itr_doc_cnt=5,
                                                use_subquery_cnt=5,
                                                lm_lmd=1.0,
                                                xquad_lmd=0.6,
                                                idf_dict=idf_dict,
                                                jig=jig,
                                                irsys=irsys,
                                                data_dir=NYT_SEG_DATA_DIR,
                                                data_field='content_full_text',
                                                key2id_dict=key2id_dict,
                                                use_jig_feedback_cnt_limit=2,
                                                query_expansion_feedback_cnt_limit=1,
                                                tot_retrival_doc=700,
                                             idf_dict_without_stem = idf_dict_without_stem,
                                             every_expand_words_cnt=3
                                                )


def test_2_ebola():
    logging.info("loading key2id dict ebola")
    ebola_key2id_dict = json.load(codecs.open(FULL_KEY2ID))

    logging.info("load nyt stem idf dict...")
    ebola_stem_idf_dict = json.load(codecs.open(STEM_IDF_DICT_EBOLA, 'r', 'utf-8'))
    # idf_dict = json.load(codecs.open(nyt_idf_idf_dic_stem, 'r', 'utf-8'))
    # print "tot word BEFORE to str cnt:", len(ebola_stem_idf_dict.items())

    logging.info("load nyt without stem idf dict")
    # idf_dict_without_stem = json.load(codecs.open(nyt_idf_idf_dic_nostem, 'r', 'utf-8'))

    ebola_idf_dict_without_stem = json.load(codecs.open(ebola_nostem_idf_dic_path_clean, 'r', 'utf-8'))

    ebola_solrs = get_all_ebola_solrs()
    ebola_solr_w = [3,1,1,1,1,1]

    irsys = IRSys(ebola_solrs, ebola_solr_w)
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    jig = JigClient(tot_itr_times=2, base_jig_dir=EBOLA_NYT_JIG_DIR)

    # EBOLA_TOPICS = [
    #     ('DD16-7', 'Urbanisation Urbanization'),
    # ]

    # NYT_TOPICS = [
    #     # ('dd17-46', 'PGP')
    #
    #     # ('dd17-4', 'Origins Tribeca Film Festival'),
    #
    #     # ('dd17-15', 'arik afek yair klein link'),
    #     # ('dd17-14', 'Montserrat eruption effects'),
    #     ('dd17-2', 'Who Outed Valerie Plame?'),
    #     # ('dd17-16', 'Eggs actually are good for you'),
    # ]

    xQuAD_clean_use_local_data_with_feedback_clean_code_confirm_D(topics=EBOLA_TOPICS,
                                                                  suggestor=suggestor,
                                                                  if_use_clean_text=True,
                                                                  boost_params=1,
                                                                  if_stem=True,
                                                                  candidate_doc_cnt=30,
                                                                  tot_itr_times=2,
                                                                  every_itr_doc_cnt=5,
                                                                  use_subquery_cnt=5,
                                                                  lm_lmd=1.0,
                                                                  xquad_lmd=0.6,
                                                                  idf_dict=ebola_stem_idf_dict,
                                                                  jig=jig,
                                                                  irsys=irsys,
                                                                  data_dir=EBOLA_FULL_NOT_CLEAN,
                                                                  data_field='content',
                                                                  key2id_dict=ebola_key2id_dict,
                                                                  use_jig_feedback_cnt_limit=2,
                                                                  query_expansion_feedback_cnt_limit=1,
                                                                  tot_retrival_doc=700,
                                                                  idf_dict_without_stem=ebola_idf_dict_without_stem,
                                                                  every_expand_words_cnt=3
                                                                  )




if __name__ == '__main__':
    # test_1()
    # test_1_nyt()
    # test_2_nyt()
    test_2_ebola()

__END__ = True