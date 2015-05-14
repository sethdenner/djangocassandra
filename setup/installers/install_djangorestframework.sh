#!/bin/bash

echo 'installing djangorestframework ...'
pip=${install_location}/venv/bin/pip

#$pip install djangorestframework # This might be too new.
$pip install djangorestframework==3.1.1

$pip install markdown
$pip install django-filter
$pip install defusedxml
$pip install PyYAML
$pip install django-oauth-plus
$pip install django-guardian
$pip install django-oauth-toolkit==0.8.1
