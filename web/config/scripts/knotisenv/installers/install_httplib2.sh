#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

venv_bin=/srv/knotis/venv/bin

echo 'installing httplib2 ...'
httplib2_tarball=http://httplib2.googlecode.com/files/httplib2-0.7.7.tar.gz
quick_install wget $httplib2_tarball $venv_bin/python
