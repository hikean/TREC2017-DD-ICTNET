# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/24 上午4:41
# @version: 1.0


def xQuAD_clean(topics = EBOLA_TOPICS,
                suggestor=None,
                if_use_clean_text=True,
                boost_params=1,
                if_stem=True,
                candidate_doc_cnt = 700,
                tot_itr_times = 2,
                every_itr_doc_cnt = 5,
                use_subquery_cnt = 5,
                lm_lmd = 1.0,
                xquad_lmd = 0.6,
                idf_dict = None,
                jig = None,
                irsys = None
                ):

    # from src.utils.data_utils import basic_preprocess
    # logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    # if if_use_clean_text:
    #     print "load:", LMDirichlet_without_stem_lower
    #     lm.load(LMDirichlet_clean_Json)
    # else:
    #     print "load:", LMDirichlet_without_stem_lower
    #     # lm.load(LMDirichlet_Json)
    #     lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    # logging.info("get all solrs...")
    # solrs = get_all_ebola_solrs()
    # print "solr cnt:", len(solrs)
    # # w = [1] * len(solrs)
    # # w = [3, 1, 1, 1, 1] #提高1.5%
    # irsys = IRSys(solrs, ws=w)
    #
    # jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd
            print "if_stem:", if_stem
            print "if_use_clean_text:", if_use_clean_text
            print "candidate doc cnt:", candidate_doc_cnt

        # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            # query_word_list = basic_preprocess(topic, if_lower=True, if_stem=if_stem)
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not idf_dict.has_key(_):
                    print "!!!!==> idf_dict not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list, if_stem=if_stem)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)
            check_cnt = 0
            print "??????????++++++!!!!!!!!!>>>>>>>>>CHECK DC DICT :"
            for k in dc_dict.keys():
                print "dc k,v:", k, dc_dict[k]
                check_cnt += 1
                if check_cnt >= 1:
                    break


            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            # subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            subquerys = clean_subquery_list(subquerys, idf_dict, if_stem=if_stem, query_words=query_word_list)
            # subquerys = clean_subquerys_to_query_lists_and_filter_query(subquerys, lm, if_stem=if_stem,
            #                                                             query_words=query_word_list)
            print "===> subqueries:", subquerys

            file_ptr = 0
            for i in range(tot_itr_times):
                print "itr:", i, " tid:", tid
                this_itr_select_docs = []
                if i == 0 or len(subquerys) == 0:
                    if len(subquerys) == 0:
                        print "======@@@@@@@@@@@@> subquery cnt is zero, tid, topic:", tid, topic
                    print docs_list[0]
                    while len(this_itr_select_docs) < 5  and file_ptr < len(docs_list):
                        if docs_list[file_ptr][0] in already_select_key_set:
                            continue
                        this_itr_select_docs.append( docs_list[file_ptr][1][2] )
                        already_select_key_set.add( docs_list[file_ptr][1][2]['key'] )
                        #TODO CHECK:D
                        # D.append( docs_list[file_ptr][1][2] )
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        if type(iresult) is list:
                            for _ in iresult:
                                print _
                        else:
                            print iresult
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        print "==== [INFO] R_left cnt:", len(R_left)
                        ranked_docs = xquad.select_doc_u_cos(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict,
                                              ret_rel_div_score=True)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        if d[0][KEY] in already_select_key_set:
                            print "############!!!!!!!!!ERROR >>>>>>>>>>>> SELECT DUP:", d[KEY]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])
                        print "len R_left, D, this_itr_select_docs, already_select_keys:", len(R_left), len(D), len(
                        this_itr_select_docs), len(already_select_key_set)

                    # this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]
                    this_itr_select_docs = []
                    for i,_ in enumerate(ranked_docs):
                        if _[0][KEY] in already_select_key_set:continue
                        this_itr_select_docs.append(_)
                        if len(this_itr_select_docs) >= 5:
                            if i >= 5:
                                print "^^^^^^^^^ [ERROR] ThErE must be DUP......!!, i:", i
                            break

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        if type(iresult) is list:
                            for _ in iresult:
                                print _
                        else:
                            print iresult
            print "======== CHECK DUP:", len(already_select_key_set), tot_itr_times * 5
            if tot_itr_times * 5 != len(already_select_key_set):
                print "[ERROR]  FUCK"
            jig.judge()

__END__ = True