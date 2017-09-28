#! /bin/bash

cd "../datas/xml"

mkdir "../data_tagz"
for year in `ls`;
do cd $year;
    for file in 01 02 03 04 05 06 07 08 09 10 11 12;
    do mv $file "../../data_tagz/$year_$file.tgz"
    done
    cd ../
done

