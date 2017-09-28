#!/bin/bash

for i in `seq $1 $2`;
do
    args="xQuAD_multi_source_feedback_Ebola_NYT_solution $i";
    plr $args &
done;

