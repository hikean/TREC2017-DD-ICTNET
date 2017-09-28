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
def interact_with_jig(jig, docs, interact_times=10 ):
    st_ptr = 0

    for i in range(interact_times):
        rslt = jig.run_itr(docs[st_ptr:st_ptr+5])
        st_ptr += 5
        #print ("itr:", i) #, " rslt:", rslt
#         if rslt is not None:
        for _ in rslt:
            print ("rslt:", _)
                
                
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

stopword = [line.strip() for line in codecs.open('data/stopwords.txt',encoding='UTF-8').readlines()];

def init_query(str_query):
    list_query = jieba.cut(str_query, cut_all = False)
    word_set = set([])
    for word in list_query:
        if (word not in stopword) and (len(word) > 1):
            word_set.add(word)
    
    new_query = ""
    for word in word_set:
        new_query += word + "^" + "1.0 " 
    
    new_query = new_query[:-1]
    return new_query

if __name__ == '__main__':
    
    """
    
    global stopword
    
    
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

    
    tot_itr_times = int(sys.argv[1])
    jig = JigClient("",tot_itr_times=tot_itr_times,base_jig_dir="/home/zhangwm/Software/dk_jig4/jig/trec-dd-jig/")
    
    for ebola_query in NYT_TOPICS:
        
        if sys.argv[2] == "1":
            if ebola_query[1][-1] == "?":
                topic_query = [ebola_query[1][0:-1]]
            else:
                topic_query = [ebola_query[1]]
        else:
            topic_query = [ebola_query[1]]
        #print("topic_query: ",topic_query)
        #topic_query = [','.join(topic_query[0].split())]
        topic_name = ebola_query[0]
        
        if (topic_name == "dd17-46") and ( int(sys.argv[1]) > 6):
            continue
        
        jig.topic_id = topic_name
        
        #FULL_SOLR_URL = "http://172.22.0.11:8983/solr/ebola_extract/select?"
        
        solr = SolrClient(SOLR_SEG_nyt_LMD_URL)
        
        topic_query = [init_query(topic_query[0])]
        
        docs = retrieval_top_k_doc_full(topic_query, solr, 100, query_range=['content_full_text'])
        
        interact_with_jig(jig, docs, int(sys.argv[1])  )

    jig.judge()