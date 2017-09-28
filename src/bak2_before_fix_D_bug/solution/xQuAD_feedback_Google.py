# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/28 上午3:56
# @version: 1.0

from xQuAD_with_feedback import *

'''

两个地方：
1、把google的rank作为分数
2、如果某一轮完全没有结果，那么就开始返回google的结果，然后stop策略方面，现有的cnt-x， x可调

'''


def google_help(google_scorer, tid , already_select_keys):
    data = google_scorer.data[tid]
    ret = []
    for key in data:
        if key not in already_select_keys:
            ret.append( (0, key, 5-len(ret)) )
            already_select_keys.add(key)
        if len(ret) >= 5:continue
    return ret

def xQuAD_feedback_google_score(topics = EBOLA_TOPICS,
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
                stop_at_cnt = 10,
                google_scorer = None,
                use_google_help = False,
                google_help_stop_minus = 3
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
            current_max_score = 0 #为了google score部分
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
            current_max_score = tot_doc_list[0][1][0]
            this_topic_use_google = False
            for i in range(tot_itr_times):
                print "itr:", i, " tid:", tid

                if if_use_stop_stop_strategy:
                    not_on_topic_cnt = len(not_on_topic_doc_set.keys())
                    print "CHECK IF STOP, not_on_topic_cnt:", not_on_topic_cnt, " stop at cnt:", stop_at_cnt
                    if not_on_topic_cnt >= stop_at_cnt:
                        print "STOP THIS TOPIC,tid:", tid
                        break



                #先判断是不是已经满足google的条件
                if use_google_help and this_topic_use_google:
                    print "USING GOOGLE HELP"
                    jig_format_docs = google_help(google_scorer, tid, already_select_key_set)
                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    print "i itr:", i
                    if iresult is not None:
                        this_itr_not_on_topic_cnt = 0
                        for ir, _ in enumerate(iresult):
                            print _
                            if _['on_topic'] == 0:
                                not_on_topic_doc_set[ jig_format_docs[ir][1] ] = None


                    continue


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
                    current_max_score = tot_doc_list[0][1][0]

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
                if i == 0 or ( not if_use_jig_feedback and len(subqueries) == 0 ):
                    this_itr_select_docs = []
                    #this_itr_select_docs里面格式是 [ (key, [tot_score, [scores], d] ) ]
                    file_ptr = 0 #TODO:检查所有的这个变量，，，
                    if len(subqueries) == 0:
                        print "======@@@@@@@@@@@@> subquery cnt is zero, tid, topic:", tid, topic
                    # print docs_list[0]
                    while len(this_itr_select_docs) < 5  and file_ptr < len(docs_list):
                        if docs_list[file_ptr][1][2]['key'] in already_select_key_set:
                            continue
                        this_itr_select_docs.append( docs_list[file_ptr] )
                        #ADD GOOGLE SCORE
                        this_itr_select_docs[-1][1][0] += google_scorer.get_score_by_tid_key(tid, docs_list[file_ptr][0])

                        already_select_key_set.add( docs_list[file_ptr][1][2]['key'] )
                        #TODO CHECK:D 如果i!=0的时候  这个D是不是应该增大一些...
                        # D.append( docs_list[file_ptr][1][2] )
                        file_ptr += 1

                    # jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]
                    # print "already_select_key_set:", already_select_key_set
                    this_itr_select_docs = sorted(this_itr_select_docs, reverse=True, key=lambda d:d[1][0])
                    jig_format_docs = irsys.items2jigdocs(this_itr_select_docs)
                    print "USE:", jig_format_docs
                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    print "i itr:", i
                    if iresult is not None:
                        this_itr_not_on_topic_cnt = 0
                        for ir, _ in enumerate(iresult):
                            print _
                            if _['on_topic'] == 0:
                                this_itr_not_on_topic_cnt += 1
                            if i == 0:continue
                            if _['on_topic'] == 1:
                                print "IS THIS BUG?:", this_itr_select_docs[ir][0]
                                print "当使用搜索引擎结果的时候D append:", this_itr_select_docs[ir][1][2]
                                D.append(this_itr_select_docs[ir][1][2])
                                D[-1][SCORE] = this_itr_select_docs[ir][1][0]
                            else:
                                print "CCC this_itr_select_docs[ir]:", this_itr_select_docs[ir]
                                print "this_itr_select_docs[ir][0]:", this_itr_select_docs[ir][0]
                                not_on_topic_doc_set[this_itr_select_docs[ir][0]] = this_itr_select_docs[ir][1][2]
                    update_state(already_cover_topic_dict, iresult)
                    if this_itr_not_on_topic_cnt >= every_itr_doc_cnt:
                        this_topic_use_google = True

                    continue
                else:

                    #use xQuAD to select best docs
                    #TODO:检查整个代码逻辑, docs_list应该是保持有candidate_cnt个没有select的
                    R_left = get_R_left(docs_list, already_select_key_set)
                    this_itr_select_docs = []
                    #这里的this_itr_select_docs的每一个元素的格式是 [doc{}, xquad score, rel_score, div_score格式]

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
                        this_itr_select_docs[-1][1] += google_scorer.get_score_by_tid_key(tid,  d[0][KEY])
                        # D.append(d[0])
                        # D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])
                        print "len R_left, D, this_itr_select_docs, already_select_keys:", len(R_left), len(D), len(
                            this_itr_select_docs), len(already_select_key_set)

                    this_itr_select_docs = sorted(this_itr_select_docs, reverse=True, key=lambda d:d[1])
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
                            this_itr_not_on_topic_cnt = 0
                            if iresult is not None:
                                for ir, _ in enumerate(iresult):
                                    print _
                                    if _['on_topic'] == 1:
                                        D.append(this_itr_select_docs[i][0])
                                        D[-1][SCORE] = this_itr_select_docs[i][1]
                                    else:
                                        # print "CCC this_itr_select_docs[ir]:", this_itr_select_docs[ir]
                                        # print "this_itr_select_docs[ir][0]:", this_itr_select_docs[ir][0]
                                        not_on_topic_doc_set[this_itr_select_docs[ir][0][KEY]] = this_itr_select_docs[ir][0]
                                        this_itr_not_on_topic_cnt += 1
                            update_state(already_cover_topic_dict, iresult)
                            if this_itr_not_on_topic_cnt >= every_itr_doc_cnt:
                                this_topic_use_google = True
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



if __name__ == '__main__':
    pass

__END__ = True