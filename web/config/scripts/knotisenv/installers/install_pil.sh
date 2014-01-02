#!/bin/bash

# Make sure that prerequisites for zlib jpeg and freetype support are installed
apt-get install libjpeg8 libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev

ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/ 2> /dev/null
ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/ 2> /dev/null
ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/ 2> /dev/null

venv_bin=/srv/knotis/venv/bin

echo 'installing PIL ...'
$venv_bin/pip install PIL
