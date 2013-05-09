#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing sorl-thumbnail ...'
sorlthumbnail_git=https://github.com/Knotis/sorl-thumbnail.git@fix_cropping
${venv_bin}/pip install git+${sorlthumbnail_git}
