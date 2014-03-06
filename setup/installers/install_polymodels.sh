#!/bin/bash

echo 'installing polymodels ...'
polymodels_tarball="${setup_dir}/static/django-polymodels-1.3-support.tar.gz"
${install_location}/venv/bin/pip install ${polymodels_tarball}
