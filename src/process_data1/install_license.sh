#! /bin/bash

echo "THE PASSWORD IS changme"
curl -XPUT -u elastic 'http://localhost:9200/_xpack/license?acknowledge=true' -H "Content-Type: application/json" -d @harry-potter-v5-licence.json

