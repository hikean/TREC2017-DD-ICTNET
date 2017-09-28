#! /bin/bash

for process_id in 0 1 2 3 4 5 6 7;
do python merger_ebola_content.py $process_id 8 &
done
