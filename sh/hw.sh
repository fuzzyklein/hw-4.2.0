#! /usr/bin/env bash
source ~/.venv-3.9/bin/activate
export PYTHONSTARTUP=hw.startup.py
export startup=PYTHONSTARTUP
python3 -m hw $@
deactivate
