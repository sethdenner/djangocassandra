#!/bin/bash
pip=${install_location}/venv/bin/pip

echo 'installing MySQL-python ...'
${pip} install --upgrade distribute
${pip} install MySQL-python
