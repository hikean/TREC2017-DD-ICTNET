# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/6 上午5:06
# @version: 1.0


#url = "http://172.22.0.17:8983/solr/ebola/select?q=content_h1:ebola&rows=100&wt=json&fl=*,score"

from basic_init import *

from urllib2 import urlopen
import urllib
import urlparse

from src.global_settings import *

class SolrClient(object):
    def __init__(self, solr_url="http://172.22.0.17:8983/solr/ebola_v2/select?", ret_doc_cnt=1000, wt='json', collection_name='ebola', mlt=False, full_search = False):
        self.solr_url = solr_url
        self.url_params = urlparse.urlparse(solr_url)
        self.mlt = mlt
        self.full_search = full_search

    def query_url(self, url):
        connection = urlopen(url)
        response = eval(connection.read())

        return response

    def mk_url(self, **params):
        query = dict(urlparse.parse_qsl(self.url_params.query))
        query.update(params)
        prlist = list(self.url_params)
        prlist[4] = urllib.urlencode(query)
        return urlparse.ParseResult(*prlist).geturl()


    def mk_url_dic(self, **params):
        dic=dict(**params)

        base_url = self.solr_url
        for (k,v) in dic.items():
            if k != 'q':base_url += '&'
            if k == 'q' or k == 'qf':
                v = urllib.quote(v)
            base_url += str(k) + '=' + str(v)

        if self.mlt:
            base_url += "&mlt.fl=" + "content,key,doc_id,score"

        return base_url


    def query_fields(self, keywords=[], query_fields=None,fl='*', rows=10, show_score=True, wt='json'):

        keywords = ','.join(keywords)
        if show_score: fl = fl + ',score'
        print fl
        if query_fields is None:
            #&mlt=true&mlt.fl=content&mlt.count=100
            if not self.mlt:
                url = self.mk_url_dic(q=keywords, fl=fl, wt=wt, rows=rows)
            else:
                url = self.mk_url_dic(q=keywords, fl=fl, wt=wt, rows=rows, mlt="true")
        else:
            if self.mlt:
                url = self.mk_url_dic(q=query_fields + ':' + keywords, fl=fl, wt=wt, rows=rows, mlt="true")
            else:
                url = self.mk_url_dic( q= query_fields+':'+keywords ,fl=fl, wt=wt, rows=rows)

        logging.info("query:" + str(url))
        try:
            return self.query_url(url)['response']['docs']
        except Exception, e:
            logging.error("query error:" + url + "," +str(e))
            return []


    #'''http://10.61.2.164:8983/solr/nyt_6_sep/select?_=1506439592437&defType=dismax&fl=key,date,content_full_text,title,score&indent=on&q=*:ebola&qf=title%5E5+content_full_text%5E2&wt=json'''

    def query_fields_by_weight(self, keywords=[], query_fields=None,fl='*', rows=10, show_score=True, wt='json', ws=[]):

        search_field = ','.join(query_fields)
        real_q_field = []
        for i_ in range(len(query_fields)):
            real_q_field.append(
                str(query_fields[i_]) + '^' + str(ws[i_])
            )
        real_q_field = ' '.join(real_q_field)


        keywords = ','.join(keywords)

        if show_score: fl = fl + ',score'
        url = self.mk_url_dic(q=search_field+':'+keywords, fl=fl, wt=wt, rows=rows, qf=real_q_field, defType='dismax')
        logging.info("query:" + str(url))
        try:
            return self.query_url(url)['response']['docs']
        except Exception, e:
            logging.error("query error:" + url + "," +str(e))
            return []

    def retrive_top_k_docs(self, keywords, rcnt=100, fl = 'key,doc_id', query_field="content"):
        return self.query_fields(keywords=keywords, query_fields=query_field, rows=rcnt)

if __name__ == '__main__':
    from constants import FULL_SOLR_URL
    client = SolrClient(solr_url=FULL_SOLR_URL)
    # logging.info("test",1,2,3)
    # print client.query_fields(keywords=['ebola'])
    print client.query_fields_by_weight(keywords=['ebola'], query_fields=['title', 'content', 'a'], ws=[0.3, 0.7, 0.1], fl='content,key')


#http://172.22.0.17:8983/solr/ebola_v2/select?indent=on&q=doc_id:*&wt=json&fl=key,doc_id,score

__END__ = True