#! /usr/bin/env bash

printf -v CALLER "$_"

printf -v PROGRAM "${0##*/}"
printf -v DESCRIPTION "Set up the environment for $PROGRAM and run the program."
printf -v AUTHOR "Russell Klein"
printf -v VERSION "1.0"

export debug=0
export verbose=0
# export logfile=

optstring=e:dv

while getopts $optstring opt; do
  case $opt in
    e) logfile=$OPTARG ;;
    v) verbose=$(( $verbose + 1 )) ;;
    d) export debug=$(( $debug + 1 )) ;;
  esac
done

printf "Running $CALLER\n"
printf "Program: $PROGRAM\n"
printf -v TARGET ""

if [ -h $CALLER ]; then
  printf -v TARGET "`realpath $CALLER`"
else
  printf -v allbutfirst "${CALLER#?}"
  printf -v first "%s" "${CALLER%$allbutfirst}"
  printf "%s\n" "First character of caller: $first"

  if [ $first == '/' ]; then
    printf -v TARGET $CALLER
  else
    printf -v TARGET "$PWD/$CALLER"
  fi

fi

printf "Target: $TARGET\n"
printf -v BASEDIR "${TARGET%/*/*}" # "`hello/basedir.py`"
printf -v BASEDIR "`realpath $BASEDIR`"
printf "Base directory: $BASEDIR\n"
printf -v BASENAME "`basename $BASEDIR`"
printf -v PROJECT "${BASENAME%%-*}\n"
printf -v VERSION "${BASENAME##*-}\n"

virtual=0
venv=.venv
installed_just_now=1

function venv() {
  printf "Virtual environment $BASEDIR/$venv does not exist.\n"
  printf "Do you want to create it? (y/n): "
  read answer;
  case $answer in
    y)
      printf "OK, let's do that then.\n"
      python3.9 -m venv --upgrade-deps $BASEDIR/$venv
      virtual=0
      installed_just_now=0
  esac
}

if [ ! -d $BASEDIR/$venv ]; then
   virtual=1; venv a
fi
[[ $virtual ]] && source $BASEDIR/$venv/bin/activate
[[ $installed_just_now -eq 0 ]] && pip install -r $BASEDIR/requirements.txt


if [[ " $@ " =~ " -d " ]]; then
  python $BASEDIR/$PROJECT $@
else
  python -O $BASEDIR/$PROJECT $@
fi

[[ $virtual ]] && deactivate
