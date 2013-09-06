#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing djangotoolbox ...'
djangotoolbox_tarball=${setup_dir}/static/djangotoolbox.tar.gz
${install_location}/venv/bin/pip install ${djangotoolbox_tarball}
