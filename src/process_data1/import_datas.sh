#! /bin/bash


scriptname="extract_ny"
if [[ -n $1 ]]; then
    scriptname=$1
fi

process_count=$2
if [[ -z $2 ]]; then
    echo "Usage: import_datas.sh script_name <process_count>"
    exit
fi

process_id=0

echo "import $scriptname data using $process_count processes..."

while [ $process_id -lt $process_count ]
do
    py_name="$scriptname.py"
    log_name="../log/$scriptname-$process_id.log"
    echo "nohup python $py_name process $process_id $process_count > $log_name &"
    nohup python $py_name process $process_id $process_count >  $log_name  &
    process_id=$[$process_id + 1]
done