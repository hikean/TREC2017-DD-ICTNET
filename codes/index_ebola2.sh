#!/bin/bash


echo "If the index existed, then delete it. "
curl -XDELETE "http://localhost:9200/trec2"


echo "creating trec index. "

curl -XPUT http://elastic:changeme@localhost:9200/trec2 -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "ebola": {
      "_all": {
        "term_vector": "yes"
      },
      "properties": {
        "title": {
          "type": "text",
          "include_in_all": "true",
          "boost": 1
        },
        "url": {
          "type": "keyword"
        },
        "key": {
          "type": "keyword"
        },
        "content": {
          "type": "text",
          "include_in_all": "true",
          "boost": 1,
          "similarity": "classic"
        },
        "metas": {
          "type": "text",
          "similarity": "classic",
          "include_in_all": "true"
        },
        "hs":{
          "type": "text",
          "similarity": "classic",
          "include_in_all": "true"
        }
      }
    }
  }
}'


