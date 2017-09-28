# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/22 上午9:23
# @version: 1.0


'''

用融合的irsys

算法流程：
1、第一轮可控，
直接xQuAD + Gooogle Suggestor 或者XXX


===如果第一轮没有搜到相关文档，那么

2、已选文档
考虑：
本轮选的时候--->是否考虑本轮选择的文章/ 即使考虑了已后也清除
jig确定相关加入

记录jig返回的话题

3、用Word2vec和正常相似来做...

4、动态限定文档...

5、按照句子级别的匹配
然后相似的句子和jig返回的passage_text连接在一起 求tf-idf筛选词扩充

6、根据unrelevence的jig返回的信息...暂时考虑不用
看是不是会出现这样的情况，就是一片文档的重复文档没在ground data...

可以考虑完全一样的文章 如果相似度一般就不考虑。。。


7、如果在D中的文章不是on-topic 可能需要删除...


===


实现细节，

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
from src.utils.stop_stratage import *
# from xQuAD_with_feedback import get_top_docs_from_doc_list


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


    lm = LMDirichlet(lmd=lm_lmd)
    logging.info("initing xQuAD...")
    xquad = xQuAD(lm, lmd=xquad_lmd, alpha=1.0)

    for tid, topic in topics:
            logging.info("search for topic %s %s" % (tid, topic))
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
            # already_cover_topic_dict
            already_cover_topic_dict = {}

            logging.info("preprocess data...")
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not idf_dict.has_key(_):
                    print "!!!!==> idf_dict not has key:", _

            docs_list = irsys.retrieve_docs([topic], with_query_field=True)[0:candidate_doc_cnt]
            docs_list = preproces_docs_list(docs_list, if_stem=if_stem)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)
            # check_cnt = 0
            # print "??????????++++++!!!!!!!!!>>>>>>>>>CHECK DC DICT :"
            # for k in dc_dict.keys():
            #     print "dc k,v:", k, dc_dict[k]
            #     check_cnt += 1
            #     if check_cnt >= 1:
            #         break

            subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
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

                    jig.run_itr(jig_format_docs, topic_id=tid)
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

                    # this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]
                    this_itr_select_docs = []
                    for i,_ in enumerate(ranked_docs):
                        if _[0][KEY] in already_select_key_set:continue
                        this_itr_select_docs.append(_)


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

'''
通过词频计算相似度, 清理出来干净句子
'''
def cal_sim_by_wc(doc_a, doc_b, if_stem=True, if_stem_b=True):
    doc_a = basic_preprocess(doc_a, if_lower=True, if_stem=if_stem)
    if if_stem_b:
        doc_b = basic_preprocess(doc_b, if_lower=True, if_stem=if_stem)

    return cos_dis(doc_a, doc_b), doc_a, doc_b

def detect_most_sim_sents(key_sent, doc, sim_limit=0.8, sim_func=cal_sim_by_wc, if_stem=True):
    '''
    :param sent:
    :param doc:
    :param sim_limit:
    :param sim_func:
    :return:
    '''
    candidates = []
    sents = clean_error_words_splitSentence(doc)
    key_sent = basic_preprocess(key_sent, if_stem=if_stem)
    clean_sents = []
    for s in sents:
        sim, clean_s, clean_key_sent = sim_func(s, key_sent, if_stem=if_stem, if_stem_b=False)
        clean_sents.append( clean_s )
        if sim >= sim_limit: candidates.append( [clean_s, sim] )

    print "candidate cnt:", len(candidates)

    return candidates

def concat_sents_and_filter_words_by_tf_idf(rel_sent=[],idf_dict = {}, ret_cnt = 10):
    tot_words = []
    for s in rel_sent:
        tot_words += s
    sz = len(tot_words)
    words_counter = Counter(tot_words)
    for w in words_counter.keys():
        words_counter[w] = words_counter[w] * idf_dict[w] / float(sz)
    words_counter = dict(words_counter)
    words_counter = sorted( words_counter.items(), reverse=True, key=lambda d:d[1])[0:ret_cnt]
    return words_counter



'''
already_cover_topic_dict:
{
    subtopic_id: {
        rating_0:不相关的文档
        rating_1:[ article_cnt, [passage_text,], ]
        rating_2: 同上
        rating_3:
        rating_4:

    }

}

