#!/bin/bash

cd ../tools/runner_2
/bin/bash local-runner-sync.sh

echo 'waiting...'
sleep $1
echo 'ok'

cd ../../src
python3 Runner.py
