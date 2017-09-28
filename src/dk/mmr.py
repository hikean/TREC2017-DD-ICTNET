import json
import codecs
import jieba
from datasketch import MinHashLSHForest, MinHash
import sys

sys.path.append('../utils')

from JigClient import JigClient
from es_client import ElasticClient

stopword = []

forest = MinHashLSHForest(num_perm=128)
lam = 0.5

def add_json_in_mh(in_dir,file_id):
    
    js = json.load(codecs.open(in_dir, "r") )
    line = js["content_p"]
    seg_list = jieba.cut(line, cut_all = False)
    no_list = []
    for word in seg_list:
        if word not in stopword:
            no_list.append(word)

    mh = MinHash(num_perm = 128)
    for word in no_list:
        mh.update(word.encode('utf8'))
        
    forest.add(file_id, mh)

def query_sim(in_dir):
    
    js = json.load(codecs.open(in_dir, "r") )
    line = js["content_p"]
    seg_list = jieba.cut(line, cut_all = False)
    no_list = []
    for word in seg_list:
        if word not in stopword:
            no_list.append(word)

    mh = MinHash(num_perm = 128)
    for word in no_list:
        mh.update(word.encode('utf8'))
    
    result = forest.query(mh,1)
    return mh.jaccard(forest[result[0]])
    
if __name__ == '__main__':
    
    global stopword
    stopword = [line.strip() for line in codecs.open('data/stopwords.txt',encoding='UTF-8').readlines()];
    
    client = ElasticClient(doc_type="ebola", return_size=1000, index="trec3")
    dictionary = client.search_ebola(
        keyword="Blut-Therapie soll gegen Ebola helfen",
        fields=["title", "content"])
    
    #in_dir = "data/clean_ebola_json/{}.json"
    in_dir = "data/test_ebola_json/{}.json"
    
    result = dictionary["results"]
    
    list_doc_q = []
    for doc_json in result[1:]:
        dict_file = doc_json
        list_doc_q.append(dict_file)
    
    list_doc_s = []
    list_doc_s.append(result[0])
    
    file_id = result[0]["id"]
    add_json_in_mh(in_dir.format(file_id),file_id )
    
    del list_doc_q[0]
    for i in range(4):
        for doc_json in list_doc_q:
            doc_json["mmr"] = lam * doc_json["score"] - (1.0 - lam) * query_sim( in_dir.format(doc_json["id"] ) )
    
        sorted(list_doc_q, cmp=lambda a,b: a["mmr"]-b["mmr"])
        list_doc_s.append(list_doc_q[0])
        add_json_in_mh(in_dir.format(list_doc_q[0]["id"]), list_doc_q[0]["id"])
        del list_doc_q[0]
    
    out_dir = "data/mmr.txt"
    fl = codecs.open(out_dir, "w", "utf-8")
    for file_json in list_doc_s:
        fl.write(file_json["id"])
        fl.write("\n")
    fl.close()
    
    print("ok")
