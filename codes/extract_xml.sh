#! /bin/bash


datatype=$1
for file in `ls ../datas/xml`;
do nohup python extract_$datatype.py "../datas/xml/$file" > "../log/extract-$datatype-$file.log" & 
done
