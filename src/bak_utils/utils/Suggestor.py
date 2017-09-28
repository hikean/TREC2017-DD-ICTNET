# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/13 下午4:10
# @version: 1.0

from basic_init import *

from src.utils.constants import *

import json as js
import codecs

class SubQueryGenerator(object):
    def __init__(self, js_file,subquery_field_name='suggestions', query_field = 'query'):

        self.query2tid = {}
        self.tid2query = {}

        domain_topics = TOT_TOPICS

        for tid, tname in domain_topics:
            self.query2tid[tname] = tid
            self.tid2query[tid] = tname

        # print self.tid2query

        self.data = js.load(codecs.open(
            js_file, 'r'
        ))
        #key:topic_id v:list(subquerys)
        self.data_dict = {}

        for topic_id, vs in self.data.items():
            if vs is None:
                # print topic_id, vs
                print "[ERROR] vs is None, topic_id, vs:", topic_id, vs
                self.data_dict[topic_id] = []
            else:
                self.data_dict[topic_id] = vs[subquery_field_name]


    def get_subquery_by_topic_id(self, tid, if_related=False):
        return self.data_dict[tid]

    def get_subquery_by_query(self, query):
        query = query.strip()
        if self.query2tid.has_key(query):
            tid = self.query2tid[query]
        else:
            return None
        return self.get_subquery_by_topic_id(tid)

class SubQueryGenerator_V1(object):
    def __init__(self, js_file, subquery_field_name='suggestions', query_field = 'query'):

        self.query2tid = {}
        self.tid2query = {}

        domain_topics = TOT_TOPICS

        for tid, tname in domain_topics:
            self.query2tid[tname] = tid
            self.tid2query[tid] = tname

        # print self.tid2query

        self.data = js.load(codecs.open(
            js_file, 'r'
        ))
        #key:topic_id v:list(subquerys)
        self.data_dict = {}

        for topic_id, vs in self.data.items():
            if vs is None:
                # print topic_id, vs
                print "[ERROR] vs is None, topic_id, vs:", topic_id, vs
                self.data_dict[topic_id] = []
            else:
                self.data_dict[topic_id] = vs
                # print topic_id, vs


    def get_subquery_by_topic_id(self, tid, if_related=False):
        return self.data_dict[tid]

    def get_subquery_by_query(self, query):
        query = query.strip()
        if self.query2tid.has_key(query):
            tid = self.query2tid[query]
        else:
            return None
        return self.get_subquery_by_topic_id(tid)


class SubQueryGenerator_by_abstract(object):
    def __init__(self, js_file):
        self.query2tid = {}
        self.tid2query = {}
        domain_topics = TOT_TOPICS
        for tid, tname in domain_topics:
            self.query2tid[tname] = tid
            self.tid2query[tid] = tname

        self.data = js.load(codecs.open(js_file, 'r', 'utf-8'))

        self.data_dict = {}

        for topic_id, tdata in self.data.items():
            #[0]是related [1]是suggested
            self.data_dict[topic_id] = [
                tdata['suggestions'],
                tdata['results']
            ]

    def get_subquery_by_topic_id(self, tid, if_related=False):
        if if_related: return self.get_related_subquery_by_tid(tid)
        else: return self.get_suggested_subquery_by_topic_id(tid)

    def get_subquery_by_query(self, query, if_related=False):
        if if_related: return self.get_related_subquery_by_query(query)
        else: self.get_suggested_subquery_by_query(query)

    def get_suggested_subquery_by_topic_id(self, tid, field='abstract'):
        data = self.data_dict[tid][1]
        ret = []
        for r in data:
            ret.append( r[field] )

        return ret

    def get_suggested_subquery_by_query(self, tname, field='abstract'):
        # data = self.data_dict[0]
        return self.get_suggested_subquery_by_topic_id( self.query2tid[tname.strip()], field=field )

    def get_related_subquery_by_tid(self, tid):
        return self.data_dict[tid][0]

    def get_related_subquery_by_query(self, tname):
        return self.get_related_subquery_by_tid( self.query2tid[tname] )


'''
几种方式：
1、title的处理
2、如果related没有的话才用title
3、每个topic都用相同的subquery//
4、w2v 来查出近义词做扩展

'''

