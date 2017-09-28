#! /bin/bash

for process_id in 0 1 2 3 4 5 6 7;
do python format_json2xml.py $process_id 8 &
done
