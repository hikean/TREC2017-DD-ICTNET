from w2v_utils import VecUtils
import os
import json
if __name__ == '__main__':

    root_path = "/home/zhangwm/zhangweimin/Data/trec/build_data/"
    query_d2v_file = os.path.join(root_path, "fengyue/query_t2v_file.json")
    out = open(query_d2v_file, 'w')
    model_path = os.path.join(root_path, "ebola/titlemodel/title_w2v.model")
    query = json.load(open(os.path.join(root_path, "fengyue/query.json")))
    vec_utils = VecUtils(model_path)

    query_map = {}

    for key, value in query.items():
        query_id = key.split('-')[1].split('.')[0]
        vector = vec_utils.doc2vec(value)
        print vector
        query_map[query_id] = vector
								
    json.dump(query_map, out)

				

	
