import json
import codecs
import sys
import jieba
import logging

logging.basicConfig(level=logging.ERROR)

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

lama = 0.8
lamb = 0.00
n_topic = int(sys.argv[3])

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

def interact_with_jig(jig, docs, interact_times=10):
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5])
        st_ptr += 5
        #print ("itr:", i) #, " rslt:", rslt
        for _ in rslt:
            print ("rslt:", _)
            if _["on_topic"] == '0':
                continue
            flag_choose = 0
            for dict_subtopics in _["subtopics"]:
                #if dict_subtopics["rating"] == "3" or dict_subtopics["rating"] == "4":
                flag_choose = 1
                break
            
            if flag_choose == 1:
                list_doc_s.append( str(dict_key_id[ _["doc_id"] ] ) )
                
                
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

stopword = []
corp = []
get_id = []

def read_json_file(in_path, id):
    
    get_id.append(id)
    
    if sys.argv[7] == "1":
        js = json.load(codecs.open(in_path, "r") )
        line = js["content_p"]
    else:
        js = json.loads(codecs.open(in_path, "r").readline()[1:-1] )
        line = js["content"]
    
    seg_list = jieba.cut(line, cut_all = False)
    
    no_list = []
    for word in seg_list:
        if (word not in stopword) and (len(word)>1):
            no_list.append(word)
            
    corp.append(no_list)

def get_lda(out_dir,topic_name):
    dictionary = corpora.Dictionary(corp)
    corpus = [dictionary.doc2bow(text) for text in corp]
    
    lda = models.LdaModel(corpus, id2word=dictionary, num_topics=n_topic)
    lda.save(out_dir + "{}-{}-{}-{}-{}-{}-{}-{}-much-lda_model.model".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],topic_name) )
    
    ldaOut = lda.print_topics(n_topic)
    file_ldaOut = codecs.open(out_dir + "{}-{}-{}-{}-{}-{}-{}-{}-much-lda_topics.txt".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],topic_name), "w", "utf-8")
    file_ldaOut.write(str(ldaOut))
    
    file_id_lda = codecs.open(out_dir + "{}-{}-{}-{}-{}-{}-{}-{}-much-fileid_lda.txt".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],topic_name), "w", "utf-8")
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
    
    global list_doc_q,list_doc_s,lama,lamb
    """
    
    global stopword
    stopword = [line.strip() for line in codecs.open('data/stopwords.txt',encoding='UTF-8').readlines()];
    
    client = ElasticClient(doc_type="ebola", return_size=1000, index="trec3")
    dictionary = client.search_ebola(
        keyword="Blut-Therapie soll gegen Ebola helfen",
        fields=["title", "content"])
    
    """
    stopword = [line.strip() for line in codecs.open('data/stopwords.txt',encoding='UTF-8').readlines()];
    
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
        list_doc_q = []
        
        topic_query = [ebola_query[1]]
        
        #topic_query = [','.join(topic_query[0].split())]
        topic_name = ebola_query[0]
        
        jig.topic_id = topic_name
        
        #FULL_SOLR_URL = "http://172.22.0.11:8983/solr/ebola_extract/select?"
        
        solr = SolrClient(FULL_SOLR_URL)
        
        docs = retrieval_top_k_doc_full(topic_query, solr, int(sys.argv[5]), query_range=['content'])
        
        #print(docs)
        
        dict_fileid_score = {}
    
        if sys.argv[7] == "1":
            in_dir = "data/clean_ebola_json/{}.json"
        else:
            in_dir = "data/ebola_htmls/{}.json"
        #in_dir = "data/test_ebola_json/{}.json"
        
        corp = []
        get_id = []

        for dict_doc in docs:
            list_doc_q.append(str(dict_key_id[ dict_doc[1] ] ) )
            dict_fileid_score[str(dict_key_id[ dict_doc[1] ] ) ] = float(dict_doc[2] )  
            read_json_file(in_dir.format(str(dict_key_id[ dict_doc[1] ] )), str(dict_key_id[ dict_doc[1] ] ))
        
        out_dir = "data/lda/"
        #out_dir = "data/test_lda/"
        get_lda(out_dir,topic_name )
        
        in_dir_fileid_lda = "data/lda/{}-{}-{}-{}-{}-{}-{}-{}-much-fileid_lda.txt".format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],topic_name)
        
        dict_u_topic = cal_dict_u_topic(in_dir_fileid_lda)
        
        #print("dict_u_topic: ",dict_u_topic)
        
        dict_fileid_topic = get_dict_fileid_topic(in_dir_fileid_lda)
        
        for tt in range( int(sys.argv[4]) ):
            
            if tt == 0:
                lama = 0.9
                lamb = 0.0
            else:
                lama = float(sys.argv[1])
                lamb = float(sys.argv[2])
                
            docs_result_id = []
            
            for i in range(5):
                
                dict_s_topic = cal_dict_s_topic(list_doc_s , in_dir_fileid_lda)
                
                #print("dict_s_topic: ",dict_s_topic)
                
                max_topic_value = 0.0
                max_topic_id = "0"
                quotient = {}
                
                for topic_id in range(n_topic):
                    key_topic_id = str(topic_id)
                    quotient[key_topic_id] = dict_u_topic[key_topic_id] / (1.0 + 2 * dict_s_topic[key_topic_id])
                    """
                    if quotient[key_topic_id] > max_topic_value :
                        max_topic_value = quotient[key_topic_id]
                        max_topic_id = key_topic_id
                    """
                list_quotient = sorted(quotient.items() , key = lambda asd:asd[1] , reverse = True)
                max_file_value = 0.0
                max_file_id = "0"
                for file_id in list_doc_q:
                    
                    if file_id not in dict_fileid_topic:
                        continue
                    
                    file_value = 0.0
                    """
                    for topic_id in range(n_topic):
                        key_topic_id = str(topic_id)
                        if key_topic_id == max_topic_id :
                            file_value += lama * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                        else:
                            file_value += (1.0-lama) * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                    """
                    topic_cnt = 0
                    main_topic = sys.argv[8]
                    for item_topic_id_quo in list_quotient:
                        topic_id = item_topic_id_quo[0]
                        topic_cnt += 1
                        key_topic_id = str(topic_id)
                        if topic_cnt <= main_topic :
                            file_value += lama * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                        else:
                            file_value += (1.0-lama) * quotient[key_topic_id] * (dict_fileid_topic[file_id][key_topic_id] if key_topic_id in dict_fileid_topic[file_id] else 0.0)
                            
                    #print("topic_score: ",file_value )
                    #print("solr_score: ",dict_fileid_score[file_id])
                    #add_score
                    topic_score = file_value
                    solr_score = dict_fileid_score[file_id]
                    file_value = lamb * file_value + (1.0-lamb) * dict_fileid_score[file_id]
                    
                    if file_value > max_file_value:
                        max_file_value = file_value
                        max_file_id = file_id
                        max_topic_score = topic_score
                        max_solr_score = solr_score
                
                print("topic_score: ",max_topic_score)
                print("solr_score: ",max_solr_score)
                docs_result_id.append(max_file_id)
                list_doc_q.remove(max_file_id)
            
            docs_result = []
            
            for doc_id in docs_result_id:
                for dict_doc in docs:
                    if str(dict_key_id[ dict_doc[1] ] ) == doc_id:
                        docs_result.append(dict_doc)
                        break
                        
            interact_with_jig(jig, docs_result, 1)
        
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
            
            #print("ok")
    jig.judge()