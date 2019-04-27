#!/usr/bin/env bash

host=$1
port=$2
count=0
goodmsg="STROLL,00:00:00:00:00:00,IGNORE,00:00:00:00:00:00,1"
badmsg="SOME GARBAGE"


end=$((SECONDS+1))
while [ $SECONDS -lt $end ]; do
    echo $goodmsg
    echo $badmsg
    count=$((count + 2))
    :
done
echo $count >> ./result



