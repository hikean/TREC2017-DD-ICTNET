import json
import codecs
import sys
import jieba
import math
from os.path import exists, isfile, isdir
from gensim import corpora, models
from sklearn import lda

sys.path.append('../utils')

from JigClient import JigClient
from es_client import ElasticClient

from basic_init import *

from src.utils.SolrClient import SolrClient
from src.utils.Document import *
from src.utils.JigClient import *

list_doc_s = []
list_doc_q = []
dict_key_id = json.load(codecs.open("data/key2id.json","r") )
idf_dictionary = json.load(codecs.open("data/dict-all-clean.txt","r") )

def get_dict_keyword(str_text , cnt_key_word):
    list_word = jieba.cut( str_text , cut_all = False)
    cnt_word = {}
    cnt_word_in_doc = 0.0
    for word in list_word:
        if word not in idf_dictionary:
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


def interact_with_jig(jig, docs, interact_times=10):
    list_re_doc_id = []
    list_unre_doc_id = []
    dict_keyword_score = {}
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5])
        st_ptr += 5
        print ("itr:", i) #, " rslt:", rslt
        for _ in rslt:
            print ("rslt:", _)
            if _["on_topic"] == '0':
                list_unre_doc_id.append( str(dict_key_id[ _["doc_id"] ] ) )
                continue
            flag_choose = 0
            for dict_subtopics in _["subtopics"]:
                #if dict_subtopics["rating"] == "3" or dict_subtopics["rating"] == "4":
                flag_choose = 1
                dict_keyword = get_dict_keyword(dict_subtopics["passage_text"] , 3)
                for word in dict_keyword:
                    if word not in dict_keyword_score:
                        dict_keyword_score[word] = 0.0
                    dict_keyword_score[word] += dict_keyword[word]
            
            if flag_choose == 1:
                list_doc_s.append( str(dict_key_id[ _["doc_id"] ] ) )
                list_re_doc_id.append( str(dict_key_id[ _["doc_id"] ] ) )
            else:
                list_unre_doc_id.append( str(dict_key_id[ _["doc_id"] ] ) )
                
    return list_re_doc_id,list_unre_doc_id,dict_keyword_score
    
    
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

stopword = [line.strip() for line in codecs.open('data/stopwords.txt',encoding='UTF-8').readlines()]
corp = []
get_id = []

def read_json_file(in_path, id):
    
    get_id.append(id)
    
    js = json.load(codecs.open(in_path, "r") )
    line = js["content_h2"]
    seg_list = jieba.cut(line, cut_all = False)
    no_list = []
    for word in seg_list:
        if (word not in stopword) and (len(word)>1):
            no_list.append(word)
            
    corp.append(no_list)
    
def get_dict_key_word(in_dir , doc_id , cnt_key_word):
    js = json.load( codecs.open( in_dir.format(doc_id) , "r") )
    list_word = jieba.cut( js["content_h2"] , cut_all = False)
    cnt_word = {}
    cnt_word_in_doc = 0.0
    for word in list_word:
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
        dict_key_word = get_dict_key_word(in_dir, doc_id, 5)
        for word in dict_key_word:
            if word not in dict_query:
                dict_query[word] = dict_key_word[word]
            else:
                dict_query[word] += dict_key_word[word]
    
    for doc_id in list_unre_doc_id:
        dict_key_word = get_dict_key_word(in_dir, doc_id, 5)
        for word in dict_key_word:
            if word not in dict_query:
                dict_query[word] = -dict_key_word[word]
            else:
                dict_query[word] -= dict_key_word[word]
    
    str_new_query = ""
    for word in dict_query:
        str_new_query += word + "^" + str(dict_query[word]) + ","
    
    str_new_query = str_new_query[:-1]
    return str_new_query

