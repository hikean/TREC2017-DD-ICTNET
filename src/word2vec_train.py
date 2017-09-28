# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/4 下午4:22
# @version: 1.0

from global_settings import *
from gensim.models import Word2Vec
from preprocess_utils import *
import multiprocessing
from utils import *
from doc2vec_train import get_files, get_file_id


def train_w2v(model_file, word_sentences, epoch_cnt = 5 , p_size=128, p_window=7, p_min_count=5):

    logging.info("train word2vec epoch:" + str(epoch_cnt))

    model = Word2Vec(word_sentences, size=p_size, iter=epoch_cnt, window=p_window, min_count=p_min_count,
                     workers=multiprocessing.cpu_count() * 3)

    logging.info("train w2v end ")
    model.save(model_file)

    return model


def doc2vec(model, doc, sp=','):
    if type(doc) == list:
        words = doc
    else:
        words = doc.split(sp)

    ret =[]
    for w in words:
        if model.wv.__contains__(w):
            ret.append(model[w])
            # print "get one word:", model[w]
    ret = np.asarray(ret)
    if ret.shape[0] == 0:
        return [0.0] * model.vector_size
    else:
        return (sum(ret) / (1.0 * ret.shape[0])).tolist()

def corpus_process_w2v_feat(data_dir, w2v_feat_file, prefix="content_", epochs = 3):

    model_file = data_dir + "model/" + prefix+"w2v.model"

    file_list = get_files(data_dir)

    print "file cnt:", len(file_list)

    logging.info("clean texts")
    sents = []
    labels = []
    for i, v in enumerate(file_list):
        labels.append(prefix + get_file_id(v))
        sents.append(
            file2cleansentence_en(v).split(' ')
        )

    # logging.info("make labeled sents")
    # labeled_docs = sentsListToLabeledSents(sents, labels)
#ttrain_w2v(model_file, word_sentences, epoch_cnt = 5 , p_size=128, p_window=7, p_min_count=5):
    logging.info("train doc vectors")
    model = train_w2v(model_file=model_file, word_sentences=sents, epoch_cnt=50,p_min_count=5)

    logging.info("infer_vectors:")
    ret = []
    for i, v in enumerate(labels):
        # line = [v[v.find('_') + 1:]] + model.infer_vector(sents[i]).tolist()
        line = [v[v.find('_') + 1:]] + doc2vec(model, sents[i])
        ret.append(line)

    logging.info("writing vec file...")
    txt_write_file(w2v_feat_file, ret)


def test_train():
    data_dir = "/Users/zhangweimin/Desktop/TREC/Data/build_data/check_data/"
    out_dir = "/Users/zhangweimin/Desktop/TREC/Data/build_data/check_data/out"
    model_file = data_dir +"model/" + "w2v.model"
    word_file = data_dir +"model/" + "w2v_word.model"
    file_list = get_files(data_dir)
    d2v_file = out_dir + "content_w2v_feat_vector.txt"

    print "file cnt:", len(file_list)

    logging.info("clean texts")
    sents = []
    labels = []
    for i,v in enumerate(file_list):
        labels.append( "content_" + get_file_id(v) )
        if i == 0:
            print labels[-1]
        sents.append(
            file2cleansentence_en(v).split(' ')
        )

    # labeled_docs = sentsListToLabeledSents(sents, labels)
    #train_w2v(model_file, word_sentences, epoch_cnt = 5 , p_size=128, p_window=7, p_min_count=1):
    model = train_w2v(model_file,sents, 5)

    # OK
    # print "before infer:", model.infer_vector(sents[0]).tolist()
    print "sents[0]:", sents[0]
    print "before doc2v:", doc2vec(model, sents[0])

    model = Word2Vec.load(model_file)
    # print model.raw_vocab

    print "sents[0]:", sents[0]
    print "type:", type(model)
    print "load and infer:", doc2vec(model, sents[0])
    # print "new sent:", model.infer_vector(['ebola', 'health', 'death'])

    logging.info("infer_vectors:")
    ret = []
    for i,v in enumerate(labels):
        line = [v[v.find('_') + 1:]] + doc2vec(model, sents[i])
        ret.append(line)
    txt_write_file(d2v_file, ret)

# test_train()

if __name__ == '__main__':
    EPOCH_CNT = 50

    root_path =  "/home/zhangwm/zhangweimin/Data/trec/build_data/" #"/Users/zhangweimin/Desktop/TREC/Data/build_data/"
    dir_path = os.path.join(root_path, "ebola/")
    content_dir = os.path.join(dir_path, "text")
    title_dir = os.path.join(dir_path, "title")

    content_d2v_file = os.path.join(root_path, "content_w2v_feat_file.txt")
    title_d2v_file = os.path.join(root_path, "title_w2v_feat_file.txt")

    print "content cnt:", len(get_files(content_dir)), " title cnt:", len(get_files(title_dir))

    # dir_path = "/Users/zhangweimin/Desktop/TREC/Data/build_data/check_data/"
#corpus_process_w2v_feat(data_dir, w2v_feat_file, prefix="content_", epochs = 3)
    # corpus_process_w2v_feat(data_dir=content_dir, w2v_feat_file=content_d2v_file, prefix="content_", epochs=EPOCH_CNT)
    corpus_process_w2v_feat(data_dir=title_dir, w2v_feat_file=title_d2v_file, prefix="title_", epochs=EPOCH_CNT)


__END__ = True


