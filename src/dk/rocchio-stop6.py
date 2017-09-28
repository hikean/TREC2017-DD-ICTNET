import json
import codecs
import sys
import jieba
import logging

#logging.basicConfig(level=logging.ERROR)

from os.path import exists, isfile, isdir
from gensim import corpora, models
from sklearn import lda

sys.path.append('../utils')

from JigClient import JigClient
from es_client import ElasticClient

from basic_init import *

from src.data_preprocess.doc_preprocess import *
from src.utils.SolrClient import SolrClient
from src.utils.Document import *
from src.utils.JigClient import *

from nltk.stem.porter import PorterStemmer

from datasketch import MinHash, MinHashLSH

lsh = MinHashLSH(threshold=0.90, num_perm=128)

list_doc_s = []
list_doc_q = []
#dict_key_id = json.load(codecs.open("data/key2id.json","r") )

lama = 0.8
lamb = 0.00
n_topic = int(sys.argv[3])

english_punctuations = set(',-.:;?()[]&!*@#$%|"\'+={}`~_<>^ \n\t')
porter_stemmer = PorterStemmer()

stopword = [line.strip() for line in codecs.open('data/stopwords.txt',encoding='UTF-8').readlines()]
corp = []
get_id = []

idf_dictionary = json.load(codecs.open("data/nyt_withoutstem_idf.json","r") )

list_not_in_dictionary = set([])

def judge_if_untopic_doc(in_path):
    
    js = json.load(codecs.open(in_path, "r") )
    line = js["content_full_text"]
    
    seg_list = basic_preprocess(line,"utf8",True,True)
    
    #seg_list = jieba.cut(line, cut_all = False)
    #seg_list = stemmer_by_porter(seg_list)
    
    no_list = []
    for word in seg_list:
        if (word not in stopword) and (len(word)>1):
            no_list.append(word)
            
    mh = MinHash(num_perm = 128)
    for word in no_list:
        mh.update(word.encode('utf8'))
        
    result = lsh.query(mh)
    
    if len(result) > 0:
        return True
    else:
        return False
    
def add_untopic_doc(in_path , file_id):
    js = json.load(codecs.open(in_path, "r") )
    line = js["content_full_text"]
    
    seg_list = basic_preprocess(line,"utf8",True,True)
    #seg_list = jieba.cut(line, cut_all = False)
    #seg_list = stemmer_by_porter(seg_list)
    
    no_list = []
    for word in seg_list:
        if (word not in stopword) and (len(word)>1):
            no_list.append(word)
            
    mh = MinHash(num_perm = 128)
    for word in no_list:
        mh.update(word.encode('utf8'))
        
    lsh.insert(file_id, mh)
    
def stemmer_by_porter(wordlist):
    global porter_stemmer
    # for w in word_list:
    # return [porter_stemmer.stem(w) for w in wordlist]
    ret = []
    for w in wordlist:
        try:
            ret.append(porter_stemmer.stem(w))
        except Exception as e:
            # print "ERROR STEM:", w
            pass
            # logging.exception("[!] porter_stemmer exception: %s", e)
    if len(ret) == 0 and len(wordlist) != 0:
        logging.warning(
            "empty stemming result, wordlist sample: %s", wordlist[:10])
    return ret

def cal_dict_s_topic(list_s , in_dir):
    dict_s_topic = {str(key) : 0.0 for key in range(n_topic)}
        
    js = json.load(codecs.open(in_dir, "r") )
    for file_id in list_s:
        sum = 0.0
        for topic_pro in js[file_id]:
            sum += float(topic_pro[1]) 
        for topic_pro in js[file_id]:
            dict_s_topic[str(topic_pro[0])] += float(topic_pro[1]) / sum
        
    return dict_s_topic

def cal_dict_u_topic(in_dir):
    dict_u_topic = {str(key) : 0.0 for key in range(n_topic)}
    
    js = json.load(codecs.open(in_dir, "r") )
    for file_id in js:
        for topic_pro in js[file_id]:
            dict_u_topic[str(topic_pro[0])] += float(topic_pro[1])
        
    return dict_u_topic

