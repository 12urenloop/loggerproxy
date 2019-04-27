#!/usr/bin/env bash


host="localhost"
port="12345"
serverport="5000"

./testserver.sh $serverport
cd ..
python ./loggingproxy.py &
cd testing
