# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/18 下午11:38
# @version: 1.0


'''

数据方面，词干化、大写转小写等都做...

基本idea 使用LDA的隐主题替代subquery
需要调试的点
1、LDA HDP
2、可以考虑扩展层次了...
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
from xQuAD_solution import cal_dc_dicts, get_R_left, preproces_docs_list

def train_lda(corpus, n_topics, key_list=[]):
    '''
    :param corpus: 文章是wordlist的格式，然后corpus是文章的格式
    :param n_topics: 隐话题数目
    :param key_list: 表示顺序的corpus的key
    :return: 返回 dict key:key, v:lda feature
    '''
    logging.info("training LDA...%d" % len(corpus))
    dictionary = corpora.Dictionary(corpus)
    corpus2bow = [ dictionary.doc2bow(text) for text in corpus ]
    lda = LdaModel(corpus2bow, id2word=dictionary, num_topics=n_topics, iterations=150)
    ldaOut = lda.print_topics(n_topics)

    print "ladOut:", ldaOut

    key_lda_dict = {}
    for i,k in enumerate(key_list):
        key_lda_dict[k] = lda[ corpus2bow[i] ]

    return key_lda_dict

def mk_file_name(data_dir, id):
    return os.path.join( data_dir, str(id) + '.json' )

def get_doc_keys_from_doc_list(docs_list):
    ret = []
    for d in docs_list:
        ret.append( d[1][2][KEY] )
    return ret

def get_corpus_by_keys(dir_path, key2id_dict={}, keys=[], field='content', if_stem=True):
    '''
    :param dir_path: 数据存储在哪里
    :param key2id_dict: 根据key找到id 从而找到文件所在
    :param keys: 对应需要找到的文档内容
    :param field: 需要找的文章字段
    :return: 每个文档一行，并且是处理过的word_list，包括分词，停用词，stemmer
    '''
    raw_corpus = []
    logging.info("reading datas...")
    for key in keys:
        filename = mk_file_name(dir_path, key2id_dict[key])
        line = codecs.open(filename, 'r', 'utf-8').readline().strip()
        if line[0] == '[': line = line[1:]
        if line[-1] == ']': line = line[0:len(line)-1]
        content = json.loads(line)[field]
        new_content = basic_preprocess(content, if_stem=if_stem)
        if len(content) != 0 and len(new_content) == 0:
            print "!!!!!!+++>>> ERROR, get_corpus_by_keys, content zero, doc_id, original content:", filename, content
        raw_corpus.append( new_content )
    return raw_corpus

def get_top_docs(doc_list, selected_keys=set(), ret_cnt=None):
    ret = []
    if ret_cnt is None:
        ret_cnt = len(doc_list) - len(selected_keys)
    cnt = 0
    for d in doc_list:
        if d[1][2][KEY] not in selected_keys:
            ret.append(d)
            cnt += 1
            selected_keys.add(d[1][2][KEY])
            if cnt >= ret_cnt:break
    return ret

def update_selected(already_selected_keys, selected_jig_docs):
    for d in selected_jig_docs:
        already_selected_keys.add(d[1])
    return already_selected_keys

def xQuAD_by_LDA_without_feedback(topics = EBOLA_TOPICS,
                 w = None,
                 if_stem=True,
                candidate_doc_cnt = 700,
                tot_itr_times = 2,
                every_itr_doc_cnt = 5,
                use_subquery_cnt = 5,
                xquad_lmd = 0.8,
                 key2id_dict = {},
                lda_ntopics = 5,
                data_dir = EBOLA_CLEAN_SEG_DATA_DIR,
                data_field = 'content_p',
                 ):
    logging.info("get all solrs...")
    solrs = get_all_ebola_solrs()
    print "solr cnt:", len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
        logging.info("search for topic %s %s" % (tid, topic))
        print "tot_itr_times:", tot_itr_times
        print "every_itr_doc_cnt:", every_itr_doc_cnt
        print "use_subquery_cnt:", use_subquery_cnt
        print "xquad_lmd:", xquad_lmd
        print "lda ntopics:", lda_ntopics
        print "candidate_doc_cnt:", candidate_doc_cnt

        already_select_key_set = set()

        logging.info("preprocess data...")
        query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)

        print "===> !!!! query_word_list:", query_word_list

        #这里面本身是排序过的
        docs_list = irsys.retrieve_docs([topic], with_query_field=False)[0:candidate_doc_cnt]

        docs_keys = get_doc_keys_from_doc_list(docs_list)
        R_left = dict(copy.deepcopy(docs_list))

        # corpus = get_corpus_by_keys(EBOLA_FULL_DATA_DIR, key2id_dict, docs_keys, if_stem=if_stem)
        corpus = get_corpus_by_keys(data_dir, key2id_dict, docs_keys, if_stem=if_stem, field=data_field)

        # print "CHECK corpus[0:3]:"
        # for _ in  corpus[0:1]:
        #     print _

        #Add query before train..
        docs_keys.append('query')
        corpus.append( query_word_list )

        key_lda_feat_dict = train_lda(corpus, lda_ntopics, docs_keys)
        print "check:", key_lda_feat_dict

        for k,v in key_lda_feat_dict.items():
            key_lda_feat_dict[k] = dict( key_lda_feat_dict[k] )

        logging.info("initing xQuAD_LDA...")
        xquad_lda = xQuAD_LDA(key_lda_feat_dict, lda_ntopics, lmd=xquad_lmd)

        for i in range(tot_itr_times):
            print "i itr:", i, " tid:", tid
            if i == 0:
                this_itr_docs = get_top_docs(docs_list, already_select_key_set, ret_cnt=5)
                jig_format_docs = irsys.items2jigdocs(this_itr_docs)
                jig.run_itr(jig_format_docs, tid)
                already_select_key_set = update_selected(already_select_key_set, jig_format_docs)
            else:
                this_itr_docs = []

                while len(this_itr_docs) < every_itr_doc_cnt:
                    # xquad_doc_list = xquad_lda.select_doc_u(R_left.items(), already_select_key_set, key_lda_feat_dict)
                    xquad_doc_list = xquad_lda.select_doc_u_log_weak_rel_score(R_left.items(), already_select_key_set, key_lda_feat_dict)
                    idx_ptr = 0
                    while xquad_doc_list[idx_ptr][0][KEY] in already_select_key_set:
                        idx_ptr += 1
                        continue
                    right_doc = xquad_doc_list[idx_ptr]
                    already_select_key_set.add( right_doc[0][KEY] )
                    R_left.pop(right_doc[0][KEY])
                    this_itr_docs.append( (0, right_doc[0][KEY], right_doc[1]) )

                    print "====>select doc, tot_score, solr_score, xquad_div_score:", right_doc
                irslt = jig.run_itr(this_itr_docs, tid)
                if irslt is not None:
                    for _ in irslt:
                        print _

        print "======== CHECK DUP:", len(already_select_key_set), tot_itr_times * 5
        if tot_itr_times * 5 != len(already_select_key_set):
            print "[ERROR]  FUCK, tid, itr:", tid, i
            exit(-1)

        jig.judge()



def xQuAD_by_LDA_without_feedback_ir_blending(topics = EBOLA_TOPICS,
                 w = None,
                 if_stem=True,
                candidate_doc_cnt = 700,
                tot_itr_times = 2,
                every_itr_doc_cnt = 5,
                use_subquery_cnt = 5,
                xquad_lmd = 0.8,
                 key2id_dict = {},
                lda_ntopics = 5,
                data_dir = EBOLA_CLEAN_SEG_DATA_DIR,
                data_field = 'content_p',
                 ):
    logging.info("get all solrs...")
    # solrs = get_all_ebola_solrs()
    solrs = [
        SolrClient(solr_url=FULL_SOLR_URL), #LMD, FULL
        SolrClient(solr_url=SOLR_FULL_BM25_URL),
        SolrClient(solr_url=SOLR_FULL_Classic_URL),
        SolrClient(solr_url=SOLR_FULL_IBS_URL),
        SolrClient(solr_url=SOLR_FULL_LMJM_URL),
        # SolrClient(solr_url=SOLR_FULL_DFR_G_L_H2)
    ]
    w = [3,1,1,1,1]
    print "solr cnt:", len(solrs)
    # w = [3, 1, 1, 1, 1] #提高1.5%
    irsys = IRSys(solrs, ws=w)

    jig = JigClient(tot_itr_times=tot_itr_times)

    for tid, topic in topics:
        logging.info("search for topic %s %s" % (tid, topic))
        print "tot_itr_times:", tot_itr_times
        print "every_itr_doc_cnt:", every_itr_doc_cnt
        print "use_subquery_cnt:", use_subquery_cnt
        print "xquad_lmd:", xquad_lmd
        print "lda ntopics:", lda_ntopics
        print "candidate_doc_cnt:", candidate_doc_cnt

        already_select_key_set = set()

        logging.info("preprocess data...")
        query_word_list = basic_preprocess_for_query(topic, if_lower=True, if_stem=if_stem)

        print "===> !!!! query_word_list:", query_word_list

        #这里面本身是排序过的
        docs_list = irsys.retrieve_docs([topic], with_query_field=False)[0:candidate_doc_cnt]

        docs_keys = get_doc_keys_from_doc_list(docs_list)
        R_left = dict(copy.deepcopy(docs_list))

        # corpus = get_corpus_by_keys(EBOLA_FULL_DATA_DIR, key2id_dict, docs_keys, if_stem=if_stem)
        corpus = get_corpus_by_keys(data_dir, key2id_dict, docs_keys, if_stem=if_stem, field=data_field)

        print "CHECK corpus[0:3]:"
        for _ in  corpus[0:1]:
            print _

        #Add query before train..
        docs_keys.append('query')
        corpus.append( query_word_list )

        key_lda_feat_dict = train_lda(corpus, lda_ntopics, docs_keys)
        print "check:", key_lda_feat_dict

        for k,v in key_lda_feat_dict.items():
            key_lda_feat_dict[k] = dict( key_lda_feat_dict[k] )

        logging.info("initing xQuAD_LDA...")
        xquad_lda = xQuAD_LDA(key_lda_feat_dict, lda_ntopics, lmd=xquad_lmd)

        for i in range(tot_itr_times):
            print "i itr:", i, " tid:", tid
            if i == 0:
                this_itr_docs = get_top_docs(docs_list, already_select_key_set, ret_cnt=5)
                jig_format_docs = irsys.items2jigdocs(this_itr_docs)
                jig.run_itr(jig_format_docs, tid)
                already_select_key_set = update_selected(already_select_key_set, jig_format_docs)
            else:
                this_itr_docs = []

                while len(this_itr_docs) < every_itr_doc_cnt:
                    # xquad_doc_list = xquad_lda.select_doc_u(R_left.items(), already_select_key_set, key_lda_feat_dict)
                    xquad_doc_list = xquad_lda.select_doc_u_log_weak_rel_score(R_left.items(), already_select_key_set, key_lda_feat_dict)
                    idx_ptr = 0
                    while xquad_doc_list[idx_ptr][0][KEY] in already_select_key_set:
                        idx_ptr += 1
                        continue
                    right_doc = xquad_doc_list[idx_ptr]
                    already_select_key_set.add( right_doc[0][KEY] )
                    R_left.pop(right_doc[0][KEY])
                    this_itr_docs.append( (0, right_doc[0][KEY], right_doc[1]) )

                    print "====>select doc, tot_score, solr_score, xquad_div_score:", right_doc
                irslt = jig.run_itr(this_itr_docs, tid)
                if irslt is not None:
                    for _ in irslt:
                        print _

        print "======== CHECK DUP:", len(already_select_key_set), tot_itr_times * 5
        if tot_itr_times * 5 != len(already_select_key_set):
            print "[ERROR]  FUCK, tid, itr:", tid, i
            exit(-1)

        jig.judge()

def test_1():
    key2id_dict = json.load( codecs.open( KEY2ID_FILE ) )
    xQuAD_by_LDA_without_feedback(topics=EBOLA_TOPICS,
                                  w=None,
                                  if_stem=True,
                                  candidate_doc_cnt=350,
                                  tot_itr_times=2,
                                  every_itr_doc_cnt=5,
                                  use_subquery_cnt=5,

                                  xquad_lmd=10,
                                  key2id_dict=key2id_dict,
                                  lda_ntopics=15,
                                  )

'''
是是干净的全文数据，而不是只有content_p
'''
def test_2():
    key2id_dict = json.load(codecs.open(FULL_KEY2ID))
    xQuAD_by_LDA_without_feedback(topics=EBOLA_TOPICS,
                                  w=None,
                                  if_stem=True,
                                  candidate_doc_cnt=350,
                                  tot_itr_times=2,
                                  every_itr_doc_cnt=5,
                                  use_subquery_cnt=5,

                                  xquad_lmd=10,
                                  key2id_dict=key2id_dict,
                                  lda_ntopics=13,
                                  data_dir=EBOLA_FULL_NOT_CLEAN,
                                  data_field='content'
                                  )



'''
混合的ebola 搜索引擎
'''
def test_3():
    key2id_dict = json.load(codecs.open(KEY2ID_FILE))
    xQuAD_by_LDA_without_feedback_ir_blending(topics=EBOLA_TOPICS,
                                  w=None,
                                  if_stem=True,
                                  candidate_doc_cnt=300,
                                  tot_itr_times=2,
                                  every_itr_doc_cnt=5,
                                  use_subquery_cnt=5,

                                  xquad_lmd=10,
                                  key2id_dict=key2id_dict,
                                  lda_ntopics=15,
                                  data_dir=EBOLA_CLEAN_FULL_DATA_DIR,
                                  data_field='content'
                                  )

if __name__ == '__main__':
    # test_1()
    # test_3()
    test_2()

__END__ = True