def get_dict_fileid_topic(in_dir):
    
    js = json.load(codecs.open(in_dir, "r") )
    
    dict_ans = {}
    
    for file_id in js:
        dict_file = {}
        for topic_pro in js[file_id]:
            dict_file[str(topic_pro[0])] = topic_pro[1]
        dict_ans[file_id] = dict_file
    
    return dict_ans

def get_dict_keyword(str_text , cnt_key_word):
    list_word = jieba.cut( str_text , cut_all = False)
    cnt_word = {}
    cnt_word_in_doc = 0.0
    for word in list_word:
        if word not in idf_dictionary:
            list_not_in_dictionary.add(word)
            continue
        if (word not in stopword) and (len(word) > 1):
            cnt_word_in_doc += 1.0
            if word not in cnt_word:
                cnt_word[word] = 1.0
            else:
                cnt_word[word] += 1.0
    
    for word in cnt_word:
        cnt_word[word] = cnt_word[word] / cnt_word_in_doc * idf_dictionary[word]
    
    list_cnt_word = sorted(cnt_word.items() , key = lambda asd:asd[1] , reverse = True)
    #print("list_cnt_word:" , list_cnt_word)
    
    dict_key_word = {}
    for item in list_cnt_word[0:cnt_key_word]:
        dict_key_word[item[0]] = item[1]
        
    return dict_key_word 

def interact_with_jig(jig, docs, in_dir , interact_times , dict_subtopic_cnt , list_doc_untopic , int_untopic):
    list_re_doc_id = []
    list_unre_doc_id = []
    dict_keyword_score = {}
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5])
        st_ptr += 5
        #print ("itr:", i) #, " rslt:", rslt
        for _ in rslt:
            print ("rslt:", _)
            if _["on_topic"] == '0':
                #list_unre_doc_id.append( _["doc_id"] )
                add_untopic_doc( in_dir.format( _["doc_id"] ) , _["doc_id"] )
                list_doc_untopic.append(  _["doc_id"] )
                int_untopic += 1
                continue
            
            flag_choose = 0
            for dict_subtopics in _["subtopics"]:
                subtopic_id = dict_subtopics["subtopic_id"]
                if (subtopic_id not in dict_subtopic_cnt) or (dict_subtopic_cnt[subtopic_id] < 8):
                    flag_choose = 1
                    if subtopic_id not in dict_subtopic_cnt:
                        dict_subtopic_cnt[subtopic_id] = 0
                    dict_subtopic_cnt[subtopic_id] += dict_subtopics["rating"]
                    dict_keyword = get_dict_keyword(dict_subtopics["passage_text"] , 3)
                    for word in dict_keyword:
                        if word not in dict_keyword_score:
                            dict_keyword_score[word] = 0.0
                        dict_keyword_score[word] += dict_keyword[word]
            
            if flag_choose == 1:
                list_doc_s.append( _["doc_id"] )
                list_re_doc_id.append( _["doc_id"]  )
                
            else:
                list_unre_doc_id.append( _["doc_id"] )
                pass
                
    return list_re_doc_id , list_unre_doc_id , dict_keyword_score , dict_subtopic_cnt, list_doc_untopic , int_untopic
            
def retrieval_top_k_doc_full(query, solr=SolrClient(), k=RET_DOC_CNT, query_range=[ "content_title", "content_p", "content_h1", "content_h2", "content_h3", "content_h4", "content_h5"]):
    fl = 'key,doc_id'

    irdocs = []

    for v in query_range:
        logging.info("ir: " + v)
        docs = solr.query_fields(query, v, fl, rows=k)
        irdocs += docs
    #print "tot ir doc cnt:", len(irdocs)

    # print docs

    return irdocs2tuple_full(irdocs)[0:k]

