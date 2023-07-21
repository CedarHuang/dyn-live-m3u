#!/bin/sh
cd /app/dyn-live-m3u
git pull
pip install -r requirements.txt
cp ./src/* ..