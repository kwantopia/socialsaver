#!/bin/sh

cd packages
./download.sh
cd ..
cp settings.py.sample settings.py
cp logging.conf.sample logging.conf
cp mobilog.conf.sample mobilog.conf