def read_json_file(in_path, id):
    global corp
    
    get_id.append(id)
    
    js = json.load(codecs.open(in_path, "r") )
    line = js["content_full_text"]
    
    seg_list = basic_preprocess(line,"utf8",True,True)
    #seg_list = jieba.cut(line, cut_all = False)
    #seg_list = stemmer_by_porter(seg_list)
    
    no_list = []
    for word in seg_list:
        if (word not in stopword) and (len(word)>1):
            no_list.append(word)
            
    corp.append(no_list)

def get_lda(out_dir,topic_name):
    global corp
    
    dictionary = corpora.Dictionary(corp)
    corpus = [dictionary.doc2bow(text) for text in corp]
    
    lda = models.LdaModel(corpus, id2word=dictionary, num_topics=n_topic , random_state= 1 )
    lda.save(out_dir + "{}-{}-{}-{}-{}-{}-{}-lda_model-single-nyt.model".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],topic_name) )
    
    ldaOut = lda.print_topics(n_topic)
    file_ldaOut = codecs.open(out_dir + "{}-{}-{}-{}-{}-{}-{}-lda_topics-single-nyt.txt".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],topic_name), "w", "utf-8")
    file_ldaOut.write(str(ldaOut))
    
    file_id_lda = codecs.open(out_dir + "{}-{}-{}-{}-{}-{}-{}-fileid_lda-single-nyt.txt".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],topic_name), "w", "utf-8")
    corpus_lda_doc = lda[corpus]
    
    index_id = -1
    dict_id_lda = {}
    for doc in corpus_lda_doc:
        index_id += 1
        file_id = get_id[index_id]
        dict_id_lda[file_id] = doc
    
    file_id_lda.write(json.dumps(dict_id_lda))

def get_dict_key_word(in_dir , doc_id , cnt_key_word):
    
    js = json.load( codecs.open( in_dir.format(doc_id) , "r") )

    list_word = jieba.cut( js["content_full_text"] , cut_all = False)
    #list_word = stemmer_by_porter(list_word)
    
    cnt_word = {}
    cnt_word_in_doc = 0.0
    for word in list_word:
        if (word not in stopword) and (len(word) > 1):
            if word not in idf_dictionary:
                list_not_in_dictionary.add(word)
                continue
            cnt_word_in_doc += 1.0
            if word not in cnt_word:
                cnt_word[word] = 1.0
            else:
                cnt_word[word] += 1.0
    
    for word in cnt_word:
        cnt_word[word] = cnt_word[word] / cnt_word_in_doc * idf_dictionary[word]
    
    list_cnt_word = sorted(cnt_word.items() , key = lambda asd:asd[1] , reverse = True)
    #print("list_cnt_word:" , list_cnt_word)
    
    dict_key_word = {}
    for item in list_cnt_word[0:cnt_key_word]:
        dict_key_word[item[0]] = item[1]
        
    return dict_key_word 
    
def rocchio_get_new_query(str_query , list_re_doc_id , list_unre_doc_id , in_dir , dict_keywords):
    
    dict_query = dict_keywords
    list_query = str_query.split(",")
    for word_tfidf in list_query:
        sub = word_tfidf.split("^")
        if sub[0] not in dict_query:
            dict_query[sub[0]] = 0.0
        dict_query[sub[0]] += float(sub[1])
    
    """     
    for word in list_query:
        if (word not in stopword) and (len(word) > 1):
            if word not in dict_query:
                dict_query[word] = 1.0
            else:
                dict_query[word] += 1.0
    """         
    
    for doc_id in list_re_doc_id:
        dict_key_word = get_dict_key_word(in_dir, doc_id, 10)
        for word in dict_key_word:
            if word not in dict_query:
                dict_query[word] = dict_key_word[word]
            else:
                dict_query[word] += dict_key_word[word]
    
    """
    for doc_id in list_unre_doc_id:
        dict_key_word = get_dict_key_word(in_dir, doc_id, 10)
        for word in dict_key_word:
            if word not in dict_query:
                dict_query[word] = -dict_key_word[word]
            else:
                dict_query[word] -= dict_key_word[word]
    """
    str_new_query = ""
    for word in dict_query:
        str_new_query += word + "^" + str(dict_query[word]) + ","
    
    str_new_query = str_new_query[:-1]
    return str_new_query

