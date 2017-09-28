# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/6/17 下午9:19
# @version: 1.0

'''
根据看的
https://rare-technologies.com/doc2vec-tutorial/
应该是每个文件先处理成一个句子

ebola长度:
content cnt: 194481  title cnt: 194481

只处理这样的东西:

输出文件格式：
输出两个文件：
content的d2v: label vector
title d2v同上
label指的是 xx.json的xx

'''

import random
import os
from preprocess_utils import *
from log import *
from utils import *

def get_files(dir_path):
    filenames = os.listdir(dir_path)
    return [ os.path.join(dir_path, f) for f in filenames if os.path.isfile(os.path.join(dir_path, f) )]

def get_file_id(filename):
    return filename[ filename.rfind('/')+1: filename.find('.') ]

def train_d2v(docs, model_file, word_file, epoch_cnt = 10, if_shuffle=True, learn_rate = 0.025, dec_lr = 0.002, size=100, window=8, min_count=5, workers=4, epoch=5):
    model = Doc2Vec(alpha=learn_rate, size=100, window=8, min_count=5, workers=4)
    log_info("build vocab...")
    model.build_vocab(docs)
    if epoch_cnt != 0:
        log_info( "d2v train, epoch %d:" % epoch )
        print " learn rate:", model.alpha, " dec learn rate by:", dec_lr, " tot epoch:", epoch_cnt
        model.train(docs, total_examples=model.corpus_count, epochs=epoch_cnt)
        model.alpha -= dec_lr
        model.min_alpha = model.alpha  # fix the learning rate, no decay
    model.delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)
    model.save(model_file)

    return model

def test_train():
    data_dir = "/Users/zhangweimin/Desktop/TREC/Data/build_data/check_data/"
    out_dir = "/Users/zhangweimin/Desktop/TREC/Data/build_data/check_data/out"
    model_file = data_dir +"model/" + "d2v.model"
    word_file = data_dir +"model/" + "d2v_word.model"
    file_list = get_files(data_dir)
    d2v_file = out_dir + "content_vector.txt"

    print "file cnt:", len(file_list)

    log_info("clean texts")
    sents = []
    labels = []
    for i,v in enumerate(file_list):
        labels.append( "content_" + get_file_id(v) )
        if i == 0:
            print labels[-1]
        sents.append(
            file2cleansentence_en(v).split(' ')
        )

    labeled_docs = sentsListToLabeledSents(sents, labels)

    model = train_d2v(labeled_docs, model_file, word_file, 3)

    # OK
    print "before infer:", model.infer_vector(sents[0]).tolist()

    model = Doc2Vec.load(model_file)

    print "sents[0]:", sents[0]
    print "type:", type(model)
    print "load and infer:", model.infer_vector(sents[0]
                                       ).tolist() #ERROR
    print "new sent:", model.infer_vector(['ebola', 'health', 'death'])

    log_info("infer_vectors:")
    ret = []
    for i,v in enumerate(labels):
        line = [ v[ v.find('_')+1: ] ] + model.infer_vector(sents[i]).tolist()
        ret.append(line)
    txt_write_file(d2v_file, ret)

def test_get_file_id():
    fn = "/Users/zhangweimin/Desktop/TREC/Data/build_data/check_data/111107.json"
    print get_file_id(fn)

# test_train()


def corpus_train(data_dir, d2v_file, prefix="content_", epochs = 3):

    model_file = data_dir + "model/" + "d2v.model"
    word_file = data_dir + "model/" + "d2v_word.model"
    file_list = get_files(data_dir)

    print "file cnt:", len(file_list)

    log_info("clean texts")
    sents = []
    labels = []
    for i, v in enumerate(file_list):
        labels.append(prefix + get_file_id(v))
        sents.append(
            file2cleansentence_en(v).split(' ')
        )

    log_info("make labeled sents")
    labeled_docs = sentsListToLabeledSents(sents, labels)

    log_info("train doc vectors")
    model = train_d2v(labeled_docs, model_file, word_file, epochs)

    log_info("infer_vectors:")
    ret = []
    for i, v in enumerate(labels):
        line = [v[v.find('_') + 1:]] + model.infer_vector(sents[i]).tolist()
        ret.append(line)

    log_info("writing vec file...")
    txt_write_file(d2v_file, ret)

if __name__ == '__main__':

    EPOCH_CNT = 100

    root_path = "/Users/zhangweimin/Desktop/TREC/Data/build_data/"
    dir_path = os.path.join(root_path, "ebola/")
    content_dir = os.path.join(dir_path, "text")
    title_dir = os.path.join(dir_path, "title")

    content_d2v_file = os.path.join(root_path, "content_d2v_file.txt")
    title_d2v_file = os.path.join(root_path, "title_d2v_file.txt")

    print "content cnt:", len(get_files(content_dir)), " title cnt:", len(get_files(title_dir))

    # dir_path = "/Users/zhangweimin/Desktop/TREC/Data/build_data/check_data/"

    corpus_train(content_dir, content_d2v_file, prefix="content_", epochs = EPOCH_CNT)
    corpus_train(title_dir, title_d2v_file, prefix="title_", epochs=EPOCH_CNT)




__END__ = True