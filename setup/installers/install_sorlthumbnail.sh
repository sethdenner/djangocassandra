#!/bin/bash
echo 'installing sorl-thumbnail ...'
sorlthumbnail_git=https://github.com/Knotis/sorl-thumbnail.git@fix_cropping
${install_location}/venv/bin/pip install git+${sorlthumbnail_git}
