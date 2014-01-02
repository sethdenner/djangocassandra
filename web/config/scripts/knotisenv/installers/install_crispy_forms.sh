#!/bin/bash
venv_bin=/srv/knotis/venv/bin

echo 'installing crispy_forms ...'
crispy_forms_git_repo=https://github.com/maraujop/django-crispy-forms.git
${venv_bin}/pip install git+${crispy_forms_git_repo}@master
