#!/bin/bash

for i in `seq $1 $2`;
do
    args="x_fb_ge_sol $i";
    plr $args &
done;

