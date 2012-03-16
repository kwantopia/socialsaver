#!/bin/sh

cd packages
./download.sh
cd ..
cp settings.py.sample settings.py
cp logging.conf.sample logging.conf
ln -s packages/sorl-thumbnail/sorl