def get_idf_dictionary(list_doc_id , in_dir , int_cnt_doc):
    
    dict_cnt_word_in_doc = {}
    for doc_id in list_doc_id:
        js = json.load( codecs.open( in_dir.format(doc_id) , "r") )
        list_word = jieba.cut( js["content_p"] , cut_all = False)
        
        dict_word_in_doc = {}
        for word in list_word:
            if (word not in stopword) and (len(word) > 1):
                dict_word_in_doc[word] = 1.0

        for word in dict_word_in_doc:
            if word in dict_cnt_word_in_doc:
                dict_cnt_word_in_doc[word] += 1.0
            else:
                dict_cnt_word_in_doc[word] = 1.0
    
    idf_dictionary = {}
    for word in dict_cnt_word_in_doc:
        idf_dictionary[word] = math.log(int_cnt_doc / dict_cnt_word_in_doc[word])
    
    return idf_dictionary

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
    
    global list_doc_q , list_doc_s , lama , lamb , corp , get_id
    
    list_query = [('DD16-1', 'US Military Crisis Response'),
          ('DD16-2', 'Ebola Conspiracy Theories'),
          ('DD16-3', 'healthcare impacts of ebola'),
          ('DD16-4', 'Daniel Berehulak'),
          ('DD16-5', 'Ewedu as an Ebola Treatment'),
          ('DD16-6', 'Alleged Alternative Treatments for Ebola'),
          ('DD16-7', 'Urbanisation/Urbanization '),
          ('DD16-8', 'Dr. Olivet Buck'),
          ('DD16-9', 'Thomas Eric Duncan'),
          ('DD16-10', 'Economic impact of ebola'),
          ('DD16-11', 'U.S. healthcare workers'),
          ('DD16-12', 'is there a natural immunity to ebola'),
          ('DD16-13', 'Dr. Steven Hatch'),
          ('DD16-14', 'T.B. Joshua'),
          ('DD16-15', 'Maurice Iwu'),
          ('DD16-16', 'Modeling'),
          ('DD16-17', 'Kenema District Government Hospital'),
          ('DD16-18', 'Robots'),
          ('DD16-19', 'Attacks on ebola aid'),
          ('DD16-20', 'Pauline Cafferkey'),
          ('DD16-21', 'Ebola medical waste'),
          ('DD16-22', 'radio school'),
          ('DD16-23', 'Crowdfunding Crowdsourcing'),
          ('DD16-24', 'Olu-Ibukun Koye Spread EVD to Port Harcourt'),
          ('DD16-25', "Emory University's role in Ebola treatment"),
          ('DD16-26', 'Effects of African Culture'),
          ('DD16-27', 'kaci hickox'),
          ('DD16-28', 'Is the distribution of permafrost changing in the Arctic?'),
          ('DD16-29', 'ice sheet sea level rise'),
          ('DD16-30', 'Where are basal boundary conditions in East Antarctica?'),
          ('DD16-31', 'sea level rise change strom surge'),
          ('DD16-32', 'polar oceans freshwater sensitivity'),
          ('DD16-33', 'sea-level rise and coastal erosion'),
          ('DD16-34', 'melting ice sheet ocean circulation'),
          ('DD16-35', 'snow accumulation rate Greenland'),
          ('DD16-36', 'Is the rate of snow accumulation changing in Antarctica?'),
          ('DD16-37', 'west antarctic ice sheet'),
          ('DD16-38', 'Are significant changes occurring in ocean productivity'),
          ('DD16-39',
           'How will shipping be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-40', 'Polar terrestrial ecosystems CO2 trace gas'),
          ('DD16-41', 'Artic sea ice fishery'),
          ('DD16-42',
           'How will offshore mineral extraction be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-43', 'Is ice sheet elevation changing'),
          ('DD16-44',
           'Are changes occurring in the distribution and productivity of Arctic vegetation?'),
          ('DD16-45',
           'How will subsistence fishing and hunting be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-46', 'Are changes occurring the coverage of the Arctic Sea ice'),
          ('DD16-47', 'Arctic sea ice thickness'),
          ('DD16-48', 'polar ocean global ocean circulation'),
          ('DD16-49', 'Are changes occurring in the circulation of the Arctic Sea'),
          ('DD16-50', 'planning for sea level rise'),
          ('DD16-51',
           'How will changes in sea-level rise affect coastal freshwater supply'),
          ('DD16-52', 'albedo feedback future climate change Poles'),
          ('DD16-53', 'climate change polar bears')]
    
    tot_itr_times = int(sys.argv[4])
    jig = JigClient("",tot_itr_times=tot_itr_times)
    
    for ebola_query in list_query[0:int(sys.argv[6])]:
        
         
        list_doc_s = []
        
        topic_query = [ebola_query[1]]
          
        #topic_query = [','.join(topic_query[0].split())]
        topic_name = ebola_query[0]
        
        jig.topic_id = topic_name
        
        solr = SolrClient(FULL_SOLR_URL)
        
        for tt in range( int(sys.argv[4]) ):
            

            #FULL_SOLR_URL = "http://172.22.0.11:8983/solr/ebola_extract/select?"
            
            print("query: ",topic_query)
            docs = retrieval_top_k_doc_full(topic_query, solr, int(sys.argv[5]) , query_range=['content'])
            
            #print(docs)
        
            in_dir = "data/clean_ebola_json/{}.json"
            #in_dir = "data/test_ebola_json/{}.json"
            
            list_re_doc_id , list_unre_doc_id , dict_keyword = interact_with_jig(jig, docs, 1)
            
            if tt == 0: 
                topic_query = [init_query(topic_query[0])]  
            topic_query = [rocchio_get_new_query(topic_query[0] , list_re_doc_id, list_unre_doc_id, in_dir, dict_keyword)]

            #print("ok")
    jig.judge()