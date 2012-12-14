#!/bin/bash
rand=$(date | md5sum)
rand=(${rand})
temp_dir="./tmp-${rand[0]}"

mkdir "${temp_dir}" 2> /dev/null

git clone https://github.com/vaterlaus/django_cassandra_backend.git ${temp_dir}

django_cassandra_dir="$(find ${temp_dir} -name django_cassandra)"

cp -rf ${django_cassandra_dir} /srv/knotis/venv/lib/python2.7/site-packages/
rm -rf ${temp_dir}
