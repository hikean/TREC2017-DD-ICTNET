#! /bin/bash

cd "../datas/xml"


for year in `ls`;
do cd $year;
    for file in 01 02 03 04 05 06 07 08 09 10 11 12;
    do tar -zxf "$file.tgz"
    done
    cd ../
done

