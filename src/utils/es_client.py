# -*- coding: utf-8 -*-
"""Elasticsearch Client"""

import json
from elasticsearch import Elasticsearch
import logging


class ElasticClient(object):
    """Elcasticsearch Client"""

    def __init__(self, doc_type="ebola", return_size=1000,
                 hosts=['http://10.61.2.168:9200/'], index="trec"):
        """Init.

        doc_type can only be "ebola" or "nytimes"
        """
        if doc_type not in {"ebola", "nytimes"}:
            raise ValueError(
                '"{}" is neither "ebola" nor "nytimes .'.format(doc_type))
        self.doc_type = doc_type
        self.return_size = return_size
        self.es = Elasticsearch(hosts)
        self.index = index

    @staticmethod
    def _format_search_response(response):
        ret = {}
        ret["took"] = response.get("took", 0)
        ret["timed_out"] = response.get("timed_out", True)
        hits = response["hits"]
        ret["result_total"] = hits.get("total", 0)
        ret["max_score"] = hits.get("max_score", 0)
        result_array = []
        for result in hits["hits"]:
            now = {"es" + key: result[key]
                   for key in result if key != "_source" and key[0] == "_"}
            now.update({key: result["_source"][key]
                        for key in result["_source"]})
            result_array.append(now)
        ret["results"] = result_array
        return ret

    @staticmethod
    def result2tuple(results, key="key"):
        return [(page["es_id"], page[key], page["es_score"])
                for page in results["results"]]

    def es_search(self, body, doc_type=None):
        if doc_type is None:
            doc_type = self.doc_type
        return self.es.search(index=self.index, doc_type=doc_type, body=body)

    def search(self, keyword, fields, doc_type=None,
               return_size=None, excludes=True):
        if doc_type is None:
            doc_type = self.doc_type
        if return_size is None:
            return_size = self.return_size
        body = {
            "from": 0,
            "size": return_size,
            "min_score": 0,
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": fields,
                    "type": "most_fields" # "cross_fields" # "best_fields" #   
                }
            },
            "sort": [
                # {"date": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ],
        }
        excludes = [{"excludes": ["content", "description"]},
                    {"excludes": ["blocks", "head", "metas", "classifier"]}]
        if excludes:
            body["_source"] = excludes[0 if doc_type == "ebola" else 1]
        return ElasticClient._format_search_response(
            self.es_search(body=body, doc_type=doc_type))

    def search_ebola(self, keyword, fields, return_size=None, excludes=True):
        """Search from ebola.

        fields can be some of ["title", "content", "description"]
        """
        return self.search(keyword=keyword, fields=fields, doc_type="ebola",
                           return_size=return_size, excludes=excludes)

    def search_nytimes(self, keyword, fields, return_size=None, excludes=True):
        """Search from NY Times.

        fields can be some of ["head", "title", "blocks", "classifier"]
        """
        return self.search(keyword=keyword, fields=fields, doc_type="nytimes",
                           return_size=return_size, excludes=excludes)


def main():
    """Entry.

    some simple examples of basic usages.
    """
    logging.root.setLevel(logging.INFO)
    client = ElasticClient(doc_type="ebola", return_size=5)
    logging.info(client.search_nytimes(
        keyword="The Other Sister  Juliette Lewis",
        fields=["head", "title", "blocks", "classifier"]))
    logging.info(client.search_ebola(
        keyword="Blut-Therapie soll gegen Ebola helfen",
        fields=["title", "content", "description"]))


if __name__ == "__main__":
    main()
