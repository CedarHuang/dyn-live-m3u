#!/bin/sh
cd /app/dyn-live-m3u
update() {
    git pull
    pip install -r requirements.txt
}
update &
cp ./src/* ..
FROM="./config"
TO="/config"
for file in "$FROM"/*; do
    filename=$(basename "$file")
    if [ ! -e "$TO/$filename" ]; then
        cp "$file" "$TO"
        echo "$filename does not exist, has been generated"
    fi
done
cd /app
python app.py 3658