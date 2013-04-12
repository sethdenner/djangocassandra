#!/bin/bash
my_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${my_dir}/../../utilities/quick_install.sh

venv_bin=/srv/knotis/venv/bin

echo 'installing django-permission-backend-nonrel ...'
perm_backend_nonrel_git=https://github.com/django-nonrel/django-permission-backend-nonrel.git
quick_install git ${perm_backend_nonrel_git} ${venv_bin}/python
