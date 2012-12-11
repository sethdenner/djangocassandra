#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

venv_bin=/srv/knotis/venv/bin

echo 'installing djangotoolbox ...'
djangotoolbox_git_repo=https://github.com/django-nonrel/djangotoolbox.git
quick_install git $djangotoolbox_git_repo $venv_bin/python
