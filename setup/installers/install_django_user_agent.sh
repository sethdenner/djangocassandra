#!/bin/bash
echo 'installing django-user_agent ...'
${install_location}/venv/bin/pip install pyyaml ua-parser user-agents
${install_location}/venv/bin/pip install django-user-agents
