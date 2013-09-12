#!/bin/bash

# Make sure that prerequisites for zlib jpeg and freetype support are installed
apt-get install -y libjpeg8 libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev

ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/ 2> /dev/null
ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/ 2> /dev/null
ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/ 2> /dev/null

echo 'installing PIL ...'
${install_location}/venv/bin/pip install PIL
