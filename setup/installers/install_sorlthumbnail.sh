#!/bin/bash
echo 'installing sorl-thumbnail ...'
sorlthumbnail_git=https://github.com/simlay/sorl-thumbnail.git@test_django-1.7

${install_location}/venv/bin/pip install git+${sorlthumbnail_git}