'''
def update_state(already_cover_topic_dict, jig_rslts):
    for info in jig_rslts:
        info['on_topic'] = int (info['on_topic'])
        if info['on_topic'] == 0:
            # if not already_cover_topic_dict.has_key(NOT_ON_TOPIC):
            #     already_cover_topic_dict[NOT_ON_TOPIC] = 1
            # else:
            #     already_cover_topic_dict[NOT_ON_TOPIC] += 1
            continue
        subtopics = info['subtopics']
        for subtopic in subtopics:
            subtopic_id = subtopic['subtopic_id']
            subtopic['rating'] = int(subtopic['rating'])
            rating = subtopic['rating']
            passage_text = subtopic['passage_text']
            if not already_cover_topic_dict.has_key(subtopic_id):
                already_cover_topic_dict[subtopic_id] = {}
            if not already_cover_topic_dict.has_key(rating):
                already_cover_topic_dict[subtopic_id][rating] = [0, []]
            already_cover_topic_dict[subtopic_id][rating][0] += 1
            if passage_text.strip() not in already_cover_topic_dict[subtopic_id][rating][1]:
                already_cover_topic_dict[subtopic_id][rating][1].append( passage_text )
    return already_cover_topic_dict



# def update_state_with_sta(already_cover_topic_dict, jig_rslts):
#     for info in jig_rslts:
#         info['on_topic'] = int (info['on_topic'])
#         if info['on_topic'] == 0:continue
#         subtopics = info['subtopics']
#         for subtopic in subtopics:
#             subtopic_id = subtopic['subtopic_id']
#             subtopic['rating'] = int(subtopic['rating'])
#             rating = subtopic['rating']
#             passage_text = subtopic['passage_text']
#             if not already_cover_topic_dict.has_key(subtopic_id):
#                 already_cover_topic_dict[subtopic_id] = {}
#             if not already_cover_topic_dict.has_key(rating):
#                 already_cover_topic_dict[subtopic_id][rating] = [0, []]
#             already_cover_topic_dict[subtopic_id][rating][0] += 1
#             if passage_text.strip() not in already_cover_topic_dict[subtopic_id][rating][1]:
#                 already_cover_topic_dict[subtopic_id][rating][1].append( passage_text )
#     return already_cover_topic_dict

def remove_dup_from_words_by_set(docs):
    '''

    :param docs: [ [词干化后的一个文章的词] ]
    :return:
    '''
    ret = set()
    for d in docs:
        ret.add( tuple(d) )

    ret = [ list(d) for d in ret ]
    return ret


'''
这个会是最复杂的地方，
选择当前每个子话题最top的passage_text作为aspect，
'''
def passage_text_to_subqueries(already_cover_topic_dict, user_top_k_text=2):
    '''

    :param already_cover_topic_dict:
    :param user_top_k_text:
    :return: user_top_k_text个子话题的text 没有做过Clean， 每个话题一个str 跟没有clean的subtipic一样
    '''
    aspect_sents = []
    CHECK = True
    for subtopic_id, info in already_cover_topic_dict.items():
        one_aspect = []
        select_cnt = 0
        for rate in RATES:
            if info.has_key(rate):
                one_aspect += info[rate][1]
                if CHECK:
                    print "CHECK passage_text_to_subqueries, rate, info[rate]:", rate, info[rate]
                    CHECK = False
                select_cnt += 1
                print  "subtopic_id", subtopic_id, " select rate:", rate
                print "passage_text_to_subqueries, subtopic_id, use rate:", subtopic_id, rate
            if select_cnt >= user_top_k_text:
                #TODO:这里没有Break的时候能act第二轮0.2...

                break

        one_aspect = ' '.join(one_aspect)
        aspect_sents.append(one_aspect)

    return aspect_sents

'''
这个会是最复杂的地方，
选择当前每个子话题最top的passage_text作为aspect，
'''
def passage_text_to_expand_query(already_cover_topic_dict, user_top_k_text=2, ignore_limit_cnt=4, qe_score_limit=3):
    '''

    :param already_cover_topic_dict:
    :param user_top_k_text:
    :param ignore_limit_cnt: 已经在这个话题覆盖了超过这个数字的文章之后，就不再在这个subtopic下扩展查询
    :param qe_score_limit: >=这个分数的才用于扩展
    :return: user_top_k_text个子话题的text 没有做过Clean， 每个话题一个str 跟没有clean的subtipic一样
    '''
    aspect_sents = []
    CHECK = True
    for subtopic_id, info in already_cover_topic_dict.items():
        one_aspect = []
        select_cnt = 0
        for rate in RATES:
            #TODO:这里改成负权重
            if rate < qe_score_limit:continue
            if info.has_key(rate):
                one_aspect += info[rate][1]
                if CHECK:
                    print "CHECK passage_text_to_subqueries, rate, info[rate]:", rate, info[rate]
                    CHECK = False
                select_cnt += 1
                print  "subtopic_id", subtopic_id, " select rate:", rate
                print "passage_text_to_subqueries, subtopic_id, use rate:", subtopic_id, rate
            if select_cnt >= user_top_k_text:
                #TODO:这里没有Break的时候能act第二轮0.2...

                break

        one_aspect = ' '.join(one_aspect)
        aspect_sents.append(one_aspect)

    return aspect_sents



def cal_sim_by_word_set(doc_a, doc_b):
    a = set(doc_a)
    b = set(doc_b)
    bing = a | b
    jiao = a & b
    return float(jiao) / float(bing)

def judge_dup_doc(doc_a, doc_b, sim_limit=0.8, if_stem=False):
    da = basic_preprocess(doc_a, if_stem=if_stem)
    db = basic_preprocess(doc_b, if_stem=if_stem)
    sim = cal_sim_by_word_set(da, db)
    return sim >= sim_limit

def select_query_expansion_words_by_passage_text( idf_dict, passage_text_words , qe_words_cnt = 5 ):
    '''
    在调用之前需要先过滤一下passage text
    :param idf_dict:
    :param passage_text_words:
    :param qe_words_cnt:
    :return:一个dict, k:words, v:tf-idf
    '''
    sz = float(len(passage_text_words))
    ret = {}
    cp = Counter(passage_text_words)
    for w in cp.keys():
        w = w.strip()
        if len(w) == 0:
            print "[WARN]select_query_expansion_words_by_passage_text:", w
            continue
        if not idf_dict.has_key(w):
            print "[WARN] select_query_expansion_words_by_passage_text idf_dict not has word:", w
            continue
        ret[w] = cp[w] / sz * idf_dict[w]

    return dict(
        sorted(ret.items(), reverse=True, key=lambda d: d[1])[0:qe_words_cnt]
    )


def dicts2query(q, eq, sp=' '):
    '''
    :param q: 为了保证次序，这个是一个list
    :param eq: 这个事一个Dict
    :param sp:
    :return: 查询以及 query_word_list（这个是词干化之后的。。）
    '''
    ret = ''
    ret_word_list = []
    for w in q:
        ret += w + '^' + str(1.0) + sp

        ret_word_list.append(w)
    for w in eq.keys():
        ret += w + '^' + str(eq[w]) + sp
        ret_word_list.append(w)
    ret_word_list = stemmer_by_porter(ret_word_list)

    return ret.strip(), ret_word_list

def append_docs_to_doc_list(doc_list, keys, corpus, field='content', if_filter_null=False):
    '''

    :param doc_list:
    :param keys:
    :param corpus: corpus是做过clean的
    :return:
    '''
    ret = []
    for i,k in enumerate(keys):
        # if i == 0:
        #     print  "CHECK doc_list:", doc_list
        if len(corpus[i]) == 0:
            print "ERROR EMPTY CORPUS, KEY:", k
        doc_list[i][1][2][field] = corpus[i]
        if if_filter_null:
            if len(corpus[i]) != 0:
                ret.append(doc_list[i])
        else:
            ret.append(doc_list[i])

    return ret
    # doc_list = dict(doc_list)
    # for i,k in enumerate(keys):
    #     # if i == 0:
    #     #     print  "CHECK doc_list:", doc_list
    #     if len(corpus[i]) == 0:
    #         print "ERROR EMPTY CORPUS, KEY:", k
    #     doc_list[k][2][field] = corpus[i]
    # return doc_list.items()


def cal_qe_words_by_dif_subtopics(feedbacks, idf_dict_without_stem, if_lower=False, if_stem=False, every_expand_words_cnt = 5):
    '''
    每个subtopic里面扩展出来一些词 去重，然后扩展进查询
    :param feedbacks: 是一个list， 每一个是一个subtopic的passage_text的混合,
    :param idf_dict_without_stem:
    :param if_lower:
    :param if_stem:
    :return:
    '''
    ret_words_items = []

    for feedback in feedbacks:
        feedback_words = basic_preprocess(feedback, if_lower=if_lower, if_stem=if_stem)
        expand = select_query_expansion_words_by_passage_text(idf_dict_without_stem, feedback_words, qe_words_cnt=every_expand_words_cnt)
        ret_words_items += expand.items()

    return dict(ret_words_items)

def xQuAD_clean_use_local_data_without_feedback(topics = EBOLA_TOPICS,
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
                irsys = None,
                data_dir=EBOLA_CLEAN_FULL_DATA_DIR,
                data_field='content',
                key2id_dict = {},
                use_jig_feedback_cnt_limit = 2,
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

            # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            # already_cover_topic_dict
            # already_cover_topic_dict，格式 key:subtopic_id，
            # v: dict形式， key是相关度， v [这个subtopic下已经有的文章个数, [passage_text], 筛选出来的词的list, ]
            already_cover_topic_dict = {}

            logging.info("preprocess data...")
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not idf_dict.has_key(_):
                    print "!!!!==> idf_dict not has key:", _

            # docs_list = irsys.retrieve_docs([topic], query_field=data_field, with_query_field=False)[0:candidate_doc_cnt]
            tot_docs_list = irsys.retrieve_docs([topic], query_field=data_field, with_query_field=False)[0:(tot_itr_times+1)*candidate_doc_cnt]

            tot_docs_keys = get_doc_keys_from_doc_list(tot_docs_list)
            print "CHECK docs_list, docs_keys cnt:", len(tot_docs_list), len(tot_docs_keys)
            corpus = get_corpus_by_keys(data_dir, key2id_dict, tot_docs_keys, if_stem=if_stem, field=data_field)
            tot_docs_list = append_docs_to_doc_list(tot_docs_list, tot_docs_keys, corpus, field=data_field, if_filter_null=True)
            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(tot_docs_list, content_field=data_field)

            google_subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            google_subquerys = clean_subquery_list(google_subquerys, idf_dict, if_stem=if_stem, query_words=query_word_list)

            print "===> google_subquerys:", google_subquerys


            for i in range(tot_itr_times):
                print "itr:", i, " tid:", tid

                if if_use_stop_stop_strategy:
                    not_on_topic_cnt = get_not_on_topic_cnt(already_cover_topic_dict)
                    print "CHECK IF STOP, not_on_topic_cnt:", not_on_topic_cnt, " stop at cnt:", stop_at_cnt
                    if not_on_topic_cnt >= stop_at_cnt:
                        print "STOP THIS TOPIC,tid:", tid
                        break



                print "already select cnt:", len(already_select_key_set), " tot_docs_list:", len(tot_docs_list)
                if (i+1) * every_itr_doc_cnt > len(tot_docs_list):
                    print "DOCS NOT ENOUGH:", tid, topic
                    break

                docs_list = get_top_docs_from_doc_list(tot_docs_list, already_select_key_set,
                                                       ret_cnt=candidate_doc_cnt)
                print "doc_list cnt:", len(docs_list)

                if i == 0:
                    if_use_jig_feedback = False
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


                if if_use_jig_feedback:
                    print "USE JIG PASSAGE TEXT AS subquery, itr:", i
                    # TODO:这里要试试是不是要做筛选词处理，另外要考虑passage_text是不是已经用过
                    subqueries = passage_text_to_subqueries(already_cover_topic_dict)
                    subqueries = clean_subquery_list(subqueries, idf_dict, if_stem=if_stem, query_words=query_word_list)
                    subqueries = remove_dup_from_words_by_set(subqueries)
                    subqueries_statics[tid][1] += 1
                else:
                    print "USE Suggested query as subquery, itr:", i
                    subqueries = google_subquerys
                    subqueries_statics[tid][0] += 1
                print "USE SUBQUERIES:"
                for _ in subqueries:
                    print _
                this_itr_select_docs = []
                if i == 0 or ( not if_use_jig_feedback and len(subqueries) == 0 ):
                    if len(subqueries) == 0:
                        print "======@@@@@@@@@@@@> subquery cnt is zero, tid, topic:", tid, topic
                    # print docs_list[0]
                    file_ptr = 0
                    while len(this_itr_select_docs) < 5  and file_ptr < len(docs_list):
                        if docs_list[file_ptr][1][2]['key'] in already_select_key_set:
                            continue
                        this_itr_select_docs.append( docs_list[file_ptr] )
                        already_select_key_set.add( docs_list[file_ptr][1][2]['key'] )
                        #TODO CHECK:D
                        # D.append( docs_list[file_ptr][1][2] )
                        file_ptr += 1

                    # jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]
                    # print "already_select_key_set:", already_select_key_set
                    jig_format_docs = irsys.items2jigdocs(this_itr_select_docs)

                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    print "i itr:", i
                    if iresult is not None:
                        for _ in iresult:
                            print _
                    update_state(already_cover_topic_dict, iresult)
                    continue
                else:

                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    # ranked_docs = []
                    # for ixquad_selected in range(every_itr_doc_cnt):
                    #     print "==== [INFO] R_left cnt:", len(R_left)
                    #     ranked_docs = xquad.select_doc_u_cos(query_word_list, R_left, D, subqueries, dc_dicts=dc_dict,
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
                        ranked_docs = xquad.select_doc_u_cos(query_word_list, R_left, D, subqueries, dc_dicts=dc_dict,
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
                print "tot_itr_times * 5 != len(already_select_key_set):", tot_itr_times * 5, len(already_select_key_set)
                print "[ERROR]  FUCK, tid, itr:", tid, i
                # exit(-1)

            jig.judge()



    for tid, v in subqueries_statics.items():
        print "tid:", tid, "suggested, jig feedback:", v

def cut_off_jig_feedback( subqueries, idf_dict , ret_words):

    ret = []
    for q in subqueries:
        cq = Counter(q)
        sz = float( len(q) )
        for k in cq.keys():
            cq[k] = cq[k] * idf_dict[k] / sz
        ws = sorted(cq.items(), reverse=True, key=lambda k:k[1])[0:ret_words]
        ret.append( list(dict(ws).keys()) )
    return ret

def xQuAD_clean_use_local_data_without_feedback_div_from1(topics = EBOLA_TOPICS,
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
                irsys = None,
                data_dir=EBOLA_CLEAN_FULL_DATA_DIR,
                data_field='content',
                key2id_dict = {},
                use_jig_feedback_cnt_limit = 2,
                ret_words=  10,
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

            # already_select_key_set表示的是 已经选的key set， D表示的是已经选的文章，文章的格式是{}这种而不是IRSys的
            already_select_key_set = set()
            D = []
            # already_cover_topic_dict
            # already_cover_topic_dict，格式 key:subtopic_id，
            # v: dict形式， key是相关度， v [这个subtopic下已经有的文章个数, [passage_text], 筛选出来的词的list, ]
            already_cover_topic_dict = {}

            logging.info("preprocess data...")
            query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)
            print "===> !!!! query_word_list:", query_word_list
            for _ in query_word_list:
                if not idf_dict.has_key(_):
                    print "!!!!==> idf_dict not has key:", _

            docs_list = irsys.retrieve_docs([topic], query_field=data_field, with_query_field=False)[0:candidate_doc_cnt]
            docs_keys = get_doc_keys_from_doc_list(docs_list)
            # print docs_list[0]
            print "CHECK docs_list, docs_keys cnt:", len(docs_list), len(docs_keys)
            corpus = get_corpus_by_keys(data_dir, key2id_dict, docs_keys, if_stem=if_stem, field=data_field)
            # print "CHECK corpus[0]:", corpus[0]
            docs_list = append_docs_to_doc_list(docs_list, docs_keys, corpus, field=data_field, if_filter_null=True)

            logging.info("cal dcs...")
            dc_dict = cal_dc_dicts(docs_list)

            google_subquerys = suggestor.get_subquery_by_topic_id(tid, if_related=False)[0:use_subquery_cnt]
            google_subquerys = clean_subquery_list(google_subquerys, idf_dict, if_stem=if_stem, query_words=query_word_list)

            print "===> google_subquerys:", google_subquerys

            file_ptr = 0
            for i in range(tot_itr_times):
                print "itr:", i, " tid:", tid

                if i == 0:
                    if_use_jig_feedback = False
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


                if if_use_jig_feedback:
                    print "USE JIG PASSAGE TEXT AS subquery, itr:", i
                    # TODO:这里要试试是不是要做筛选词处理，另外要考虑passage_text是不是已经用过
                    subqueries = passage_text_to_subqueries(already_cover_topic_dict)
                    subqueries = clean_subquery_list(subqueries, idf_dict, if_stem=if_stem, query_words=query_word_list)
                    subqueries = cut_off_jig_feedback( subqueries, idf_dict , ret_words)
                    subqueries_statics[tid][1] += 1
                else:
                    print "USE Suggested query as subquery, itr:", i
                    subqueries = google_subquerys
                    subqueries_statics[tid][0] += 1
                print "if_use_jig_feedback:", if_use_jig_feedback
                print "USE SUBQUERIES:", subqueries

                this_itr_select_docs = []
                if  not if_use_jig_feedback and len(subqueries) == 0 :
                    if len(subqueries) == 0:
                        print "======@@@@@@@@@@@@> subquery cnt is zero, tid, topic:", tid, topic
                    # print docs_list[0]
                    while len(this_itr_select_docs) < 5  and file_ptr < len(docs_list):
                        if docs_list[file_ptr][1][2]['key'] in already_select_key_set:
                            continue
                        this_itr_select_docs.append( docs_list[file_ptr] )
                        already_select_key_set.add( docs_list[file_ptr][1][2]['key'] )
                        #TODO CHECK:D
                        # D.append( docs_list[file_ptr][1][2] )
                        file_ptr += 1

                    # jig_format_docs = irsys.items2jigdocs(docs_list)[i * every_itr_doc_cnt:i * every_itr_doc_cnt + every_itr_doc_cnt]
                    # print "already_select_key_set:", already_select_key_set
                    jig_format_docs = irsys.items2jigdocs(this_itr_select_docs)

                    iresult = jig.run_itr(jig_format_docs, topic_id=tid)
                    print "i itr:", i
                    if iresult is not None:
                        for _ in iresult:
                            print _
                    update_state(already_cover_topic_dict, iresult)
                    continue
                else:

                    #use xQuAD to select best docs
                    R_left = get_R_left(docs_list, already_select_key_set)
                    this_itr_select_docs = []

                    for ixquad_selected in range(every_itr_doc_cnt):
                        print "==== [INFO] R_left cnt:", len(R_left)
                        ranked_docs = xquad.select_doc_u_cos(query_word_list, R_left, D, subqueries, dc_dicts=dc_dict,
                                              ret_rel_div_score=True)
                        ptr_ = 0
                        while ranked_docs[ptr_][0][KEY] in already_select_key_set:
                            ptr_ += 1
                            continue
                        d = ranked_docs[ptr_] #这个d的格式是[doc{}, xquad score, rel_score, div_score格式]
                        if d[0][KEY] in already_select_key_set:
                            print "############!!!!!!!!!ERROR >>>>>>>>>>>> SELECT DUP:", d[KEY]
                        # if i == 0:
                        print "-----CHECK SCORE SELECTED, [ xquad score, rel_score, div_score格式]->>>:", d[1:], d[0]
                        this_itr_select_docs.append( d )
                        D.append(d[0])
                        D[-1][SCORE] = d[1]
                        already_select_key_set.add(d[0][KEY])
                        R_left.remove(d[0])
                        print "len R_left, D, this_itr_select_docs, already_select_keys:",len(R_left), len(D), len(this_itr_select_docs), len(already_select_key_set)


                    # this_itr_select_docs = ranked_docs[0:every_itr_doc_cnt]

                    # for idx_,_ in enumerate(ranked_docs):
                    #     if _[0][KEY] in already_select_key_set:continue
                    #     this_itr_select_docs.append(_)
                    #     if len(this_itr_select_docs) >= 5:break


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
                print "[ERROR]  FUCK, tid, itr:", tid, i
                exit(-1)

            jig.judge()



    for tid, v in subqueries_statics.items():
        print "tid:", tid, "suggested, jig feedback:", v


'''
使用jig的passage text作为返回

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

    solrs = get_all_ebola_solrs()
    w = [3,1,1,1,1]

    # solrs = [
    #     SolrClient(solr_url=FULL_SOLR_URL),  # LMD, FULL
    #     # SolrClient(solr_url=SOLR_FULL_BM25_URL),
    #     # SolrClient(solr_url=SOLR_FULL_Classic_URL),
    #     # SolrClient(solr_url=SOLR_FULL_IBS_URL),
    #     # SolrClient(solr_url=SOLR_FULL_LMJM_URL),
    #     # SolrClient(solr_url=SOLR_FULL_DFR_G_L_H2)
    # ]
    #
    # w = [1]

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
    #     ('DD16-25', "Emory University's role in Ebola treatment"),
    #     ('DD16-26', 'Effects of African Culture'),
    #     ('DD16-27', 'kaci hickox'),
    # ]

    xQuAD_clean_use_local_data_without_feedback(topics=EBOLA_TOPICS,
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
                                                data_dir=EBOLA_FULL_NOT_CLEAN,
                                                data_field='content',
                                                key2id_dict=key2id_dict,
                                                use_jig_feedback_cnt_limit=1,
                                                )


