#! /usr/bin/env bash

virtual=0
venv=.venv

function venv() {
  printf "Virtual environment $venv does not exist.\n"
  printf "Do you want to create it? (y/n): "
  read answer;
  case $answer in
    y)
      printf "OK, let's do that then.\n"
      python3.9 -m venv --system-site-packages --symlinks --upgrade-deps $venv
      virtual=0
  esac
}

if [ ! -d ${venv} ]; then
   virtual=1; venv a
fi
[[ $virtual ]] && source $venv/bin/activate; printf "venv active\n"
export PYTHONSTARTUP=hw.startup.py
export startup=PYTHONSTARTUP
python3 -m hw $@
[[ $virtual ]] && deactivate
