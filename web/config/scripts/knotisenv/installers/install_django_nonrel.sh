#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

venv_bin=/srv/knotis/venv/bin

echo 'installing django-nonrel ...'
django_git_repo=https://github.com/django-nonrel/django-nonrel.git
quick_install git $django_git_repo $venv_bin/python
