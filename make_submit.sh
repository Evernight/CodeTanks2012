#!/bin/sh
cp /home/whatever/work/tanks_ai/src/*.py cur_files/
rm cur_files/RemoteProcessClient.py
rm cur_files/Runner.py

cd cur_files
zip submit * 
mv submit.zip ..
