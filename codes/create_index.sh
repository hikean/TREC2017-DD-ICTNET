#!/bin/bash


echo "If the index existed, then delete it. "
curl -XDELETE "http://localhost:9200/trec"


echo "creating trec index. "

curl -XPUT http://elastic:changeme@localhost:9200/trec -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "nytimes": {
      "_all": {
        "term_vector": "yes",
        "store": "true"
      },
      "properties": {
        "title": {
          "type": "text",
          "include_in_all": "true",
          "boost": 2
        },
        "classifier": {
          "include_in_all": "true",
          "type": "text",
          "boost": 1.5
        },
        "metas": {
          "type": "keyword"
        },
        "doc_id": {
          "type": "keyword"
        },
        "date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
        },
        "head": {
          "type": "text",
          "include_in_all": "true",
          "boost": 1.5
        },
        "blocks": {
          "include_in_all": "true",
          "properties": {
            "lead": {
              "type": "text"
            },
            "full_text": {
              "type": "text"
            }
          }
        }
      }
    },
    
    "ebola": {
      "_all": {
        "term_vector": "yes",
        "store": "true"
      },
      "properties": {
        "title": {
          "type": "text",
          "include_in_all": "true",
          "boost": 2
        },
        "description": {
          "include_in_all": "true",
          "type": "text",
          "boost": 1.5
        },
        "url": {
          "type": "keyword"
        },
        "key": {
          "type": "keyword"
        },
        "spacetime": {
          "type": "keyword"
        },
        "content": {
          "type": "text",
          "include_in_all": "true",
          "boost": 1
        }
      }
    }
  }
}'