class SubQueryGenerator_by_title(object):
    def __init__(self, js_file):
        self.query2tid = {}
        self.tid2query = {}
        domain_topics = TOT_TOPICS
        for tid, tname in domain_topics:
            self.query2tid[tname] = tid
            self.tid2query[tid] = tname

        self.data = js.load(codecs.open(js_file, 'r', 'utf-8'))

        self.data_dict = {}

        for topic_id, tdata in self.data.items():
            #[0]是related [1]是suggested
            self.data_dict[topic_id] = [
                tdata['suggestions'],
                tdata['results']
            ]

    def get_subquery_by_topic_id(self, tid, if_related=False):
        if if_related: return self.get_related_subquery_by_tid(tid)
        else: return self.get_suggested_subquery_by_topic_id(tid)

    def get_subquery_by_query(self, query, if_related=False):
        if if_related: return self.get_related_subquery_by_query(query)
        else: self.get_suggested_subquery_by_query(query)

    def get_suggested_subquery_by_topic_id(self, tid, field='title'):
        data = self.data_dict[tid][1]
        ret = []
        for r in data:
            ret.append( r[field] )

        return ret

    def get_suggested_subquery_by_query(self, tname, field='title'):
        # data = self.data_dict[0]
        return self.get_suggested_subquery_by_topic_id( self.query2tid[tname.strip()], field=field )

    def get_related_subquery_by_tid(self, tid):
        return self.data_dict[tid][0]

    def get_related_subquery_by_query(self, tname):
        return self.get_related_subquery_by_tid( self.query2tid[tname] )


# class SubQueryGenerator(object):
#     def __init__(self, js_file,subquery_field_name='suggestions', domain='ebola', query_field = 'query'):
#
#         self.query2tid = {}
#         self.tid2query = {}
#
#         if domain == 'ebola':
#             domain_topics = EBOLA_TOPICS
#         else:
#             domain_topics = NYT_TOPICS
#
#         for tid, tname in domain_topics:
#             self.query2tid[tname] = tid
#             self.tid2query[tid] = tname
#
#         print self.tid2query
#
#         self.data = js.load(codecs.open(
#             js_file, 'r'
#         ))
#         #key:topic_id v:list(subquerys)
#         self.data_dict = {}
#
#         for topic_id, vs in self.data.items():
#             for q in vs:
#                 if not self.tid2query.has_key(topic_id):continue
#                 query = q[query_field].strip()
#                 if query == self.tid2query[topic_id]:
#                     self.data_dict[topic_id] = q[subquery_field_name]
#                     break
#             # self.data_dict[topic_id] = self.v[subquery_field_name]
#
#
#     def get_subquery_by_topic_id(self, tid):
#         return self.data_dict[tid]
#
#     def get_subquery_by_query(self, query):
#         tid = self.query2tid[query.strip()]
#         return self.data_dict[tid]


def test_1():
    # ebola_suggested = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    ebola_suggested = SubQueryGenerator(js_file=GOOGLE_SUGGESTED_V1_EBOLA)
    print "get:", ebola_suggested.get_subquery_by_query('Ebola Conspiracy Theories')


    ebola_related = SubQueryGenerator(js_file=GOOGLE_RELATED, subquery_field_name='related')
    print "related get:", ebola_related.get_subquery_by_query('Ebola Conspiracy Theories')

    # ebola_related = SubQueryGenerator(js_file=EBOLA_GOOGLE_RELATED, domain='ebola', query_field='related')
    # print ebola_related.get_subquery_by_query('Ebola Conspiracy Theories')


def test_2():
    tname = 'US Military Crisis Response'
    ebola_suggested = SubQueryGenerator_by_title(js_file=TITLE_BING)
    print "suggested:", ebola_suggested.get_suggested_subquery_by_query(tname)

    print "related:", ebola_suggested.get_related_subquery_by_query(tname)


'''
查看query跟subquery相同的情况
'''
def test_3():
    ebola_suggested = SubQueryGenerator_V1(js_file=GOOGLE_SUGGESTED_V1_EBOLA)
    print "get:", ebola_suggested.get_subquery_by_query('Ebola Conspiracy Theories')

    nyt_suggested = SubQueryGenerator_V1(js_file=GOOGLE_SUGGESTED_V1_NYT)
    print "get:", nyt_suggested.get_subquery_by_query("Abortion pill in the United States")

    # ebola_related = SubQueryGenerator_V1(js_file=GOOGLE_RELATED, subquery_field_name='related')
    # print "related get:", ebola_related.get_subquery_by_query('Ebola Conspiracy Theories')


def test_4():
    ebola_suggested = SubQueryGenerator(js_file=GOOGLE_SUGGESTED)
    print "get:", ebola_suggested.get_subquery_by_query('Ebola Conspiracy Theories')

    print "get:", ebola_suggested.get_subquery_by_topic_id('dd17-60')

if __name__ == '__main__':
    # test_1()
    # test_2()
    test_4()


__END__ = True