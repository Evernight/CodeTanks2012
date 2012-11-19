#!/bin/bash

cd ../tools/runner_4
/bin/bash local-runner-sync.sh

echo 'waiting...'
sleep $1
echo 'ok'

cd ../../src
python3 Runner.py
