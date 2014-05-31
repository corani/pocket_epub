#!/bin/bash
function fetchAndCreate {
    ID=$1
    NAME=$2
    echo "Fetch $ID $NAME"
    wget -q -t5 -nd -H -p --convert-links -r -l1 -A html,jpg,jpeg,png,gif,css -e robots=off "http://127.0.0.1:1337/load/$ID.html" 2>&1 > /dev/null
    if [ -f "$ID.html" ]; then
        cat "$ID.html" | sed -e 's/<img.*src="http[^>"]*".*>//g' -e "s/<img.*src='http[^>']*'.*>//g" > sed.out; mv sed.out "$ID.html"
        pandoc -f html -t epub3 -o "../epub/$NAME.epub" "$ID.html"
    fi
    rm *
}
if [ ! -d work ]; then
    mkdir work
fi
cd work
{% for key, value in articles.iteritems() %}
fetchAndCreate "{{ key }}" "{{ value|create_file_name }}"
{% endfor %}
echo "Shutdown server"
wget -q "http://127.0.0.1/done" -O /dev/null 2>&1 > /dev/null
cd ..
rm -rf work