def init_query(str_query):
    list_query = jieba.cut(str_query, cut_all = False)
    word_set = set([])
    for word in list_query:
        if (word not in stopword) and (len(word) > 1):
            word_set.add(word)
    
    new_query = ""
    for word in word_set:
        new_query += word + "^" + "1.0," 
    
    new_query = new_query[:-1]
    return new_query


if __name__ == '__main__':
    
    global list_doc_q,list_doc_s,lama,lamb,corp,get_id,lsh
    """
    
    global stopword
    stopword = [line.strip() for line in codecs.open('data/stopwords.txt',encoding='UTF-8').readlines()];
    
    client = ElasticClient(doc_type="ebola", return_size=1000, index="trec3")
    dictionary = client.search_ebola(
        keyword="Blut-Therapie soll gegen Ebola helfen",
        fields=["title", "content"])
    
    """
    
    
    NYT_TOPICS = [('dd17-1', 'Return of Klimt paintings to Maria Altmann'), 
                  ('dd17-2', 'Who Outed Valerie Plame?'), 
                  ('dd17-3', "First Women's Bobsleigh Debut 2002 Olympics"), 
                  ('dd17-4', 'Origins Tribeca Film Festival'), 
                  ('dd17-5', "Benazir Bhutto's legal problems"), 
                  ('dd17-6', 'Dwarf Planets'), 
                  ('dd17-7', 'Warsaw Pact Dissolves'), 
                  ('dd17-8', 'Concorde Crash'), 
                  ('dd17-9', 'Grenada-Cuba connections'), 
                  ('dd17-10', 'Leaning tower of Pisa Repairs'), 
                  ('dd17-11', 'Zebra mussel Hudson River'), ('dd17-12', 'Dental implants'), ('dd17-13', 'Albania pyramid scheme VEFA'), ('dd17-14', 'Montserrat eruption effects'), ('dd17-15', 'arik afek yair klein link'), ('dd17-16', 'Eggs actually are good for you'), ('dd17-17', 'Nancy Pelosi election as Speaker of the House'), ('dd17-18', 'Celebration of 50th Anniversary of Golden Gate Bridge'), ('dd17-19', 'Antioxidant food supplements'), ('dd17-20', 'Elizabeth Edwards Cancer'), ('dd17-21', 'Mega Borg Oil Spill'), ('dd17-22', 'Playstation 2 Console Sales and Prices'), ('dd17-23', 'USAF 1st Lt. Flinn discharged'), ('dd17-24', 'Melissa virus effect and monetary costs'), ('dd17-25', 'Last Checker Taxi Cab in NYC Auctioned'), ('dd17-26', 'New Scottish Parliament building'), ('dd17-27', 'Doping for professional sports'), ('dd17-28', 'Russian Organized Crime Involvement in Skating Scandal'), ('dd17-29', 'Chefs at Michelin 3- star Restaurants'), ('dd17-30', 'Nicotine addiction'), ('dd17-31', 'Implantable Heart Pump'), ('dd17-32', 'Million Man March on Washington'), ('dd17-33', 'refugees on nauru'), ('dd17-34', 'Rudolf Hess dies'), ('dd17-35', 'Bedbug infestation rising'), ('dd17-36', 'Global Warming Effect on NYC Region'), ('dd17-37', 'Gander Community Response After 9/11'), ('dd17-38', 'Iceland financial problems'), ('dd17-39', 'Munch Scream Recovered'), ('dd17-40', 'Church of England first female priests ordained'), ('dd17-41', 'Lion King Film'), ('dd17-42', 'Asian tiger mosquito'), ('dd17-43', 'Harry Connick Jr. on Broadway'), ('dd17-44', 'Whitney Museum Expansion to Meatpacking District'), ('dd17-45', 'Exhibitions of George Nakashima Works'), ('dd17-46', 'PGP'), ('dd17-47', 'Freon-12'), ('dd17-48', 'defense, precautions against modern ship piracy'), ('dd17-49', 'kangaroo survival'), ('dd17-50', 'Shrinking ice sheet in Greenland'), ('dd17-51', "Hurricane Katrina's Effects"), ('dd17-52', 'Solar power for U.S. homes'), ('dd17-53', "Alzheimer's and beta amyloid; detection, treatment?"), ('dd17-54', 'Indoor air pollution'), ('dd17-55', 'North Korea says it has nukes'), ('dd17-56', 'Abortion pill in the United States'), ('dd17-57', 'Libyan connection to Muslim coup in Trinidad Tobago'), ('dd17-58', 'cashew growing'), ('dd17-59', "Colonel Denard's mercenary activities"), ('dd17-60', 'Tupac Amaru and Shining Path, relationship, differences, similarities')]

    
    tot_itr_times = int(sys.argv[4])
    #NYT_JIG_DIR = "/home/zhangwm/Software/dk_jig1/jig/trec-dd-jig/"
    jig = JigClient("",tot_itr_times=tot_itr_times,base_jig_dir="/home/zhangwm/Software/dk_jig6/jig/trec-dd-jig/")
    
    for ebola_query in NYT_TOPICS[0:int(sys.argv[6])]:
        dict_subtopic_cnt = {}
        lsh = MinHashLSH(threshold=0.90, num_perm=128)
        #lsh.__init__()
        list_doc_s = []
        
        int_untopic = 0
        int_sumtopic = 0
        list_doc_untopic =[]
        
        topic_query = [ebola_query[1]]
        
        #print("topic_query: ",topic_query)
        #topic_query = [','.join(topic_query[0].split())]
        topic_name = ebola_query[0]
        
        #if (topic_name == "dd17-46") and (sys.argv[4] > 6):
        #    continue
        
        jig.topic_id = topic_name
        
        #FULL_SOLR_URL = "http://172.22.0.11:8983/solr/ebola_extract/select?"
        
        solr = SolrClient(SOLR_SEG_nyt_LMD_URL)
        
        in_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
        in_dir += "/datas/nonested/{}.json"
        print("in_dir: ",in_dir)
        
        for tt in range( int(sys.argv[4]) ):
            
            corp = []
            get_id = []
            list_doc_q = []
            
            print("topic_query: ",topic_query)
            docs = retrieval_top_k_doc_full(topic_query, solr, int(sys.argv[5]), query_range=['content_full_text'])
        
            print("docs: ",docs)
            
            dict_fileid_score = {}
            
            int_cnt_doc_solr = int(sys.argv[5])
            
            int_cnt_list_q = 0
            for dict_doc in docs:
                if dict_doc[1] not in list_doc_s:
                    #list_doc_solr.append( dict_doc[1] )
                    if dict_doc[1] in list_doc_untopic:
                        continue
                    int_cnt_list_q += 1
                    if int_cnt_list_q <= 30:
                        list_doc_q.append( dict_doc[1] )
                    dict_fileid_score[ dict_doc[1] ] = float(dict_doc[2] )  
                    read_json_file( in_dir.format( dict_doc[1] ), dict_doc[1] )
            
            for doc_id in list_doc_s:
                read_json_file( in_dir.format( doc_id ), doc_id )
            
            out_dir = "data/lda/"
            #out_dir = "data/test_lda/"
            get_lda(out_dir,topic_name )
            
            in_dir_fileid_lda = "data/lda/{}-{}-{}-{}-{}-{}-{}-fileid_lda-single-nyt.txt".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],topic_name)
            
            dict_u_topic = cal_dict_u_topic(in_dir_fileid_lda)
            
            #print("dict_u_topic: ",dict_u_topic)
            
            dict_fileid_topic = get_dict_fileid_topic(in_dir_fileid_lda)
            
            if tt <= 1:
                lama = 0.9
                lamb = 0.0
            elif tt == 2:
                lama = float(sys.argv[1])
                lamb = float(sys.argv[2])
            else:
                lamb += float(sys.argv[7])
                lamb = min(lamb,1.0)
                
            docs_result_id = []
            
            dict_s_topic = cal_dict_s_topic(list_doc_s , in_dir_fileid_lda)
            
            dict_fileid_final_score = {}
            
            
            #print("dict_s_topic: ",dict_s_topic)
                
            max_topic_value = -10.0
            max_topic_id = "0"
            quotient = {}
            
            for topic_id in range(n_topic):
                key_topic_id = str(topic_id)
                quotient[key_topic_id] = dict_u_topic[key_topic_id] / (1.0 + 2 * dict_s_topic[key_topic_id])
                    
                if quotient[key_topic_id] > max_topic_value :
                    max_topic_value = quotient[key_topic_id]
                    max_topic_id = key_topic_id
                    
            #list_quotient = sorted(quotient.items() , key = lambda asd:asd[1] , reverse = True)

            #print("list_doc_q: ",list_doc_q)
            
            dict_file_id_score = {}
            for file_id in list_doc_q:
                    
                if file_id not in dict_fileid_topic:
                    topic_score = 0.0
                    solr_score = dict_fileid_score[file_id]
                    file_value = lamb * topic_score + (1.0-lamb) * solr_score
                else:
                    topic_score = 0.0
                    for topic_id in range(n_topic):
                        key_topic_id = str(topic_id)
                        if key_topic_id == max_topic_id :
                            topic_score += lama * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                        else:
                            topic_score += (1.0-lama) * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                        """
                        topic_cnt = 0
                        main_topic = 3
                        for item_topic_id_quo in list_quotient:
                            topic_id = item_topic_id_quo[0]
                            topic_cnt += 1
                            key_topic_id = str(topic_id)
                            if topic_cnt <= main_topic :
                                file_value += lama * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                            else:
                                file_value += (1.0-lama) * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                        """        
                        #print("topic_score: ",file_value )
                        #print("solr_score: ",dict_fileid_score[file_id])
                        #add_score
                    solr_score = dict_fileid_score[file_id]
                    file_value = lamb * topic_score + (1.0-lamb) * solr_score
                    
                    #print("file_id: ",file_id)
                    #print("file_value: ",file_value)
                dict_file_id_score[file_id] = file_value 
                
            list_score = sorted(dict_file_id_score.items() , key = lambda asd:asd[1] , reverse = True)    
            
            docs_result = []
            
            int_choose = 0
            for tuple in list_score:
                if judge_if_untopic_doc( in_dir.format(tuple[0]) ) == False:
                    docs_result_id.append( tuple[0] )
                    dict_doc_copy = (0 , tuple[0] , tuple[1])
                    docs_result.append(dict_doc_copy)
                    int_choose += 1
                else:
                    list_doc_untopic.append( tuple[0] )
                list_doc_q.remove( tuple[0] )
                if int_choose == 5:
                    break
            
            print("docs_result: ",docs_result)
            
            int_untopic = 0
            list_re_doc_id , list_unre_doc_id , dict_keyword , dict_subtopic_cnt , list_doc_untopic , int_untopic = interact_with_jig(jig, docs_result, in_dir, 1, dict_subtopic_cnt , list_doc_untopic , int_untopic)
            if int_untopic == 0:
                int_sumtopic += int_untopic
            else:
                int_sumtopic = 0
            if int_sumtopic >= int(sys.argv[8]) and (len(list_doc_s) > 0):
                break
            
            if tt == 0: 
                topic_query = [init_query(topic_query[0])]  
            topic_query = [rocchio_get_new_query(topic_query[0] , list_re_doc_id, list_unre_doc_id, in_dir, dict_keyword)]
            
        jig.judge()    
            #print("ok")
    jig.judge()
    print("list_not_in_dictionary: ",list_not_in_dictionary)