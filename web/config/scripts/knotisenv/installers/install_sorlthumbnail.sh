#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing sorl-thumbnail ...'
sorlthumbnail_git=https://github.com/sorl/sorl-thumbnail.git
${venv_bin}/pip install git+${sorlthumbnail_git}
