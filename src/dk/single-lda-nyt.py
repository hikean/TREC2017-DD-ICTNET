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

def interact_with_jig(jig, docs, in_dir , interact_times=10 , ):
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5])
        st_ptr += 5
        #print ("itr:", i) #, " rslt:", rslt
#         if rslt is not None:
        for _ in rslt:
            print ("rslt:", _)
            if _["on_topic"] == '0':
                
                add_untopic_doc( in_dir.format(_["doc_id"]) , _["doc_id"] )
                continue
            
            flag_choose = 0
            for dict_subtopics in _["subtopics"]:
                #if dict_subtopics["rating"] == "3" or dict_subtopics["rating"] == "4":
                flag_choose = 1
                break
            
            if flag_choose == 1:
                list_doc_s.append( _["doc_id"] )
                
                
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
    
    lda = models.LdaModel(corpus, id2word=dictionary, num_topics=n_topic)
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
    
    """
    file_word_lda = codecs.open(out_dir + "{}-{}-{}-{}-{}-{}-word_lda.txt".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],topic_name), "w", "utf-8")
    
    word_corp = []
    for word in dictionary:
        list_word = []
        list_word.append(dictionary[word])
        word_corp.append(list_word)
    
    word_corpus = [dictionary.doc2bow(text) for text in word_corp]
    corpus_lda_word = lda[word_corpus]
    dict_word_lda = {}
    for word,lda  in zip(dictionary, corpus_lda_word):
        dict_word_lda[dictionary[word]] = lda
    
    file_word_lda.write(json.dumps(dict_word_lda))
    """

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
    jig = JigClient("",tot_itr_times=tot_itr_times,base_jig_dir=NYT_JIG_DIR)
    
    for ebola_query in NYT_TOPICS[0:int(sys.argv[6])]:
        
        lsh = MinHashLSH(threshold=0.90, num_perm=128)
        #lsh.__init__()
        list_doc_s = []
        list_doc_q = []
        
        if ebola_query[1][-1] == "?":
            topic_query = [ebola_query[1][0:-1]]
        else:
            topic_query = [ebola_query[1]]
        
        #print("topic_query: ",topic_query)
        #topic_query = [','.join(topic_query[0].split())]
        topic_name = ebola_query[0]
        
        if (topic_name == "dd17-46") and (sys.argv[4] > 6):
            continue
        
        jig.topic_id = topic_name
        
        #FULL_SOLR_URL = "http://172.22.0.11:8983/solr/ebola_extract/select?"
        
        solr = SolrClient(SOLR_SEG_nyt_LMD_URL)
        
        docs = retrieval_top_k_doc_full(topic_query, solr, int(sys.argv[5]), query_range=['content_full_text'])
        
        #print("docs: ",docs)
        
        dict_fileid_score = {}
    
        in_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
        in_dir += "/datas/nonested/{}.json"
        print("in_dir: ",in_dir)
        #in_dir = "data/test_ebola_json/{}.json"
        
        corp = []
        get_id = []

        for dict_doc in docs:
            #list_doc_q.append( dict_doc[1] )
            dict_fileid_score[ dict_doc[1] ] = float(dict_doc[2] )  
            read_json_file(in_dir.format( dict_doc[1] ), dict_doc[1] )
        
        docs = sorted(docs , key = lambda x:x[2] , reverse = True)
        
        for dict_doc in docs[0:30]:
            list_doc_q.append( dict_doc[1] )
        
        out_dir = "data/lda/"
        #out_dir = "data/test_lda/"
        get_lda(out_dir,topic_name )
        
        in_dir_fileid_lda = "data/lda/{}-{}-{}-{}-{}-{}-{}-fileid_lda-single-nyt.txt".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],topic_name)
        
        dict_u_topic = cal_dict_u_topic(in_dir_fileid_lda)
        
        #print("dict_u_topic: ",dict_u_topic)
        
        dict_fileid_topic = get_dict_fileid_topic(in_dir_fileid_lda)
        
        for tt in range( int(sys.argv[4]) ):
            
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
                    file_value = lamb * file_value + (1.0-lamb) * dict_fileid_score[file_id]
                else:
                    file_value = 0.0
                    for topic_id in range(n_topic):
                        key_topic_id = str(topic_id)
                        if key_topic_id == max_topic_id :
                            file_value += lama * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                        else:
                            file_value += (1.0-lama) * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
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
                    topic_score = file_value
                    solr_score = dict_fileid_score[file_id]
                    file_value = lamb * file_value + (1.0-lamb) * dict_fileid_score[file_id]
                    
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
                    
                list_doc_q.remove( tuple[0] )
                if int_choose == 5:
                    break
            
            #print("docs_result: ",docs_result)
            
            interact_with_jig(jig, docs_result, in_dir, 1  )
            
            for dict_doc in docs[30 + tt * 5 : 35 + tt * 5]:
                list_doc_q.append( dict_doc[1] )
            """
            dict_result = jig.get_result_dict()
            print(dict_result)
            """
            #fl.write(json.dumps(dict_result))
            
            """
            out_dir = "data/mmr_scale.txt"
            fl = codecs.open(out_dir, "w", "utf-8")
            for file_id in list_doc_s:
                fl.write(file_id)
                fl.write("\n")
            fl.close()
            """
        jig.judge()    
            #print("ok")
    jig.judge()