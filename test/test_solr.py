# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/6 上午4:33
# @version: 1.0


from urllib2 import urlopen

url = 'http://localhost:8983/solr/collection_name/select?q=cheese&wt=python'

# url = 'http://172.22.0.17:8983/solr/ebola/select?q=cheese&wt=python'
url = "http://172.22.0.17:8983/solr/ebola/select?indent=on&q=content_h1:ebola&rows=100&wt=json&fl=*,score"

url = "http://172.22.0.17:8983/solr/ebola/select?q=ebola,news&rows=100&wt=json&fl=*,score"

connection = urlopen( url
                )
response = eval(connection.read())

print response['response']['numFound'], "documents found."

# Print the name of each document.
cnt = 0
for document in response['response']['docs']:
    print "  Name =", document['key'], document['score']
    cnt += 1

print "get_result cnt:", cnt


if __name__ == '__main__':
    pass

__END__ = True