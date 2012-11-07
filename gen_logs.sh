#!/bin/bash

cd ../tools/repeater/
./repeater.sh $1 &

echo "Wow"
sleep 15
echo "GO"

cd ../../src/
python3 Runner.py > "../log/$1$2.log"

echo 'Killing'
kill `lsof -i :31000 | grep java | sed -r 's/java\s+(.*)\s+what.*/\1/'`
echo 'ok'
