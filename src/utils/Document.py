# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/9 下午3:58
# @version: 1.0

from basic_init import *
from constants import *
from src.global_settings import *

class Documnet(object):
    def __init__(self,
                 key=None,
                 doc_id=None,
                 score=None):
        self.key = key
        self.doc_id = doc_id
        self.score = score
        #TODO: add necessary field



#doc2tuple相关的， 因为前三个字段和jig的判别是想对应的，不要改变，如果需要添加在后面append即可，但是前面三个的次序不要变
def doc2tuple(doc):
    return (doc[DOC_ID], doc[KEY], doc[SCORE])

def doc2tuple2(doc):
    if type(doc[KEY]) == list:
        return (0, doc[KEY][0], doc[SCORE])
    else:
        return (0, doc[KEY], doc[SCORE])

def doc2tuple_with_field(doc):
    return (doc[DOC_ID], doc[KEY], doc[SCORE], doc[QFIELD])

#去重并按score倒排
def irdocs2tuple(docs):
    ret = set()
    key_set = set()
    logging.info("irdocs2tuple before filter:" + str(len(docs)))
    for i,d in enumerate(docs):
        if i == 0: print "=========>>  ", d
        if type(d[KEY]) == list:
            ikey = d[KEY][0]
        else:
            ikey = d[KEY]
        if ikey not in key_set:
            # if d[KEY] == "ebola-ae8951e07f77c9288331e546ab6349541d70d4fc0c32ca3db9c76c96b0c03c71":
            #     print "=========>>  FIND  d1"
            key_set.add(ikey)
            ret.add( doc2tuple(d) )

    logging.info("irdocs2tuple after filter:" + str(len(ret)))
    ret = sorted( list(ret), key= lambda d: d[-1], reverse=True )

    return ret


#针对全文类型的， 去重并按score倒排
def irdocs2tuple_full(docs):
    ret = set()
    key_set = set()
    logging.info("irdocs2tuple before filter:" + str(len(docs)))
    for i,d in enumerate(docs):
        if i == 0: print "=========>>  ", d
        if type(d[KEY]) == list:
            ikey = d[KEY][0]
        else:
            ikey = d[KEY]
        if ikey not in key_set:
            # if d[KEY] == "ebola-ae8951e07f77c9288331e546ab6349541d70d4fc0c32ca3db9c76c96b0c03c71":
            # print "=========>>  FIND  d1", ikey, d
            key_set.add(ikey)
            ret.add( doc2tuple2(d) )

    logging.info("irdocs2tuple after filter:" + str(len(ret)))
    ret = sorted( list(ret), key= lambda d: d[-1], reverse=True )

    return ret

#
def irdocs2tuple_with_field(docs):
    ret = set()
    key_set = set()
    logging.info("irdocs2tuple before filter:" + str(len(docs)))
    for i, d in enumerate(docs):
        if i == 0:
            print "=========>>  ", d
        if type(d[KEY]) == list:
            ikey = d[KEY][0]
        else:
            ikey = d[KEY]
        if ikey not in key_set:
            # if d[KEY] == "ebola-ae8951e07f77c9288331e546ab6349541d70d4fc0c32ca3db9c76c96b0c03c71":
            #     print "=========>>  FIND  d1"
            key_set.add(ikey)
            ret.add(doc2tuple_with_field(d))

    logging.info("irdocs2tuple after filter:" + str(len(ret)))
    ret = sorted(list(ret), key=lambda d: d[-1], reverse=True)

    return ret

if __name__ == '__main__':
    pass

__END__ = True