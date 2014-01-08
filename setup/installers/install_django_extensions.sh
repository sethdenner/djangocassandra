#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing django_extensions ...'
django_extensions_tarball="${setup_dir}/static/django-extensions-1.3-support.tar.gz"
${install_location}/venv/bin/pip install ${django_extensions_tarball}
