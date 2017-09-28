#! /usr/bin/python

import json
from elasticsearch import Elasticsearch


ELASTICS_HOSTS = ['http://10.61.2.168:9200/']

def format_search_response(response):
    ret = {}
    ret["took"] = response.get("took", 0)
    ret["timed_out"] = response.get("timed_out", True)
    hits = response["hits"]
    ret["result_total"] = hits.get("total", 0)
    ret["max_score"] = hits.get("max_score", 0)
    result_array = []
    for result in hits["hits"]:
        now = {"es" + key: result[key] for key in result if key != "_source" and key[0] == "_"}
        now.update({key: result["_source"][key] for key in result["_source"]})
        result_array.append(now)
    ret["results"] = result_array
    return ret

def es_search(keyword, fields, doc_type="ebola", size=10):
    es = Elasticsearch(ELASTICS_HOSTS)
    body = {
        "from": 0,
        "size": size,
        "min_score": 0,
        "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": fields
                }
        },
        "sort": [
                # {"date": {"order": "desc"}},
            {"_score": {"order": "desc"}}
        ],
        "_source": {
            "excludes": ["content", "description"]
        }
    }
    if doc_type != "ebola":
        body["_source"] = {
            "excludes": ["blocks", "head", "metas", "classifier"]
        }
    content = es.search(index="trec", doc_type=doc_type, body=body)
    return format_search_response(content)


def search_nytimes(keyword, size):
    es = Elasticsearch(ELASTICS_HOSTS)
    body = {
        "from": 0,
        "size": size,
        "min_score": 1,
        "query": {
                "multi_match": {
                    "query": keywords,
                    "fields": ["head", "title", "blocks", "classifier"]
                }
        },
        "sort": [
                # {"date": {"order": "desc"}},
            {"_score": {"order": "desc"}}
        ],
        "_source": {
            "excludes": ["blocks", "head", "metas", "classifier"]
        }
    }
    content = es.search(index="trec", doc_type="nytimes", body=body)
    return format_search_response(content)


def search_ebola(keyword, size):
    es = Elasticsearch(ELASTICS_HOSTS)
    body = {
        "from": 0,
        "size": size,
        "min_score": 1,
        "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["title", "content", "description"]
                }
        },
        "sort": [
                # {"date": {"order": "desc"}},
            {"_score": {"order": "desc"}}
        ],
        "_source": {
            "excludes": ["content", "description"]
        }
    }
    content = es.search(index="trec", doc_type="ebola", body=body)
    return format_search_response(content)


def main():
    print search_nytimes(keywords="The Other Sister  Juliette Lewis", size=3)
    print "\n" * 3
    print search_ebola(keywords="Blut-Therapie soll gegen Ebola helfen", size=3)

if __name__ == "__main__":
    main()


