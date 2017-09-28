# encoding=utf-8
# @author: Weimin Zhang
# @date: 17/2/24 下午6:32

import time
import os
import os.path
import jieba
import csv
import pandas as pd
import re

import numpy as np
from scipy.sparse import *
# from global_parameters import punctuations
from sklearn.metrics import precision_recall_curve, roc_curve, auc, classification_report


class Logger(object):
    def __init__(self, level=1):
        self.level = level
        self.INFO_LEVEL = 1

    def info(self, s=""):
        if self.INFO_LEVEL <= self.level:
            print time.strftime("%b %d %Y %H:%M:%S", time.localtime(time.time())) + \
                  " [INFO] ", s


def judge_file_code(filename):
    import chardet
    f = open(filename, 'r')
    data = f.readline(1)
    print chardet.detect(data)


def judge_coding_type(s):
    import chardet
    # if isinstance(s, unicode):
    #     print "unicode"
    # if isinstance(s, utf8):
    #     print "utf8"
    #
    # if isinstance(s, ascii):
    #     print
    # print (chardet.detect(s))
    if type(s) == list:
        return (chardet.detect(s[0]))
    else:
        return (chardet.detect(s))


def filter_punctuations(l):
    ret = []

    for w in l:
        if w not in punctuations:
            ret.append(w)

    return ret


def get_dir_files(dir_path):
    files = []
    names = []
    for parent, dirnames, filenames in os.walk(dir_path):  # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        # for dirname in dirnames:  # 输出文件夹信息
        #     print "parent is:" + parent
        #     print  "dirname is" + dirname

        for filename in filenames:  # 输出文件信息
            # print "parent is:" + parent
            # print "filename is:" + filename
            # print "the full name of the file is:" + os.path.join(parent, filename)  # 输出文件路径信息
            files.append(os.path.join(parent, filename))
            names.append(filename)

    return files, names


def line_count(filename):
    # count = len(open(filename, "rU").readlines())
    count = len(open(filename, "r").readlines())
    # print count
    return count


def file_str_punc(s):
    s = s.decode("utf8")
    string = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？：、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"), s)
    print string
    return string


def cut_words_filter_punc(s):
    s = file_str_punc(s)
    seg_list = list(jieba.cut(s, cut_all=False))

    return ' '.join(seg_list)


# cut words
def doc_to_words(doc):
    type_dic = judge_coding_type(doc)

    if type_dic["encoding"] == 'utf-8':
        udoc = doc
    else:
        udoc = doc.encode('utf8')
    seg_list = list(jieba.cut(udoc, cut_all=False))

    return seg_list


def combine_csv_file(files, out_file, offsets=[]):
    if len(offsets) == 0:
        offsets = [0] * len(files)
    if len(offsets) != len(files):
        print "ERROR, combine_csv_file, offset not equal to file cnt:"

    data_lists = []
    print "combining files...", files
    for i, f in enumerate(files):
        data_lists.append(
            csv_feature_to_data_list(f))

        if i == 0:
            sz = len(data_lists[-1])
        else:
            if sz != len(data_lists[-1]):
                print "ERROR combine_csv_file len not equal:", sz, len(data_lists[-1]), f
    ret = []
    for i, d in enumerate(data_lists[0]):
        line = []
        for j, v in enumerate(data_lists):
            line += v[i][offsets[i]:]
        if i == 0:
            print "after combining, col cnt:", len(line)
        ret.append(line)
    csv_write_file(out_file, ret)
    return ret


def csv_write_file(filename, data_list):
    csvfile = file(filename, 'wb')

    # print str(data_list) + " " + str( type(data_list[0]))

    writer = csv.writer(csvfile)
    writer.writerows(data_list)

    # for r in data_list:
    #    writer.writerow(list(r))

    csvfile.close()


# TODO:可以写的更好点...
def csv_write_X_Y(filename, X, Y):
    if len(X) != len(Y):
        print "X and Y len not equal", len(X), len(Y)
    else:
        print "data len:", len(X), len(Y)

    ret = []
    for i in range(len(X)):
        ret.append([Y[i], ] + X[i])

    print "writing..... ", filename

    csv_write_file(filename, ret)


def txt_write_file(filename, data_list):
    wfile = open(filename, 'w')
    space = ' '
    try:
        for line in data_list:
            v = [str(i) for i in line]
            # wfile.write(space.join(v) )
            # print space.join(v) + '\n',
            wfile.write(space.join(v) + '\n')
    finally:
        wfile.close()
    print "write file:", filename, " len:", len(data_list)


# TODO:可以写的更好点...
def txt_write_X_Y(filename, X, Y):
    if len(X) != len(Y):
        print "X and Y len not equal", len(X), len(Y)
    else:
        print "data len:", len(X), len(Y)

    ret = []
    for i in range(len(X)):
        if type(X[i]) == str:
            line = X[i].split(' ')
        else:
            line = X[i]
        ret.append([str(Y[i]), ] + line)

    print "writing..... ", filename

    txt_write_file(filename, ret)


def txt_write_line_file(filename, data_line_list):
    wfile = open(filename, 'w')
    try:
        for line in data_line_list:
            wfile.write(line.strip() + '\n')
    finally:
        wfile.close()
    print "txt_write_line_file:", filename, " len:", len(data_line_list)


def txt_to_line_list(filename):
    ret = []
    rfile = open(filename, 'r')

    try:
        for line in rfile:
            ret.append(line.strip())
    finally:
        rfile.close()

    return ret