'''
test 2
xQuAD_clean_use_local_data_without_feedback_div_from1
第一轮用google
然后都是jig返回，如果jig没有返回，还是继续用google
'''
def test_2():
    logging.info("loading key2id dict ebola")
    key2id_dict = json.load(codecs.open(FULL_KEY2ID))

    print "id of key[ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866]:", key2id_dict[
        'ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866']

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

    solrs = get_all_ebola_solrs()
    w = [3,1,1,1,1,1]
    # w = [1]
    #
    # solrs = [
    #     SolrClient(solr_url=FULL_SOLR_URL),  # LMD, FULL
    #     # SolrClient(solr_url=SOLR_FULL_BM25_URL),
    #     # SolrClient(solr_url=SOLR_FULL_Classic_URL),
    #     # SolrClient(solr_url=SOLR_FULL_IBS_URL),
    #     # SolrClient(solr_url=SOLR_FULL_LMJM_URL),
    #     # SolrClient(solr_url=SOLR_FULL_DFR_G_L_H2)
    # ]

    EBOLA_TOPICS = [
        ('DD16-25', "Emory University's role in Ebola treatment"),
        ('DD16-26', 'Effects of African Culture'),
        ('DD16-27', 'kaci hickox'),
    ]

    irsys = IRSys(solrs, w)
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    jig = JigClient_OLD(tot_itr_times=10, base_jig_dir=EBOLA_POLAR_JIG_DIR)
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
    xQuAD_clean_use_local_data_without_feedback_div_from1(topics=EBOLA_TOPICS,
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
                                                data_dir=EBOLA_FULL_NOT_CLEAN,
                                                data_field='content',
                                                key2id_dict=key2id_dict,
                                                use_jig_feedback_cnt_limit=1,
                                                )


