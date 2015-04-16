#!/bin/bash

echo 'installing djangorestframework ...'

${install_location}/venv/bin/pip install djangorestframework==2.3.13
${install_location}/venv/bin/pip install markdown
${install_location}/venv/bin/pip install django-filter
${install_location}/venv/bin/pip install defusedxml
${install_location}/venv/bin/pip install PyYAML
${install_location}/venv/bin/pip install django-oauth-plus
${install_location}/venv/bin/pip install django-guardian
${install_location}/venv/bin/pip install -U --no-deps git+https://github.com/Knotis/doac@knotis
