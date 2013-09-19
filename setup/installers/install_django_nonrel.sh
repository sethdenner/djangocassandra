#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing django-nonrel ...'
django_tarball="${setup_dir}/static/django-nonrel-1.3.tar.gz"
${install_location}/venv/bin/pip install ${django_tarball}
