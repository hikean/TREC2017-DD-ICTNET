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
# from src.utils.data_utils import basic_preprocess

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
        if  key == 'ebola-dfc55032fd9f75ba95252e887f3c4d9f3fe281c7a6c3ff5ec7fc773eb8a98f24':
            print "======> CHECK cal_dc_dicts:", key #, ret
        ret[key] = dc

    return ret

def clean_subquerys_to_query_lists(subquerys, lm = None, if_stem=False):
    # from src.utils.data_utils import basic_preprocess
    if lm is not None:
        print "USING LM TO FILTER subqueries"
    ret = []
    for q in subquerys:
        words = basic_preprocess_for_query(q, if_lower=True, if_stem=if_stem)
        if lm is not None:
            new_words = []
            for w in words:
                if not lm.C.has_key(w):
                    print "word not int corpus:", w
                    continue
                new_words.append(w)
            words = new_words
        if len(words) == 0:
            print "====!!!!===>clean_subquerys_to_query_lists, all words of subquery is filtered:", q
            continue
        ret.append( words )

    return ret


def clean_subquerys_to_query_lists_and_filter_query(subquerys, lm = None, if_stem=False, query_words=[], idf_dict=None):
    # from src.utils.data_utils import basic_preprocess
    if lm is not None:
        print "USING LM TO FILTER subqueries"
    ret = []
    for q in subquerys:
        words = basic_preprocess_for_query(q, if_lower=True, if_stem=if_stem)
        if lm is not None:
            new_words = []
            for w in words:
                if not lm.C.has_key(w):
                    print "word not int corpus:", w
                    continue
                new_words.append(w)
            words = new_words
        if len(words) == 0:
            print "====!!!!===>clean_subquerys_to_query_lists, all words of subquery is filtered:", q
            continue
        if query_words == words:
            print "query is equal to subquery, query, subquery:", query_words, words
            continue
        ret.append( words )

    return ret


def clean_subquerys_to_query_lists_and_filter_query_by_idf_dict(subquerys, lm = None, if_stem=False, query_words=[], idf_dict=None):
    # from src.utils.data_utils import basic_preprocess

    ret = []
    for q in subquerys:
        words = basic_preprocess_for_query(q, if_lower=True, if_stem=if_stem)
        if lm is not None:
            new_words = []
            for w in words:
                if (not idf_dict is None) and (not idf_dict.has_key(w)):
                    print "word not int corpus:", w
                    continue
                new_words.append(w)
            words = new_words
        if len(words) == 0:
            print "====!!!!===>clean_subquerys_to_query_lists, all words of subquery is filtered:", q
            continue
        if query_words == words:
            print "query is equal to subquery, query, subquery:", query_words, words
            continue
        ret.append( words )

    return ret

def get_R_left(doc_list, selected_key_set):
    '''
    :param doc_list: items那种类型
    :param selected_key_set:
    :return: 是正常的dict格式的doc
    '''
    ret = []
    for d in doc_list:
        if d[0] not in selected_key_set:
            ret.append( d[1][2] )
            ret[-1][SCORE] = d[1][0]
        # if len(ret) == 1:
        #     print '====> CHECK get R left:', ret[-1]
            # print ret[-1]['key']
    if len(ret) == 0:
        print "[ERROR] when cal R_left"
    return ret

def preproces_docs_list(docs_list, field='content', if_stem=False):
    for i in range(len(docs_list)):
        # if i == 0:
        #     print "BEFORE:",  docs_list[i][1][2][field]
        docs_list[i][1][2][field] = basic_preprocess(docs_list[i][1][2][field], if_lower=True, if_stem=if_stem)
        if i == 0:
            print "**********>>>>> AFTER:", docs_list[i][1][2][field]

    return docs_list


def xQuAD_by_IRSys_ebola_without_query_feedback(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1e11):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd =  247.5 #2000.0


    from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        lm.load(LMDirichlet_clean_Json)
    else:
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)
    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=0.8, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "if lower:", True
        # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            query_word_list = basic_preprocess(topic, if_lower=True)
            print "query_word_list:", query_word_list

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:1000]
            docs_list = preproces_docs_list(docs_list)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)


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

                    subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]

                    subquerys = clean_subquerys_to_query_lists(subquerys, lm)
                    print "===> subqueries:", subquerys

                    ranked_docs = xquad.select_doc_u(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict)

                    for d in ranked_docs[0:5]:
                        D.append( d[0] )
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()


def xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1e7):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd = 2000.0
    xquad_lmd = 0.8

    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd

        # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            query_word_list = basic_preprocess(topic, if_lower=True)
            print "query_word_list:", query_word_list

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:700]
            docs_list = preproces_docs_list(docs_list)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)

            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            subquerys = clean_subquerys_to_query_lists(subquerys, lm)
            print "===> subqueries:", subquerys


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
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        ranked_docs = xquad.select_doc_u(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        if i == 0:
                            print "-----CHECK SCORE->>>:", d
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()

def xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1e7, if_stem=True):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd = 2000.0
    xquad_lmd = 0.6

    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        print "load:", LMDirichlet_without_stem_lower
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd

        # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            # query_word_list = basic_preprocess(topic, if_lower=True, if_stem=if_stem)
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not lm.C.has_key(_):
                    print "!!!!==> LM not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:700]
            docs_list = preproces_docs_list(docs_list)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)

            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            print "===> subqueries:", subquerys


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
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        ranked_docs = xquad.select_doc_u(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        if i == 0:
                            print "-----CHECK SCORE->>>:", d
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()


def xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1, if_stem=True, candidate_doc_cnt = 700):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 8
    lm_lmd = 1.0
    xquad_lmd = 0.8

    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        print "load:", LMDirichlet_without_stem_lower
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd
            print "candidate_doc_cnt:", candidate_doc_cnt

        # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            # query_word_list = basic_preprocess(topic, if_lower=True, if_stem=if_stem)
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not lm.C.has_key(_):
                    print "!!!!==> LM not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list, if_stem=if_stem)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)

            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            # subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            subquerys = clean_subquerys_to_query_lists_and_filter_query(subquerys, lm, if_stem=if_stem, query_words=query_word_list)
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
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    jig.run_itr(jig_format_docs, topic_id=tid)
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        ranked_docs = xquad.select_doc_u_cos(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict, ret_rel_div_score=True)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()


def xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_self_subtopic(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1, if_stem=True, candidate_doc_cnt = 700):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd = 2000.0
    xquad_lmd = 0.8

    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        print "load:", LMDirichlet_without_stem_lower
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd

        # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            # query_word_list = basic_preprocess(topic, if_lower=True, if_stem=if_stem)
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not lm.C.has_key(_):
                    print "!!!!==> LM not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)

            # subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            # # subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            # subquerys = clean_subquerys_to_query_lists_and_filter_query(subquerys, lm, if_stem=if_stem, query_words=query_word_list)

            subquerys = [query_word_list]

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
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    jig.run_itr(jig_format_docs, topic_id=tid)
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        ranked_docs = xquad.select_doc_u(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict, ret_rel_div_score=True)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()


# def cal_all


def xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_score(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1, if_stem=True, candidate_doc_cnt = 700):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd = 2000.0
    xquad_lmd = 0.8

    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        print "load:", LMDirichlet_without_stem_lower
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd

        # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            # query_word_list = basic_preprocess(topic, if_lower=True, if_stem=if_stem)
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not lm.C.has_key(_):
                    print "!!!!==> LM not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)

            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            # subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            subquerys = clean_subquerys_to_query_lists_and_filter_query(subquerys, lm, if_stem=if_stem, query_words=query_word_list)
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
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    jig.run_itr(jig_format_docs, topic_id=tid)
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        ranked_docs = xquad.select_doc_u(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict, ret_rel_div_score=True)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()


def xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_t_cos_sim(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1, if_stem=True, candidate_doc_cnt = 700):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd = 1.0
    xquad_lmd = 0.6

    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        print "load:", LMDirichlet_without_stem_lower
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd

        # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            logging.info("search for topic %s %s" % (tid, topic))
            logging.info("preprocess data...")
            # query_word_list = basic_preprocess(topic, if_lower=True, if_stem=if_stem)
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not lm.C.has_key(_):
                    print "!!!!==> LM not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list, if_stem=if_stem)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)
            check_cnt = 0
            print "??????????++++++!!!!!!!!!>>>>>>>>>CHECK DC DICT :"
            for k in dc_dict.keys():
                print "dc k,v:", k, dc_dict[k]
                check_cnt += 1
                if check_cnt >= 5:
                    break


            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            # subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            subquerys = clean_subquerys_to_query_lists_and_filter_query(subquerys, lm, if_stem=if_stem, query_words=query_word_list)
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
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    jig.run_itr(jig_format_docs, topic_id=tid)
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        ranked_docs = xquad.select_doc_u(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict,
                                              ret_rel_div_score=True)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()



def xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_tf_idf_cos_sim(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1, if_stem=True, candidate_doc_cnt = 700):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd = 1.0
    xquad_lmd = 0.6

    logging.info("loading idf dict")
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


    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        print "load:", LMDirichlet_without_stem_lower
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd
            print "if_stem:", if_stem
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
                if not lm.C.has_key(_):
                    print "!!!!==> LM not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list, if_stem=if_stem)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)
            check_cnt = 0
            print "??????????++++++!!!!!!!!!>>>>>>>>>CHECK DC DICT :"
            for k in dc_dict.keys():
                print "dc k,v:", k, dc_dict[k]
                check_cnt += 1
                if check_cnt >= 5:break


            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            # subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            subquerys = clean_subquerys_to_query_lists_and_filter_query(subquerys, lm, if_stem=if_stem, query_words=query_word_list)
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
                        D.append( docs_list[file_ptr][1][2] )
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    jig.run_itr(jig_format_docs, topic_id=tid)
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        ranked_docs = xquad.select_doc_u_cos_tf_idf(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict, ret_rel_div_score=True, idf_dict = idf_dict)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                        #TODO:这里需要检查一下要不要加D
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()


def xQuAD__without_query_feedback_select_one_by_one_cos_sim_wc(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1, if_stem=True, candidate_doc_cnt = 700):

    tot_itr_times = 2
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd = 1.0
    xquad_lmd = 0.85

    logging.info("loading idf dict")
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


    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        print "load:", LMDirichlet_without_stem_lower
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    print "USE ONLY LMD EBOLA SOLR"
    # solrs = get_all_ebola_solrs()
    solrs = [
        SolrClient(solr_url=FULL_SOLR_URL),  # LMD, FULL
    ]
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd
            print "if_stem:", if_stem
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
                if not lm.C.has_key(_):
                    print "!!!!==> LM not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list, if_stem=if_stem)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)
            check_cnt = 0
            print "??????????++++++!!!!!!!!!>>>>>>>>>CHECK DC DICT :"
            for k in dc_dict.keys():
                print "dc k,v:", k, dc_dict[k]
                check_cnt += 1
                if check_cnt >= 1:break


            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            # subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            subquerys = clean_subquerys_to_query_lists_and_filter_query(subquerys, lm, if_stem=if_stem, query_words=query_word_list)
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
                        # D.append( docs_list[file_ptr][1][2] )
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    jig.run_itr(jig_format_docs, topic_id=tid)
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    # ranked_docs = []
                    # for ixquad_selected in range(every_itr_doc_cnt):
                    #     ranked_docs = xquad.select_doc_u_cos(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict, ret_rel_div_score=True)
                    #     d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                    #     # if i == 0:
                    #     if d[0][KEY] in already_select_key_set:
                    #         print "############!!!!!!!!!ERROR >>>>>>>>>>>> SELECT DUP:", d[KEY]
                    #     print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                    #     #TODO:这里需要检查一下要不要加D
                    #     D.append(d[0])
                    #     D[-1][SCORE] = d[1]
                    #     already_select_key_set.add(d[0][KEY])
                    #     R_left.remove(d[0])

                    # this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]
                    # this_itr_select_docs = []
                    # for idx_,_ in enumerate(ranked_docs):
                    #     if _[0][KEY] in already_select_key_set:continue
                    #     this_itr_select_docs.append(_)
                    #     if len(this_itr_select_docs) >= 5:break


                    this_itr_select_docs = []

                    for ixquad_selected in range(every_itr_doc_cnt):
                        print "==== [INFO] R_left cnt:", len(R_left)
                        ranked_docs = xquad.select_doc_u_cos(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict,
                                                             ret_rel_div_score=True)
                        ptr_ = 0
                        while ranked_docs[ptr_][0][KEY] in already_select_key_set:
                            ptr_ += 1

                        print "SELECT PTR:", ptr_

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
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()


def xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_tf_idf_cos_sim_clean_title(topics = EBOLA_TOPICS, w = None, suggestor=None, if_use_clean_text=False, boost_params=1, if_stem=True, candidate_doc_cnt = 700):

    tot_itr_times = 5
    every_itr_doc_cnt = 5
    use_subquery_cnt = 5
    lm_lmd = 1.0
    xquad_lmd = 0.6

    logging.info("loading idf dict")
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


    # from src.utils.data_utils import basic_preprocess
    logging.info("loading... LMD...")
    lm = LMDirichlet(lmd=lm_lmd)
    if if_use_clean_text:
        print "load:", LMDirichlet_without_stem_lower
        lm.load(LMDirichlet_clean_Json)
    else:
        print "load:", LMDirichlet_without_stem_lower
        # lm.load(LMDirichlet_Json)
        lm.load(LMDirichlet_without_stem_lower)

    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [1] * len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
            print "tot_itr_times:", tot_itr_times
            print "every_itr_doc_cnt:", every_itr_doc_cnt
            print "use_subquery_cnt:", use_subquery_cnt
            print "lm_lmd:", lm_lmd
            print "xquad_lmd:", xquad_lmd
            print "if_stem:", if_stem
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
                if not lm.C.has_key(_):
                    print "!!!!==> LM not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list, if_stem=if_stem)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)

            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            # subquerys = clean_subquerys_to_query_lists(subquerys, lm, if_stem=if_stem)
            subquerys = clean_subquerys_to_query_lists_and_filter_query_by_idf_dict(subquerys, lm, if_stem=if_stem, query_words=query_word_list, idf_dict=idf_dict)
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
                        file_ptr += 1

                    jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]

                    jig.run_itr(jig_format_docs, topic_id=tid)
                # elif i == 1:
                else:
                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    ranked_docs = []
                    for ixquad_selected in range(every_itr_doc_cnt):
                        ranked_docs = xquad.select_doc_u_cos_tf_idf(query_word_list, R_left, D, subquerys, dc_dicts=dc_dict, ret_rel_div_score=True, idf_dict = idf_dict)
                        d = ranked_docs[0] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:]
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])

                    this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    jig_format_docs = []
                    for d in this_itr_select_docs:
                        #TODO:需要检查一下，这里的score，因为第一轮的score和这里太不一样了，需要考虑下怎么处理，需要验证一下score随便设置是不是可以的...
                        jig_format_docs.append(
                            (0, d[0][KEY], d[1] * boost_params)
                        )


                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    if iresult is not None:
                        print "itr result , i:", i
                        for _ in iresult:
                            print _

            jig.judge()

def test_1():
    suggestor = SubQueryGenerator_by_title(TITLE_BING)
    xQuAD_by_IRSys_ebola_without_query_feedback(topics=EBOLA_TOPICS, suggestor=suggestor)

'''
一个一个得返回文档
'''
def test_2():
    suggestor = SubQueryGenerator_by_title(TITLE_BING)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one(topics=EBOLA_TOPICS, suggestor=suggestor)

'''
使用google的
做stem和大小写
'''
def test_3():
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer(topics=EBOLA_TOPICS, suggestor=suggestor,
                                                                         if_use_clean_text=True)


'''
做stemmer
'''
def test_4():
    suggestor = SubQueryGenerator_by_title(TITLE_BING)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer(topics=EBOLA_TOPICS, suggestor=suggestor, if_use_clean_text=True)



'''
修改div的概率评分
'''
def test_5():
    #xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div(topics=EBOLA_TOPICS, suggestor=suggestor,
                                                                         if_use_clean_text=True)


'''
加了一些规则：
1、删除跟query一样的Subquery
2、没有subquery的，直接按搜索引擎结果
'''
def test_6():
    #xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div(topics=EBOLA_TOPICS, suggestor=suggestor,
                                                                         if_use_clean_text=True, boost_params=1.0)


'''
和6一样 只是用了title, 以及candidate doc cnt=70, 因为div_score实在太高了。。。
'''
def test_7():
    suggestor = SubQueryGenerator_by_title(TITLE_BING)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div(topics=EBOLA_TOPICS,
                                                                                   suggestor=suggestor,
                                                                                   if_use_clean_text=True,
                                                                                   boost_params=1.0, candidate_doc_cnt=70)



'''
和6一样，但是限制candidate 70
'''
def test_8():
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div(topics=EBOLA_TOPICS,
                                                                                   suggestor=suggestor,
                                                                                   if_use_clean_text=True,
                                                                                   boost_params=1.0,
                                                                                   candidate_doc_cnt=200)


