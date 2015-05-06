#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing django ...'

pip=${install_location}/venv/bin/pip

$pip install git+https://github.com/Knotis/djangocassandra.git
#$pip install git+https://github.com/kavdev/djangotoolbox.git@patch-1
$pip install git+https://github.com/sethdenner/djangotoolbox.git@issue-55
$pip install pycassa

$pip install --upgrade git+https://github.com/Knotis/django@custom-autofield
