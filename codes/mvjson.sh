#! /bin/bash

cd ../datas/xml

for year in `ls | grep -E '[0-9]*'`;
do mkdir "../json_data/$year"
    cd $year 
    for month in `ls`;
    do mkdir "../../json_data/$year/$month"
        cd $month
        for day in `ls`;
        do mkdir "../../../json_data/$year/$month/$day"
            cd $day
            mv  *.json  "../../../../json_data/$year/$month/$day"
            cd ../
        done
        cd ../
    done
    cd ../
done