'''
test_3
对返回的文档去重
'''

#====
'''
test_1_nyt
'''

class NytKey2Id():
    def __init__(self):
        pass
    def __getitem__(self, item):
        return item

def test_1_nyt():
    logging.info("loading key2id dict ebola")
    # key2id_dict = json.load(codecs.open(FULL_KEY2ID))
    key2id_dict = NytKey2Id()
    tot_itr_times = 10
    candidate_doc_cnt = 50

    print "id of key[ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866]:", key2id_dict['ebola-2d3fc9d3f24727460c25b5ff408a27cb82c53398a2543bffd740daf3a0d2f866']

    logging.info("load nyt stem idf dict...")
    # idf_dict = json.load(codecs.open(STEM_IDF_DICT_EBOLA, 'r', 'utf-8'))
    idf_dict = json.load(codecs.open(nyt_idf_idf_dic_stem, 'r', 'utf-8'))
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

    solrs = get_all_nyt_seg_solrs()
    w = [1,1,1,1,1]
    irsys = IRSys(solrs, w)
    suggestor = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    jig = JigClient(tot_itr_times=tot_itr_times, base_jig_dir=EBOLA_NYT_JIG_DIR)
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

    NYT_TOPICS = [
        # ('dd17-4', 'Origins Tribeca Film Festival'),
        ('dd17-46', 'PGP')
    ]

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
                                                xquad_lmd=0.6,
                                                idf_dict=idf_dict,
                                                jig=jig,
                                                irsys=irsys,
                                                data_dir=NYT_SEG_DATA_DIR,
                                                data_field='content_full_text',
                                                key2id_dict=key2id_dict,
                                                use_jig_feedback_cnt_limit=1,
                                                )

if __name__ == '__main__':
    '''
    xQuAD_clean_use_local_data_without_feedback_div_from1
    这个不好，只用LMD, 在旧的jig all,0.1893941285,0.1735672996

    xQuAD_clean_use_local_data_without_feedback
    旧的jig 只用LMD，/home/zhangwm/Software/ebola_pola_jig/trec-dd-jig/110003108.txt,all,0.1898315263,0.1921167919
    '''
    # test_2()
    # test_1()
    test_1_nyt()

__END__ = True