'''
在6的基础上，只改一点subquery就是自己
'''
def test_9():
    #xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_self_subtopic(topics=EBOLA_TOPICS, suggestor=suggestor,
                                                                         if_use_clean_text=True, boost_params=1.0)

# '''
# 在test_6的基础上，加规则
# 1、如果div score * 10 < rel_score 直接按照之前的搜索引擎的rel score排序, 只要同一批里面4个出现这种情况就认为是这样的。。
# 就认为div对rel的改变太低，直接用搜索引擎的rel排序
# 3、
# '''

'''
除以对应概率试试
'''
def test_10():
    # suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    # suggestor = SubQueryGenerator_by_title(TITLE_BING)
    suggestor = SubQueryGenerator_by_title(TITLE_GOOGLE)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div(topics=EBOLA_TOPICS,
                                                                                   suggestor=suggestor,
                                                                                   if_use_clean_text=True,
                                                                                   boost_params=1.0,
                                                                                   candidate_doc_cnt=100)


def test_11():
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div(topics=EBOLA_TOPICS,
                                                                                   suggestor=suggestor,
                                                                                   if_use_clean_text=True,
                                                                                   boost_params=1.0,
                                                                                   candidate_doc_cnt=80)



'''
cos sim 但是用title
'''
def test_12():
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_tf_idf_cos_sim(topics=EBOLA_TOPICS,
                                                                                   suggestor=suggestor,
                                                                                   if_use_clean_text=True,
                                                                                   boost_params=1.0,
                                                                                   candidate_doc_cnt=100)




'''
改成tf-idf cos sim
'''
def test_13():
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_tf_idf_cos_sim(topics=EBOLA_TOPICS,
                                                                                   suggestor=suggestor,
                                                                                   if_use_clean_text=True,
                                                                                   boost_params=1.0,
                                                                                   candidate_doc_cnt=30)


'''
改成tf-idf cos sim 用title
'''
def test_14():
    #
    # print "USING TITLE:", TITLE_GOOGLE
    # suggestor = SubQueryGenerator_by_title(TITLE_GOOGLE)

    print "USING GOOGLE SUGGESTOR:", GOOGLE_SUGGESTED
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)

    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_tf_idf_cos_sim_clean_title(topics=EBOLA_TOPICS,
                                                                                   suggestor=suggestor,
                                                                                   if_use_clean_text=True,
                                                                                   boost_params=1.0,
                                                                                   candidate_doc_cnt=40)


'''
修改了dc bug的cos sim 不用tf-idf而是次数
'''
def test_15():
    print "USING GOOGLE SUGGESTOR:", GOOGLE_SUGGESTED
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)

    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_t_cos_sim(
        topics=EBOLA_TOPICS,
        suggestor=suggestor,
        if_use_clean_text=True,
        boost_params=1.0,
        candidate_doc_cnt=30)

'''
修改了dc bug的LM
xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div
'''
def test_16():
    print "USING GOOGLE SUGGESTOR:", GOOGLE_SUGGESTED
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)

    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_t_cos_sim(
        topics=EBOLA_TOPICS,
        suggestor=suggestor,
        if_use_clean_text=True,
        boost_params=1.0,
        candidate_doc_cnt=30)


'''
复现cos sim tf-idf的第二轮 0.2000720，加了D之后0.1979887 因为topic-19变差
'''
def test_17():
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD_by_IRSys_ebola_without_query_feedback_select_one_by_one_stemer_boost_div_tf_idf_cos_sim(topics=EBOLA_TOPICS,
                                                                                                  suggestor=suggestor,
                                                                                                  if_use_clean_text=True,
                                                                                                  boost_params=1.0,
                                                                                                  candidate_doc_cnt=30)


'''
复现cos sim 词频的第二轮
已经复现出来 不加D
all	 0.2043294	 0.2040517	 0.4203910
'''
def test_18():
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    xQuAD__without_query_feedback_select_one_by_one_cos_sim_wc(topics=EBOLA_TOPICS,
                                                                                                  suggestor=suggestor,
                                                                                                  if_use_clean_text=True,
                                                                                                  boost_params=1.0,
                                                                                                  candidate_doc_cnt=80)


if __name__ == '__main__':
    # test_2()
    # test_4()

    # test_3()

    # test_5()

    # test_6()

    # test_8()
    # test_9()
    # test_13()
    # test_14()
    # test_15()

    # test_16()
    #复现最好的第二轮
    # test_13()
    test_18()

__END__ = True