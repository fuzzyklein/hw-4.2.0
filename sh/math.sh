#! /usr/bin/env bash

# old_dir=$PWD

printf "Source file: $BASH_SOURCE\n"
# printf -v dir "`dirname $BASH_SOURCE`\n"
# printf "Source file folder: $dir\n"

# OLD_IFS=$IFS
# IFS="\ "
#
if [[ -L $BASH_SOURCE ]]; then
  # tempfile=$(mktemp /tmp/hw/src_file_info.XXXXXX)
  # exec 3> "$tempfile"
  # exec 4< "$tempfile"
  src_file_info=$(file $BASH_SOURCE) # > /tmp/hw/src_file_info >&3
  # cat /tmp/src_file_path
  target=${src_file_info##* }
  printf "Link target: $target\n"
  parent=`dirname $target`
  base=`dirname $parent`
else
  printf -v base "$(dirname `dirname $BASH_SOURCE`)"
fi

printf "Base directory: $base\n"

virtual=0
venv=$base/.venv

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
[[ $virtual ]] && source $venv/bin/activate; # printf "venv active\n"

python3 -m http.server 8000 --bind 127.0.0.1 --directory $base & > $base/out/pid.txt > /dev/null
printf -v srv_pid $!
printf "Server process ID: $srv_pid\n"
printf -v message $(ncat -l 8080)
printf "Message received: $message\n"
# firefox localhost:8000/html/mathcgi.html
kill $srv_pid
# rm "$tempfile"
# IFS=$OLD_IFS
# cd $old_dir

# python3 hw/medit.py $@

[[ $virtual ]] && deactivate
