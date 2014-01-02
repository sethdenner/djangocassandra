#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

venv_bin=/srv/knotis/venv/bin

echo 'installing django-autoload ...'
autoload_hg_repo=https://bitbucket.org/twanschik/django-autoload
quick_install hg ${autoload_hg_repo} ${venv_bin}/python