def txt_to_list(filename, sep=' '):
    ret = []
    rfile = open(filename, 'r')

    try:
        for line in rfile:
            line = line.strip()
            if type(line) != str:
                print "TYPE ERROR:", type(line), line
            try:
                tl = line.split(sep)
            except Exception, e:
                print e, "len:", len(line), " find:", line.find(','), " sep:", sep  # , " find sep:", line.find(sep)
                print "ERROR, TXT TOT LIST, LINE:", type(line), line

            l = line.split(sep)
            ret.append(l)
    finally:
        rfile.close()

    return ret


def txt_to_X_Y(filename, sep=' '):
    X = []
    Y = []
    rfile = open(filename, 'r')

    try:
        for line in rfile:
            line = line.strip()
            l = line.split(sep)
            # ret.append(l)
            Y.append(int(l[0]))
            X.append(l[1:])
    finally:
        rfile.close()

    return X, Y


def csv_to_X_Y(filename):
    df = pd.read_csv(filename, header=None, sep=',')
    X = []
    Y = []
    for v in df.values:
        line = list(v)
        Y.append(int(line[0]))
        X.append(line[1:])
    print "csv_to_X_Y, len:", len(X), len(Y)
    return X, Y


def mat_to_coo(mat, row_len, col_len):
    row = []
    col = []
    data = []

    for i, line in enumerate(mat):

        for j, v in enumerate(line):

            if v != 0:
                row.append(i)
                col.append(j)
                data.append(v)

    return coo_matrix((np.array(data), (np.array(row), np.array(col))), shape=(row_len, col_len))


def mat_to_csc(mat, row_len, col_len):
    mat = mat_to_coo(mat, row_len, col_len)
    return mat.tocsc()


def cal_F1(p, r):
    f1 = 0.0
    if p == 0 and r == 0:
        return 0.0
    return 2 * float(p * r) / (p + r)


def multi_class_prf1_report(pres, Ys):
    print "class cnt:", len(Ys)
    for i in range(len(Ys)):
        print "=== class ", i, " ==="
        # precision, recall, thresholds = precision_recall_curve( Ys[i], pres[i])
        report = classification_report(np.array(pres[i]), np.array(Ys[i]))

        print report
        # print "precision:", precision
        # print "recall:", recall
        # print "thresholds:", thresholds
        #
        # mx_f1 = 0.0
        # best_threshold = 0.0
        #
        # for j in range( len(precision) ):
        #     f1 = cal_F1(precision[j], recall[j])
        #     if f1 > mx_f1:
        #         mx_f1 = f1
        #         best_threshold = thresholds[j]
        #
        # print "f1:", mx_f1, " threshold:", best_threshold

    print ""


# 保持顺序的l1-l2
# def minus_list_ordered(l1, l2):
#     ret = []
#     # s = set(l2)
#     for v in l1:
#         for v2 in l2:
#             if v != v2 : continue
#             ret.append()
#     return ret

# def txt_to_list(filename):
#     file_obj = open(filename, "r")
#     ret = []
#     labels = []
#     docs = []
#     space = " "
#
#     rslt = open(rfname, "w")
#
#     try:
#         process_cnt = 0
#         for line in file_obj:
#             if len(line) == 0:
#                 continue
#             l = []
#             labels.append(int(line[0]))
#             words = doc_to_words(line[2:])
#             docs.append(words)
#
#             for t in words:
#                 l.append(t)
#
#             rslt.write(space.join(l) + '\n')
#
#             process_cnt += 1
#
#             if process_cnt % 10000 == 0:
#                 log_info("parse_data, processed cnt:" + str(process_cnt))
#
#     finally:
#         file_obj.close()
#         rslt.close()
#
#     # dic, dic_len = create_dict(docs)
#     # bow_corpus = [dic.doc2bow(text) for text in doc_to_words]
#
#     # tf_idf = models.TfidfModel(bow_corpus)
#
#     return docs, labels


# TODO：可能需要测试一下第一行是不是读取了，如果正确的话吧代码的以前的函数全部换掉
def csv_feature_to_X_Y(filename):
    csv_reader = csv.reader(open(filename))
    X = []
    Y = []
    for row in csv_reader:
        Y.append(int(row[0]))
        X.append([float(v) for v in row[1:]])
        # print X[-1][0:5], Y[-1]

    return X, Y


def csv_feature_to_data_list(filename):
    csv_reader = csv.reader(open(filename))
    ret = []
    for row in csv_reader:
        ret.append([float(v) for v in row])
    return ret


if __name__ == "__main__":
    # ret = get_dir_files("/Users/zhangweimin/Documents/MyDocs/CodeLibrary/Sohu/data/articles")
    # print ret
    # filename = "/Users/zhangweimin/CodeLibrary/Sohu/data/dataset2/raw_val_docs_file.txt"
    # # print judge_file_code(filename)
    # temp = "想做/ 兼_职/学生_/ 的 、加,我Q：  1 5.  8 0. ！！？？  8 6 。0.  2。 3     有,惊,喜,哦"
    # print cut_words_filter_punc(temp)
    # dir_path = "C:"
    # # dir_path = os.path.join(dir_path, "Users", "xinlewang", "Desktop", "Zafedom", "test_xy.csv")
    # dir_path = "C:\\Users\\xinlewang\\Desktop\\Zafedom\\test_xy.csv"
    # X, Y = csv_feature_to_X_Y(dir_path)
    # class Logger(object):
    #     def __init__(self, level=1):
    #         self.level = level
    #         self.INFO_LEVEL = 1
    #
    #     def info(self, s=""):
    #         if self.INFO_LEVEL <= self.level:
    #             print time.strftime("%D:%H:%M:%S", time.localtime(time.time())) + \
    #                   " [INFO] ", s
    logger = Logger()
    logger.info("test")
