#!/bin/bash
rand=$(date | md5sum)
rand=(${rand})
temp_dir="${tmp}/${rand[0]}"

mkdir "${temp_dir}" 2> /dev/null

git clone https://github.com/sethdenner/django_cassandra_backend.git ${temp_dir}
(
    cd ${temp_dir}
    git checkout knotis
)

django_cassandra_dir="$(find ${temp_dir} -name django_cassandra)"

cp -rf ${django_cassandra_dir} ${install_location}/venv/lib/python2.7/site-packages/
rm -rf ${temp_dir}

path='./django_cassandra'
output="${install_location}/venv/lib/python2.7/site-packages/django_cassandra.pth"
echo "Writing pth file to $output"

if [ ! -f "$output" ]; then
    touch "$output"
fi
echo $path > $output
