#!/bin/bash
echo 'installing crispy_forms ...'
crispy_forms_git_repo=https://github.com/maraujop/django-crispy-forms.git
${install_location}/venv/bin/pip install git+${crispy_forms_git_repo}@master
